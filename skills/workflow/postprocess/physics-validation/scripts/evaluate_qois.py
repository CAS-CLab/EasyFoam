"""Normalize supplied QoI observations against CaseSpec output contracts.

A numeric value alone is never marked as passed. The supplied observation must
include a criterion and an evidence-supported status basis for passed/failed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(contract: dict[str, Any], observation: Any, evidence_ref: str | None) -> dict[str, Any]:
    name = contract.get("qoi_id") or contract.get("name")
    base = {
        "name": name,
        "status": "not_assessed",
        "value": None,
        "unit": contract.get("unit"),
        "method": contract.get("method", ""),
        "acceptance_criterion": contract.get("acceptance_criterion"),
        "status_basis": "",
        "summary": "Requested QoI has not been assessed.",
        "evidence_refs": [],
    }
    if observation is None:
        return base
    if not isinstance(observation, dict):
        base.update({
            "status": "limited",
            "value": observation,
            "status_basis": "A value was supplied without an assessment method or criterion.",
            "summary": "QoI value is available but cannot support a pass/fail claim.",
            "evidence_refs": [evidence_ref] if evidence_ref else [],
        })
        return base

    base["value"] = observation.get("value")
    base["unit"] = observation.get("unit", base["unit"])
    base["method"] = observation.get("method", base["method"])
    base["acceptance_criterion"] = observation.get("acceptance_criterion", base["acceptance_criterion"])
    base["summary"] = observation.get("summary", "QoI observation supplied.")
    base["evidence_refs"] = observation.get("evidence_refs", [evidence_ref] if evidence_ref else [])
    requested_status = observation.get("status")
    basis = observation.get("status_basis", "")

    if requested_status in {"passed", "failed"}:
        if not base["acceptance_criterion"] or not basis or not base["evidence_refs"]:
            base["status"] = "limited"
            base["status_basis"] = "Pass/fail was requested without a complete criterion, basis, and evidence reference."
            base["summary"] = "QoI is limited because the pass/fail basis is incomplete."
        else:
            base["status"] = requested_status
            base["status_basis"] = basis
    elif requested_status in {"blocked", "limited", "not_assessed", "not_applicable"}:
        base["status"] = requested_status
        base["status_basis"] = basis
    elif base["value"] is not None:
        base["status"] = "limited"
        base["status_basis"] = basis or "A value exists, but no evidence-supported pass/fail decision was supplied."
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-spec", type=Path, required=True)
    parser.add_argument("--values", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.case_spec.read_text(encoding="utf-8"))
    observations = _load(args.values)
    results = []
    for contract in spec.get("outputs", {}).get("qois", []):
        name = contract.get("qoi_id") or contract.get("name")
        results.append(normalize(contract, observations.get(name), args.values.as_posix() if args.values else None))
    print(json.dumps({"qoi_results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
