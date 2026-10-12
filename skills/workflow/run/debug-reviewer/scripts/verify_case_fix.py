"""Verify that a persisted repair description contains decisive before/after evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    record = json.loads(args.record.read_text(encoding="utf-8"))
    reasons: list[str] = []
    for key in [
        "first_deterministic_error",
        "root_cause",
        "repair_scope",
        "earliest_affected_stage",
        "verification_command",
        "verification_return_code",
    ]:
        if record.get(key) in {None, ""}:
            reasons.append(f"missing {key}")
    if record.get("verification_return_code") != 0:
        reasons.append("verification command did not pass")
    if record.get("earliest_affected_stage") in {"plan", "write"}:
        before_hash = record.get("before_hash")
        after_hash = record.get("after_hash")
        if not before_hash:
            reasons.append("missing before_hash")
        if not after_hash:
            reasons.append("missing after_hash")
        if before_hash and after_hash and before_hash == after_hash:
            reasons.append("formal repair does not show a changed before/after state")
        if before_hash and after_hash and before_hash != after_hash and not record.get("diff_ref"):
            reasons.append("formal file change requires diff_ref or equivalent auditable change evidence")
    result = {"verified": not reasons, "status": "passed" if not reasons else "failed", "reasons": reasons}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not reasons else 1


if __name__ == "__main__":
    raise SystemExit(main())
