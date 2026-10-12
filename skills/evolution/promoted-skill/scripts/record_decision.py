"""Create one canonical human decision record without modifying target files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from skills._shared.scripts.artifact_io import utc_now, write_validated_json_atomic
from skills.evolution.scripts.evolution_integrity import load_valid_candidate, relative_inside


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evolution-root", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--action", choices=["apply", "apply_limited", "revise", "reject", "defer"], required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--limitation", action="append", default=[])
    parser.add_argument("--promotion-id")
    args = parser.parse_args()

    candidate, candidate_path, _ = load_valid_candidate(args.evolution_root, args.candidate)
    if args.action in {"apply", "apply_limited"} and candidate["status"] not in {"frozen", "validated"}:
        raise ValueError("application requires a structurally frozen Candidate")
    if args.action == "apply_limited" and not args.limitation:
        raise ValueError("apply_limited requires at least one explicit limitation")

    evo_root = args.evolution_root.resolve(strict=True)
    candidate_ref = relative_inside(evo_root, candidate_path)
    promotion_id = args.promotion_id or f"PROM-{candidate['candidate_id']}"
    record_path = args.evolution_root / "decisions" / promotion_id / "promotion_record.json"
    if record_path.exists():
        raise FileExistsError(f"Promotion record already exists: {record_path}")

    action_is_apply = args.action in {"apply", "apply_limited"}
    now = utc_now()
    record = {
        "schema_version": "2.1",
        "promotion_id": promotion_id,
        "candidate_id": candidate["candidate_id"],
        "candidate_ref": candidate_ref,
        "decision": {
            "action": args.action,
            "reviewer": args.reviewer,
            "reason": args.reason,
            "decided_at": now,
        },
        "application": {
            "status": "authorized" if action_is_apply else "not_requested",
            "target_ref": None,
            "pre_hashes": [],
            "post_hashes": [],
            "evidence_refs": [],
            "summary": "Application is explicitly authorized but not yet executed." if action_is_apply else "No target modification is authorized by this decision.",
        },
        "post_apply_validation": {
            "status": "not_run",
            "summary": "Post-apply validation has not run.",
            "evidence_refs": [],
        },
        "retention": {
            "status": "pending" if action_is_apply else "not_applicable",
            "reason": "Retention requires a separate explicit decision." if action_is_apply else "This decision does not apply the Candidate.",
        },
        "limitations": args.limitation,
        "created_at": now,
        "updated_at": now,
    }
    write_validated_json_atomic(record_path, record, ROOT / "schemas" / "promotion_record.schema.json")
    print(json.dumps({"status": "passed", "artifact": record_path.as_posix(), "errors": []}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
