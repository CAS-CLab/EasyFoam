"""Record referenced Candidate validation without creating a parallel replay artifact."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from skills._shared.scripts.artifact_io import utc_now, write_validated_json_atomic
from skills._shared.scripts.path_utils import is_relative_reference
from skills.evolution.scripts.evolution_integrity import load_valid_candidate, resolve_inside


PLAN_TO_RESULT = {
    "structural": "structural",
    "source_replay": "source",
    "holdout": "holdout",
    "negative_controls": "negative",
    "compatibility": "compatibility",
    "cross_scope": "cross_scope",
}


def _status(candidate: dict[str, Any]) -> str:
    by_kind = {item["kind"]: item["status"] for item in candidate["validation"]["results"]}
    required = [PLAN_TO_RESULT[key] for key, enabled in candidate["validation"]["plan"].items() if enabled]
    if any(sum(item["kind"] == kind for item in candidate["validation"]["results"]) != 1 for kind in required):
        return "frozen"
    if any(by_kind.get(kind) == "failed" for kind in required):
        return "invalid"
    if candidate["evidence_level"] not in {"E3_SOURCE_REPLAY", "E4_HOLDOUT_SUPPORT", "E5_CROSS_SCOPE_SUPPORT"}:
        return "frozen"
    if required and all(by_kind.get(kind) == "passed" for kind in required):
        return "validated"
    return "frozen"


def _level(candidate: dict[str, Any]) -> str:
    passed = {item["kind"] for item in candidate["validation"]["results"] if item["status"] == "passed"}
    repeated = len(candidate["source_experience_refs"]) >= 2
    if repeated and {"structural", "source", "holdout", "negative", "compatibility", "cross_scope"}.issubset(passed):
        return "E5_CROSS_SCOPE_SUPPORT"
    if repeated and {"structural", "source", "holdout", "negative", "compatibility"}.issubset(passed):
        return "E4_HOLDOUT_SUPPORT"
    if repeated and {"structural", "source"}.issubset(passed):
        return "E3_SOURCE_REPLAY"
    if repeated:
        return "E2_REPEATED_SOURCE"
    return "E1_VERIFIED_SOURCE"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evolution-root", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--kind", choices=["source", "holdout", "negative", "compatibility", "cross_scope"], required=True)
    parser.add_argument("--status", choices=["passed", "failed", "limited", "blocked", "not_run"], required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--evidence-ref", action="append", default=[])
    args = parser.parse_args()

    candidate, candidate_path, _ = load_valid_candidate(args.evolution_root, args.candidate)
    if candidate["status"] not in {"frozen", "validated", "invalid"}:
        raise ValueError("Candidate must be structurally frozen before behavioral validation is recorded")
    if args.status in {"passed", "failed", "limited"} and not args.evidence_ref:
        raise ValueError(f"{args.status} validation requires at least one evidence reference")
    bad = [ref for ref in args.evidence_ref if not is_relative_reference(ref) or ".." in Path(ref).parts]
    if bad:
        raise ValueError(f"non-portable evidence references are not allowed: {bad}")
    for ref in args.evidence_ref:
        resolve_inside(args.evolution_root, ref)
    # The CLI records result kinds (for example ``source``), while the
    # validation plan uses plan keys (``source_replay``).  Accept the result
    # vocabulary directly and resolve it through the inverse mapping.
    plan_key = args.kind if args.kind in PLAN_TO_RESULT else next(
        (key for key, value in PLAN_TO_RESULT.items() if value == args.kind), None
    )
    if plan_key is None or not candidate["validation"]["plan"].get(plan_key, False):
        raise ValueError(f"validation plan does not enable {args.kind}")

    result = {
        "kind": args.kind,
        "status": args.status,
        "summary": args.summary,
        "evidence_refs": args.evidence_ref,
        "recorded_at": utc_now(),
    }
    candidate["validation"]["results"] = [
        item for item in candidate["validation"]["results"] if item["kind"] != args.kind
    ]
    candidate["validation"]["results"].append(result)
    plan = candidate["validation"]["plan"]
    mapping = PLAN_TO_RESULT
    by_kind = {item["kind"]: item for item in candidate["validation"]["results"]}
    expected = {mapping[key] for key, enabled in plan.items() if enabled}
    if set(by_kind) != expected:
        # Keep the artifact frozen until every enabled plan item has a result.
        candidate["status"] = "frozen"
    candidate["evidence_level"] = _level(candidate)
    candidate["status"] = _status(candidate)
    candidate["updated_at"] = utc_now()
    write_validated_json_atomic(candidate_path, candidate, ROOT / "schemas" / "candidate_patch.schema.json")
    print(json.dumps({"status": "passed", "evidence_level": candidate["evidence_level"], "errors": []}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
