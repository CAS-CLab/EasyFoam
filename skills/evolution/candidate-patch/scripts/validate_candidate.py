"""Structurally validate and freeze an EasyFoam Candidate in place."""
from __future__ import annotations

import argparse
import json
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from skills._shared.scripts.artifact_io import read_json, utc_now, write_validated_json_atomic
from skills._shared.scripts.hashing import sha256_canonical_text_file, sha256_file
from skills._shared.scripts.schema_validate import validate
from skills.evolution.scripts.evolution_integrity import load_valid_candidate, resolve_inside, validate_target_ref


def _hash(path: Path) -> str | None:
    return sha256_canonical_text_file(path) if path.is_file() else None


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def _target_kind(path: str) -> str:
    value = Path(path)
    if value.name == "SKILL.md" or path == "skills/ROUTING.md":
        return "skill"
    if path.startswith("skills/reference/") or "/references/" in path:
        return "reference"
    if value.suffix == ".py":
        return "script"
    if path.startswith("schemas/") or value.name.endswith(".schema.json"):
        return "schema"
    raise ValueError(f"unsupported Candidate target kind: {path}")


def _validate_skill_frontmatter(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return [f"{path}: missing Skill front matter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return [f"{path}: unterminated Skill front matter"]
    header = "\n".join(lines[1:end])
    errors = []
    if not re.search(r"^name:\s*\S+", header, re.M):
        errors.append(f"{path}: front matter is missing name")
    if not re.search(r"^description:\s*\S+", header, re.M):
        errors.append(f"{path}: front matter is missing description")
    return errors


def _referenced_paths(path: Path, root: Path) -> list[Path]:
    text = path.read_text(encoding="utf-8")
    values = re.findall(r"`((?:skills|schemas)/[^`]+|(?:references|scripts)/[^`]+)`", text)
    result = []
    for value in values:
        if any(token in value for token in ("*", "<", ">")):
            continue
        candidate = root / value if value.startswith(("skills/", "schemas/")) else path.parent / value
        result.append(candidate)
    return result


def _post_apply_compatibility(candidate: dict[str, Any], test_root: Path) -> list[str]:
    errors: list[str] = []
    for change in candidate["target_changes"]:
        path = test_root / change["path"]
        if change["change_type"] == "delete":
            if path.exists():
                errors.append(f"deleted target still exists: {change['path']}")
            continue
        if not path.is_file():
            errors.append(f"applied target is missing: {change['path']}")
            continue
        if change["target_kind"] == "script":
            try:
                py_compile.compile(str(path), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"Python compile failed for {change['path']}: {exc.msg}")
        elif change["target_kind"] == "schema":
            try:
                schema = json.loads(path.read_text(encoding="utf-8"))
                jsonschema.Draft202012Validator.check_schema(schema)
            except (json.JSONDecodeError, jsonschema.SchemaError) as exc:
                errors.append(f"Schema compatibility failed for {change['path']}: {exc}")
        elif change["target_kind"] == "skill":
            errors.extend(_validate_skill_frontmatter(path))
        if change["target_kind"] in {"skill", "reference"}:
            for ref in _referenced_paths(path, test_root):
                if not ref.exists():
                    errors.append(f"referenced path does not exist after apply: {ref.relative_to(test_root)}")
    return errors


def _experience_errors(candidate: dict[str, Any], evolution_root: Path) -> list[str]:
    errors: list[str] = []
    responsible: set[str] = set()
    for ref in candidate["source_experience_refs"]:
        path = resolve_inside(evolution_root, ref)
        schema_errors = validate(path, ROOT / "schemas" / "experience_record.schema.json")
        if schema_errors:
            errors.extend(f"{ref}: {item}" for item in schema_errors)
            continue
        experience = read_json(path)
        if not experience["candidate_eligible"]:
            errors.append(f"source Experience is no longer Candidate-eligible: {ref}")
        responsible.add(experience["responsible_skill"])
    if len(responsible) != 1:
        errors.append(f"source Experiences do not identify one responsible Skill: {sorted(responsible)}")
    elif responsible:
        skill_parent = Path(next(iter(responsible))).parent.as_posix() + "/"
        if not any(change["path"].startswith(skill_parent) or change["path"] == next(iter(responsible)) for change in candidate["target_changes"]):
            errors.append("Candidate targets are outside the responsible Skill subtree")
    return errors


def _validation_contract_errors(candidate: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return hard contract errors and pending behavioral validation items.

    Structural validation is the first lifecycle phase.  A newly built
    Candidate is expected to have no behavioral results yet; that is a frozen
    Candidate, not an invalid one.  Malformed, duplicate, or disabled-plan
    results remain hard structural errors.
    """
    plan = candidate["validation"]["plan"]
    results = candidate["validation"]["results"]
    mapping = {
        "structural": "structural",
        "source_replay": "source",
        "holdout": "holdout",
        "negative_controls": "negative",
        "compatibility": "compatibility",
        "cross_scope": "cross_scope",
    }
    errors: list[str] = []
    pending: list[str] = []
    by_kind: dict[str, int] = {}
    for result in results:
        kind = result["kind"]
        by_kind[kind] = by_kind.get(kind, 0) + 1
        if kind not in mapping.values():
            errors.append(f"unknown validation result kind: {kind}")
        if result["status"] in {"passed", "failed", "limited"} and not result["evidence_refs"]:
            errors.append(f"validation result {kind} requires evidence_refs for status {result['status']}")
    for kind, count in by_kind.items():
        if count > 1:
            errors.append(f"validation result kind {kind} must occur exactly once")
    for plan_key, result_kind in mapping.items():
        enabled = bool(plan[plan_key])
        present = by_kind.get(result_kind, 0)
        # This command is the producer of the structural result itself.
        if enabled and present != 1 and result_kind != "structural":
            if result_kind != "structural":
                pending.append(plan_key)
        if not enabled and present:
            errors.append(f"disabled validation plan {plan_key} must not have a {result_kind} result")
    if candidate.get("candidate_type") == "documentation_only":
        if candidate.get("touched_runtime_surface"):
            errors.append("documentation_only Candidate cannot touch runtime surface")
        if any(change["target_kind"] not in {"skill", "reference"} for change in candidate["target_changes"]):
            errors.append("documentation_only Candidate may only target skill/reference files")
    if candidate.get("candidate_type") == "behavioral":
        touched = set(candidate.get("touched_runtime_surface", []))
        targets = {change["path"] for change in candidate["target_changes"]}
        if not touched:
            errors.append("behavioral Candidate must declare a touched runtime surface")
        elif not touched <= targets:
            errors.append("behavioral Candidate touched_runtime_surface must be a subset of target_changes")
    return errors, pending


def _structural_check(
    candidate: dict[str, Any],
    patch_path: Path,
    base_root: Path,
    evolution_root: Path,
) -> tuple[bool, str]:
    errors = _experience_errors(candidate, evolution_root)
    contract_errors, pending = _validation_contract_errors(candidate)
    errors.extend(contract_errors)
    declared_paths = {change["path"] for change in candidate["target_changes"]}
    if candidate["primary_target"] not in declared_paths:
        errors.append("primary_target is not in target_changes")
    for change in candidate["target_changes"]:
        try:
            validate_target_ref(change["path"])
        except ValueError as exc:
            errors.append(str(exc))
        try:
            actual_kind = _target_kind(change["path"])
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if actual_kind != change["target_kind"]:
                errors.append(f"target_kind mismatch for {change['path']}: expected {actual_kind}")
    if errors:
        return False, "; ".join(errors)

    if sha256_file(patch_path) != candidate["patch_sha256"]:
        return False, "candidate patch hash mismatch"
    for change in candidate["target_changes"]:
        actual = _hash(base_root / change["path"])
        if actual != change["base_sha256"]:
            return False, f"base hash mismatch for {change['path']}"

    with tempfile.TemporaryDirectory(prefix="easyfoam-candidate-validate-") as tmp:
        test_root = Path(tmp) / "root"
        shutil.copytree(base_root, test_root, dirs_exist_ok=True)
        check = _run(["git", "apply", "--check", str(patch_path)], test_root)
        if check.returncode != 0:
            return False, f"forward apply check failed: {check.stderr.strip()}"
        applied = _run(["git", "apply", str(patch_path)], test_root)
        if applied.returncode != 0:
            return False, f"forward apply failed: {applied.stderr.strip()}"
        for change in candidate["target_changes"]:
            actual = _hash(test_root / change["path"])
            if actual != change["proposed_sha256"]:
                return False, f"proposed hash mismatch for {change['path']}"
        compatibility_errors = _post_apply_compatibility(candidate, test_root)
        if compatibility_errors:
            return False, "; ".join(compatibility_errors)
        reverse_check = _run(["git", "apply", "-R", "--check", str(patch_path)], test_root)
        if reverse_check.returncode != 0:
            return False, f"reverse apply check failed: {reverse_check.stderr.strip()}"
        reversed_run = _run(["git", "apply", "-R", str(patch_path)], test_root)
        if reversed_run.returncode != 0:
            return False, f"reverse apply failed: {reversed_run.stderr.strip()}"
        for change in candidate["target_changes"]:
            actual = _hash(test_root / change["path"])
            if actual != change["base_sha256"]:
                return False, f"base hash was not restored for {change['path']}"

    summary = "Experience eligibility, target policy, patch/hash, post-apply compatibility, and reverse restore passed"
    if pending:
        summary += f"; pending behavioral validation: {', '.join(pending)}"
    return True, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evolution-root", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--base-root", type=Path, required=True)
    args = parser.parse_args()

    candidate, candidate_path, patch_path = load_valid_candidate(args.evolution_root, args.candidate)
    passed, summary = _structural_check(candidate, patch_path, args.base_root.resolve(strict=True), args.evolution_root.resolve(strict=True))
    result = {
        "kind": "structural",
        "status": "passed" if passed else "failed",
        "summary": summary,
        "evidence_refs": [candidate["patch_ref"]],
        "recorded_at": utc_now(),
    }
    candidate["validation"]["results"] = [
        item for item in candidate["validation"]["results"] if item["kind"] != "structural"
    ] + [result]
    candidate["status"] = "frozen" if passed else "invalid"
    candidate["updated_at"] = utc_now()
    write_validated_json_atomic(candidate_path, candidate, ROOT / "schemas" / "candidate_patch.schema.json")
    print(json.dumps({"status": "passed" if passed else "failed", "summary": summary, "errors": []}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
