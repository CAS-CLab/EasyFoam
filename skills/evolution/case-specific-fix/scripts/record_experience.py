"""Write one canonical EasyFoam Experience record from a descriptor.

The descriptor may be read from a UTF-8 JSON file or stdin (use --input -).
No auxiliary process artifacts are created.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from skills._shared.scripts.artifact_io import utc_now, write_json_atomic
from skills._shared.scripts.path_utils import is_relative_reference
from skills._shared.scripts.schema_validate import validate
from experience_gates import assess_observation


def _read_descriptor(value: str) -> dict[str, Any]:
    if value == "-":
        return json.load(sys.stdin)
    return json.loads(Path(value).read_text(encoding="utf-8"))


def _check_relative_refs(record: dict[str, Any]) -> None:
    refs: list[str] = [
        record["source_workflow_ref"],
        record["responsible_skill"],
        *record.get("source_run_refs", []),
        *record.get("evidence_refs", []),
    ]
    if record.get("source_evidence_summary_ref"):
        refs.append(record["source_evidence_summary_ref"])
    if record.get("pattern", {}).get("change_ref"):
        refs.append(record["pattern"]["change_ref"])
    bad = [value for value in refs if not is_relative_reference(str(value)) or ".." in Path(str(value)).parts]
    if bad:
        raise ValueError(f"non-portable references are not allowed: {bad}")


def normalize(descriptor: dict[str, Any]) -> dict[str, Any]:
    record = dict(descriptor)
    record["schema_version"] = "2.1"
    record.setdefault("created_at", utc_now())
    kind = record.get("kind")
    if "candidate_eligible" not in record or "eligibility_reason" not in record:
        raise ValueError("descriptor must explicitly provide candidate_eligible and eligibility_reason")
    if kind == "unresolved_failure" and record["candidate_eligible"]:
        raise ValueError("unresolved_failure cannot be Candidate-eligible")
    if kind == "failure_pattern" and not record["candidate_eligible"]:
        raise ValueError("failure_pattern must be explicitly marked Candidate-eligible to trigger a validation-bound hypothesis")
    decision = assess_observation(record)
    if record["candidate_eligible"] is not decision.candidate_eligible:
        raise ValueError(
            "candidate_eligible does not match deterministic Experience gates: "
            + decision.reason
        )
    if not decision.candidate_eligible and kind in {"successful_pattern", "verified_repair"}:
        raise ValueError("successful/verified Experience lacks mandatory evidence: " + decision.reason)
    record["eligibility_reason"] = decision.reason
    _check_relative_refs(record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evolution-root", type=Path, required=True)
    parser.add_argument("--input", required=True, help="UTF-8 JSON descriptor path or '-' for stdin")
    args = parser.parse_args()

    record = normalize(_read_descriptor(args.input))
    experience_id = record.get("experience_id")
    if not experience_id:
        raise ValueError("experience_id is required")
    out = args.evolution_root / "experiences" / f"{experience_id}.json"
    if out.exists():
        raise FileExistsError(f"Experience already exists: {out}")
    write_json_atomic(out, record)
    errors = validate(out, ROOT / "schemas" / "experience_record.schema.json")
    if errors:
        out.unlink(missing_ok=True)
    print(json.dumps({"status": "passed" if not errors else "failed", "artifact": out.as_posix(), "errors": errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
