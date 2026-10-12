"""Apply an explicitly authorized frozen Candidate and record post-apply validation evidence."""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from skills._shared.scripts.artifact_io import utc_now, write_validated_json_atomic
from skills._shared.scripts.hashing import sha256_canonical_text_file
from skills.evolution.scripts.evolution_integrity import (
    load_valid_promotion,
    relative_inside,
    validate_candidate_promotion_link,
)


def _target_path(root: Path, relative: str) -> Path:
    resolved_root = root.resolve(strict=True)
    path = (resolved_root / relative).resolve(strict=False)
    if not path.is_relative_to(resolved_root):
        raise ValueError(f"Candidate target escapes repository root: {relative}")
    return path


def _hash(path: Path) -> str | None:
    return sha256_canonical_text_file(path) if path.is_file() else None


def _file_hashes(candidate: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    return [{"path": change["path"], "sha256": _hash(_target_path(root, change["path"]))} for change in candidate["target_changes"]]


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def _strip_outer_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _split_legacy_command(command_text: str, *, platform: str | None = None) -> list[str]:
    """Parse the legacy string form without corrupting Windows paths.

    JSON argv is the authoritative interface. This parser remains for backward
    compatibility with legacy command-string callers.
    """
    active_platform = platform or os.name
    command = shlex.split(command_text, posix=active_platform != "nt")
    if active_platform == "nt":
        command = [_strip_outer_quotes(item) for item in command]
    return command


def _parse_argv_json(value: str) -> list[str]:
    try:
        command = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid validation argv JSON value: {exc}") from exc
    if not isinstance(command, list) or not command:
        raise ValueError("validation argv JSON must be a non-empty JSON string array")
    if not all(isinstance(item, str) and item for item in command):
        raise ValueError("validation argv JSON entries must be non-empty strings")
    return command


def _safe_label(index: int, command: list[str]) -> str:
    base = Path(command[0]).name if command else "command"
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip("-") or "command"
    return f"{index:02d}-{base}"


def _write_logs(
    evolution_root: Path,
    log_dir: Path,
    label: str,
    result: subprocess.CompletedProcess[str],
) -> list[str]:
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = log_dir / f"{label}.stdout.log"
    stderr_path = log_dir / f"{label}.stderr.log"
    stdout_path.write_text(result.stdout or "", encoding="utf-8")
    stderr_path.write_text(result.stderr or "", encoding="utf-8")
    return [relative_inside(evolution_root, stdout_path), relative_inside(evolution_root, stderr_path)]


def _save(path: Path, promotion: dict[str, Any]) -> None:
    write_validated_json_atomic(path, promotion, ROOT / "schemas" / "promotion_record.schema.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evolution-root", type=Path, required=True)
    parser.add_argument("--promotion", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--target-ref", default="active-library")
    parser.add_argument(
        "--validation-argv-json",
        dest="validation_argv_json",
        action="append",
        default=[],
        help='Post-apply validation command as a JSON argv array; may be repeated.',
    )
    parser.add_argument(
        "--validation-command",
        dest="validation_command",
        action="append",
        default=[],
        help="Post-apply validation command string; JSON argv arrays are preferred.",
    )
    parser.add_argument("--test-argv-json", dest="validation_argv_json", action="append", help=argparse.SUPPRESS)
    parser.add_argument("--test", dest="validation_command", action="append", help=argparse.SUPPRESS)
    args = parser.parse_args()

    evolution_root = args.evolution_root.resolve(strict=True)
    promotion, promotion_path = load_valid_promotion(evolution_root, args.promotion)
    if promotion["decision"]["action"] not in {"apply", "apply_limited"}:
        raise ValueError("Promotion decision does not authorize application")
    if promotion["application"]["status"] != "authorized":
        raise ValueError("application is not in authorized state")

    candidate, _, patch_path = validate_candidate_promotion_link(evolution_root, promotion)
    if candidate["status"] not in {"frozen", "validated"}:
        raise ValueError("Candidate is not structurally frozen")

    repo_root = args.repo_root.resolve(strict=True)
    decision_dir = promotion_path.parent
    log_dir = decision_dir / "logs"
    evidence_refs: list[str] = []
    pre_hashes = _file_hashes(candidate, repo_root)
    expected_base = {item["path"]: item["base_sha256"] for item in candidate["target_changes"]}
    mismatches = [item["path"] for item in pre_hashes if item["sha256"] != expected_base[item["path"]]]
    if mismatches:
        promotion["application"].update({
            "status": "failed",
            "target_ref": args.target_ref,
            "pre_hashes": pre_hashes,
            "summary": f"Current target hashes do not match the frozen Candidate base: {mismatches}",
        })
        promotion["retention"] = {"status": "blocked", "reason": "Application was not attempted because the target base changed."}
        promotion["updated_at"] = utc_now()
        _save(promotion_path, promotion)
        print(json.dumps({"status": "failed", "reason": promotion["application"]["summary"]}, ensure_ascii=False))
        return 1

    check = _run(["git", "apply", "--check", str(patch_path)], repo_root)
    evidence_refs.extend(_write_logs(evolution_root, log_dir, "apply-check", check))
    if check.returncode != 0:
        promotion["application"].update({
            "status": "failed",
            "target_ref": args.target_ref,
            "pre_hashes": pre_hashes,
            "evidence_refs": evidence_refs,
            "summary": f"git apply --check failed: {check.stderr.strip()}",
        })
        promotion["retention"] = {"status": "blocked", "reason": "Candidate could not be applied to the declared target."}
        promotion["updated_at"] = utc_now()
        _save(promotion_path, promotion)
        print(json.dumps({"status": "failed", "reason": promotion["application"]["summary"]}, ensure_ascii=False))
        return 1

    applied = _run(["git", "apply", str(patch_path)], repo_root)
    evidence_refs.extend(_write_logs(evolution_root, log_dir, "apply", applied))
    post_hashes = _file_hashes(candidate, repo_root)
    expected_post = {item["path"]: item["proposed_sha256"] for item in candidate["target_changes"]}
    post_mismatches = [item["path"] for item in post_hashes if item["sha256"] != expected_post[item["path"]]]
    if applied.returncode != 0 or post_mismatches:
        promotion["application"].update({
            "status": "failed",
            "target_ref": args.target_ref,
            "pre_hashes": pre_hashes,
            "post_hashes": post_hashes,
            "evidence_refs": evidence_refs,
            "summary": f"Application failed or proposed hashes did not match. stderr={applied.stderr.strip()} mismatches={post_mismatches}",
        })
        promotion["retention"] = {"status": "blocked", "reason": "Application did not produce the frozen Candidate target state."}
        promotion["updated_at"] = utc_now()
        _save(promotion_path, promotion)
        print(json.dumps({"status": "failed", "reason": promotion["application"]["summary"]}, ensure_ascii=False))
        return 1

    declared_commands = [_parse_argv_json(value) for value in args.validation_argv_json]
    declared_commands.extend(_split_legacy_command(value) for value in args.validation_command)

    validation_results: list[dict[str, Any]] = []
    for index, command in enumerate(declared_commands, start=1):
        if not command:
            continue
        result = _run(command, repo_root)
        refs = _write_logs(evolution_root, log_dir, _safe_label(index, command), result)
        evidence_refs.extend(refs)
        validation_results.append({"command": command, "returncode": result.returncode, "stdout_ref": refs[0], "stderr_ref": refs[1]})

    validation_passed = bool(validation_results) and all(item["returncode"] == 0 for item in validation_results)
    validation_status = "passed" if validation_passed else "failed" if validation_results else "not_run"
    validation_summary = (
        "All declared post-apply commands passed."
        if validation_status == "passed"
        else "One or more declared post-apply commands failed."
        if validation_status == "failed"
        else "Candidate was applied, but no post-apply command was declared."
    )

    promotion["application"].update({
        "status": "applied",
        "target_ref": args.target_ref,
        "pre_hashes": pre_hashes,
        "post_hashes": post_hashes,
        "evidence_refs": list(dict.fromkeys(evidence_refs)),
        "summary": "The exact frozen Candidate patch was applied and proposed target hashes matched.",
        "applied_at": utc_now(),
    })
    promotion["post_apply_validation"] = {
        "status": validation_status,
        "summary": validation_summary,
        "evidence_refs": [ref for item in validation_results for ref in (item["stdout_ref"], item["stderr_ref"])],
    }
    if validation_status == "failed":
        promotion["retention"] = {"status": "blocked", "reason": "Post-apply validation failed; explicit rollback or revision is required."}
    promotion["updated_at"] = utc_now()
    _save(promotion_path, promotion)
    status = "passed" if validation_status != "failed" else "failed"
    print(json.dumps({"status": status, "application": "applied", "validation": validation_status, "errors": []}, ensure_ascii=False))
    return 0 if validation_status != "failed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
