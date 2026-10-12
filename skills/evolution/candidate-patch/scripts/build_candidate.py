"""Build one canonical Candidate record and a real atomic unified diff.

The script compares explicitly declared target paths in isolated base and edited
roots. It does not invent Candidate text or create selection/cluster manifests.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from skills._shared.scripts.artifact_io import read_json, utc_now, write_json_atomic
from skills._shared.scripts.hashing import sha256_canonical_text_file, sha256_file
from skills._shared.scripts.schema_validate import validate
from experience_compatibility import inspect_rows

ALLOWED_PREFIXES = ("skills/", "schemas/")
FORBIDDEN_PARTS = {".git", "archive", "experiences", "candidates", "decisions"}


def _read_metadata(value: str) -> dict[str, Any]:
    if value == "-":
        return json.load(sys.stdin)
    return json.loads(Path(value).read_text(encoding="utf-8"))


def _clean_rel(value: str) -> str:
    normalized = value.replace("\\", "/")
    path = Path(normalized)
    if path.is_absolute() or ".." in path.parts or not normalized.startswith(ALLOWED_PREFIXES):
        raise ValueError(f"invalid Candidate target path: {value}")
    if any(part in FORBIDDEN_PARTS for part in path.parts):
        raise ValueError(f"forbidden Candidate target path: {value}")
    return path.as_posix()


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def _generate_patch(base_root: Path, edited_root: Path, targets: list[str]) -> str:
    with tempfile.TemporaryDirectory(prefix="easyfoam-candidate-") as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        _run(["git", "init", "-q"], repo)
        _run(["git", "config", "user.email", "easyfoam@example.invalid"], repo)
        _run(["git", "config", "user.name", "EasyFoam Candidate Builder"], repo)

        for rel in targets:
            source = base_root / rel
            destination = repo / rel
            if source.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        add = _run(["git", "add", "-A"], repo)
        if add.returncode != 0:
            raise RuntimeError(add.stderr)
        commit = _run(["git", "commit", "-qm", "candidate baseline", "--allow-empty"], repo)
        if commit.returncode != 0:
            raise RuntimeError(commit.stderr)

        for rel in targets:
            source = edited_root / rel
            destination = repo / rel
            if source.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            elif destination.exists():
                destination.unlink()
        _run(["git", "add", "-N", "--", *targets], repo)
        diff = _run(["git", "diff", "--binary", "--", *targets], repo)
        if diff.returncode != 0:
            raise RuntimeError(diff.stderr)
        if not diff.stdout.strip():
            raise ValueError("declared targets contain no changes")
        return diff.stdout


def _kind(path: str) -> str:
    p = Path(path)
    if p.name == "SKILL.md" or path == "skills/ROUTING.md":
        return "skill"
    if path.startswith("skills/reference/") or "/references/" in path:
        return "reference"
    if p.suffix == ".py":
        return "script"
    if path.startswith("schemas/") or p.name.endswith(".schema.json"):
        return "schema"
    raise ValueError(f"unsupported formal Candidate target: {path}")


def _hash(path: Path) -> str | None:
    return sha256_canonical_text_file(path) if path.is_file() else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evolution-root", type=Path, required=True)
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--edited-root", type=Path, required=True)
    parser.add_argument("--target", action="append", required=True)
    parser.add_argument("--experience", type=Path, action="append", required=True)
    parser.add_argument("--metadata", required=True, help="JSON path or '-' for stdin")
    args = parser.parse_args()

    metadata = _read_metadata(args.metadata)
    candidate_id = metadata.get("candidate_id")
    if not candidate_id:
        raise ValueError("metadata.candidate_id is required")
    candidate_type = metadata.get("candidate_type", "behavioral")
    if candidate_type not in {"behavioral", "documentation_only", "diagnostic"}:
        raise ValueError("metadata.candidate_type must be behavioral, documentation_only, or diagnostic")
    targets = list(dict.fromkeys(_clean_rel(value) for value in args.target))

    experiences: list[dict[str, Any]] = []
    experience_refs: list[str] = []
    evo_root = args.evolution_root.resolve()
    for path in args.experience:
        schema_errors = validate(path, ROOT / "schemas" / "experience_record.schema.json")
        if schema_errors:
            raise ValueError(f"invalid Experience {path}: {schema_errors}")
        exp = read_json(path)
        if not exp["candidate_eligible"]:
            raise ValueError(f"Experience is not Candidate-eligible: {path}")
        experiences.append(exp)
        experience_refs.append(path.resolve().relative_to(evo_root).as_posix())

    compatibility = inspect_rows(experiences)
    if compatibility["status"] != "compatible":
        raise ValueError(
            f"Experience compatibility is {compatibility['status']}: "
            f"errors={compatibility['errors']} review={compatibility['review_reasons']}"
        )
    responsible = set(compatibility["responsible_skills"])
    declared_applicability = set(metadata["applicability"])
    shared_applicability = set(compatibility["shared_applicability"])
    if not declared_applicability <= shared_applicability:
        raise ValueError("metadata.applicability must be a subset of shared Experience applicability")
    declared_exclusions = set(metadata.get("exclusions", []))
    if declared_applicability & declared_exclusions:
        raise ValueError("Candidate applicability and exclusions overlap")

    primary_target = _clean_rel(metadata.get("primary_target", next(iter(responsible))))
    if primary_target not in targets:
        raise ValueError("primary_target must be one of the declared target paths")
    touched_runtime_surface = list(dict.fromkeys(metadata.get("touched_runtime_surface", [])))
    if candidate_type == "documentation_only" and touched_runtime_surface:
        raise ValueError("documentation_only Candidate cannot declare a touched runtime surface")
    if candidate_type == "documentation_only" and any(_kind(path) not in {"skill", "reference"} for path in targets):
        raise ValueError("documentation_only Candidate may only modify Skill/reference text")

    candidate_dir = args.evolution_root / "candidates" / candidate_id
    if candidate_dir.exists():
        raise FileExistsError(f"Candidate already exists: {candidate_dir}")
    candidate_dir.mkdir(parents=True)

    patch_text = _generate_patch(args.base_root, args.edited_root, targets)
    patch_path = candidate_dir / "candidate.patch"
    # Persist the patch as canonical UTF-8/LF bytes so its SHA-256 is
    # identical on Windows and POSIX hosts. Path.write_text() performs
    # platform newline translation on Windows.
    patch_path.write_bytes(patch_text.encode("utf-8"))

    changes: list[dict[str, Any]] = []
    for rel in targets:
        before = _hash(args.base_root / rel)
        after = _hash(args.edited_root / rel)
        change_type = "add" if before is None else "delete" if after is None else "modify"
        changes.append({
            "path": rel,
            "target_kind": _kind(rel),
            "change_type": change_type,
            "base_sha256": before,
            "proposed_sha256": after,
        })

    now = utc_now()
    count = len(experiences)
    validation_plan = metadata.get("validation_plan") or {
        "structural": True,
        "source_replay": True,
        "holdout": True,
        "negative_controls": True,
        "compatibility": True,
        "cross_scope": False,
    }
    if not isinstance(validation_plan, dict):
        raise ValueError("metadata.validation_plan must be an object")
    required_plan_keys = {
        "structural", "source_replay", "holdout", "negative_controls",
        "compatibility", "cross_scope",
    }
    if set(validation_plan) != required_plan_keys or validation_plan.get("structural") is not True:
        raise ValueError("metadata.validation_plan must contain exactly the canonical plan keys with structural=true")

    record = {
        "schema_version": "2.1",
        "candidate_id": candidate_id,
        "candidate_type": candidate_type,
        "touched_runtime_surface": touched_runtime_surface,
        "status": "draft",
        "source_experience_refs": experience_refs,
        "primary_target": primary_target,
        "target_changes": changes,
        "problem_pattern": metadata["problem_pattern"],
        "behavior_before": metadata["behavior_before"],
        "behavior_after": metadata["behavior_after"],
        "scope": {
            "applicability": metadata["applicability"],
            "exclusions": metadata.get("exclusions", []),
        },
        "patch_ref": patch_path.resolve().relative_to(evo_root).as_posix(),
        "patch_sha256": sha256_file(patch_path),
        "validation": {
            "plan": validation_plan,
            "results": [],
        },
        "evidence_level": "E2_REPEATED_SOURCE" if count >= 2 else "E1_VERIFIED_SOURCE",
        "risks": metadata["risks"],
        "rollback": {"method": "reverse_same_patch"},
        "created_at": now,
        "updated_at": now,
    }
    record_path = candidate_dir / "candidate_patch.json"
    write_json_atomic(record_path, record)
    errors = validate(record_path, ROOT / "schemas" / "candidate_patch.schema.json")
    if errors:
        shutil.rmtree(candidate_dir)
    print(json.dumps({"status": "passed" if not errors else "failed", "candidate": record_path.as_posix(), "errors": errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
