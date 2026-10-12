"""Reverse the exact frozen Candidate patch after explicit human instruction."""
from __future__ import annotations

import argparse
import json
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


def _write_logs(evolution_root: Path, log_dir: Path, label: str, result: subprocess.CompletedProcess[str]) -> list[str]:
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
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()

    evolution_root = args.evolution_root.resolve(strict=True)
    promotion, promotion_path = load_valid_promotion(evolution_root, args.promotion)
    if promotion["application"]["status"] not in {"applied", "failed"}:
        raise ValueError("rollback requires an applied or partially failed application state")
    candidate, _, patch_path = validate_candidate_promotion_link(evolution_root, promotion)
    repo_root = args.repo_root.resolve(strict=True)
    log_dir = promotion_path.parent / "logs"
    rollback_refs: list[str] = []

    reverse_check = _run(["git", "apply", "-R", "--check", str(patch_path)], repo_root)
    rollback_refs.extend(_write_logs(evolution_root, log_dir, "rollback-check", reverse_check))
    if reverse_check.returncode != 0:
        promotion["retention"] = {
            "status": "blocked",
            "reason": f"Rollback check failed: {reverse_check.stderr.strip()}",
            "reviewer": args.reviewer,
            "decided_at": utc_now(),
        }
        promotion["updated_at"] = utc_now()
        promotion["application"]["evidence_refs"] = list(dict.fromkeys(promotion["application"].get("evidence_refs", []) + rollback_refs))
        _save(promotion_path, promotion)
        print(json.dumps({"status": "failed", "reason": promotion["retention"]["reason"]}, ensure_ascii=False))
        return 1

    reversed_run = _run(["git", "apply", "-R", str(patch_path)], repo_root)
    rollback_refs.extend(_write_logs(evolution_root, log_dir, "rollback", reversed_run))
    restored = _file_hashes(candidate, repo_root)
    expected = {item["path"]: item["base_sha256"] for item in candidate["target_changes"]}
    mismatches = [item["path"] for item in restored if item["sha256"] != expected[item["path"]]]
    if reversed_run.returncode != 0 or mismatches:
        promotion["retention"] = {
            "status": "blocked",
            "reason": f"Rollback failed or base hashes were not restored. stderr={reversed_run.stderr.strip()} mismatches={mismatches}",
            "reviewer": args.reviewer,
            "decided_at": utc_now(),
        }
        promotion["updated_at"] = utc_now()
        promotion["application"]["evidence_refs"] = list(dict.fromkeys(promotion["application"].get("evidence_refs", []) + rollback_refs))
        _save(promotion_path, promotion)
        print(json.dumps({"status": "failed", "reason": promotion["retention"]["reason"]}, ensure_ascii=False))
        return 1

    now = utc_now()
    promotion["application"].update({
        "status": "rolled_back",
        "post_hashes": restored,
        "evidence_refs": list(dict.fromkeys(promotion["application"].get("evidence_refs", []) + rollback_refs)),
        "summary": "The exact frozen Candidate patch was reversed and declared base hashes were restored.",
    })
    promotion["retention"] = {
        "status": "rolled_back",
        "reason": args.reason,
        "reviewer": args.reviewer,
        "decided_at": now,
    }
    promotion["rollback"] = {
        "reviewer": args.reviewer,
        "reason": args.reason,
        "rolled_back_at": now,
        "evidence_refs": rollback_refs,
    }
    promotion["updated_at"] = now
    _save(promotion_path, promotion)
    print(json.dumps({"status": "passed", "retention": "rolled_back", "errors": []}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
