"""Record an explicit human retention decision in the canonical Promotion record."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from skills._shared.scripts.artifact_io import utc_now, write_validated_json_atomic
from skills.evolution.scripts.evolution_integrity import load_valid_promotion


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evolution-root", type=Path, required=True)
    parser.add_argument("--promotion", type=Path, required=True)
    parser.add_argument("--status", choices=["retained", "retained_limited", "blocked"], required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--limitation", action="append", default=[])
    args = parser.parse_args()

    record, promotion_path = load_valid_promotion(args.evolution_root, args.promotion)
    application_status = record["application"]["status"]
    validation_status = record["post_apply_validation"]["status"]
    action = record["decision"]["action"]

    if args.status == "retained":
        if application_status != "applied" or validation_status != "passed":
            raise ValueError("retained requires an applied Candidate and passed post-apply validation")
    elif args.status == "retained_limited":
        if action not in {"apply", "apply_limited"}:
            raise ValueError("retained_limited requires an apply or apply_limited decision")
        if application_status != "applied" or validation_status not in {"passed", "limited"}:
            raise ValueError("retained_limited requires an applied Candidate and passed or limited validation")
        record["limitations"] = list(dict.fromkeys(record["limitations"] + args.limitation))
        if not record["limitations"]:
            raise ValueError("retained_limited requires explicit limitations")

    record["retention"] = {
        "status": args.status,
        "reason": args.reason,
        "reviewer": args.reviewer,
        "decided_at": utc_now(),
    }
    record["updated_at"] = utc_now()
    write_validated_json_atomic(promotion_path, record, ROOT / "schemas" / "promotion_record.schema.json")
    print(json.dumps({"status": "passed", "retention": args.status, "errors": []}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
