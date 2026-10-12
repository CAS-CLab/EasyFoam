"""Build and validate the single canonical ``evidence_summary.json``."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "skills" / "workflow" / "scripts"))

from skills._shared.scripts.artifact_io import read_json, validate_json_value, write_json_atomic
from skills._shared.scripts.schema_validate import validate
from workflow_ledger import add_evidence, add_issue, advance, finish, load, record_artifact, save, semantic_errors

CATEGORIES = ("requirement", "case_contract", "mesh", "execution", "numerical", "physical", "visual")
STATUSES = {"passed", "limited", "failed", "blocked", "not_assessed", "not_applicable"}


def assessment(
    status: str,
    summary: str,
    status_basis: str,
    refs: list[str] | None = None,
    limitations: list[str] | None = None,
    observations: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "summary": summary,
        "status_basis": status_basis,
        "observations": observations or {},
        "evidence_refs": refs or [],
        "limitations": limitations or [],
    }


def parse_objects(values: list[str], label: str) -> list[dict[str, Any]]:
    result = []
    for raw in values:
        item = json.loads(raw)
        if not isinstance(item, dict):
            raise ValueError(f"{label} must be a JSON object")
        result.append(item)
    return result


def latest_formal_run(run_dir: Path, workflow: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    for ref in reversed(workflow.get("artifacts", {}).get("run_records", [])):
        path = run_dir / ref
        if not path.is_file() or validate(path, ROOT / "schemas" / "run_record.schema.json"):
            continue
        record = read_json(path)
        if record.get("mode") in {"formal", "resume"}:
            return ref, record
    return None, None


def defaults(run_dir: Path, workflow: dict[str, Any], spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    open_blockers = [item for item in spec.get("review_required", {}).get("items", []) if item.get("blocking") and item.get("status") == "open"]
    requirement = assessment(
        "blocked" if open_blockers else "passed",
        "Decisive planning requirements remain unresolved." if open_blockers else "The released CaseSpec has no open decisive review item.",
        "CaseSpec semantic release state and review items.",
        ["case_spec.json"],
        [item.get("question", "Open blocking review item.") for item in open_blockers],
    )
    formal = workflow.get("artifacts", {}).get("formal_case")
    case_contract = assessment(
        "passed" if formal else "not_assessed",
        "Validated formal case and content hash are recorded." if formal else "No validated formal case is recorded.",
        "workflow.json formal_case reference and hash." if formal else "Static case validation has not been supplied.",
        [formal["path"]] if formal else [],
        [] if formal else ["Formal case contract is unavailable."],
        {"content_sha256": formal.get("content_sha256"), "mesh_sha256": formal.get("mesh_sha256")} if formal else {},
    )
    latest_ref, latest = latest_formal_run(run_dir, workflow)
    if latest:
        status_map = {"succeeded": "passed", "failed": "failed", "blocked": "blocked"}
        execution = assessment(
            status_map[latest["terminal_status"]],
            latest.get("terminal_reason", ""),
            "Latest schema-valid formal/resume run record.",
            [latest_ref],
            [],
            {
                "attempt_id": latest["attempt_id"],
                "mode": latest["mode"],
                "completed_time_or_iteration": latest.get("completed_time_or_iteration"),
                "formal_terminal_status": latest.get("runtime_summary", {}).get("formal_terminal_status"),
            },
        )
    else:
        execution = assessment(
            "not_assessed",
            "No valid formal/resume run record is available.",
            "Smoke and diagnostic records are auxiliary evidence only.",
            [],
            ["Formal execution has not been assessed."],
        )
    visuals_requested = bool(spec.get("outputs", {}).get("visuals"))
    return {
        "requirement": requirement,
        "case_contract": case_contract,
        "mesh": assessment("not_assessed", "Mesh credibility requires topology, quality, patch/zone, and resolution evidence.", "No decisive mesh assessment was supplied."),
        "execution": execution,
        "numerical": assessment("not_assessed", "Numerical credibility has not been assessed.", "Residual, monitored-quantity, timestep, boundedness, or conservation evidence is missing."),
        "physical": assessment("not_assessed", "Physical credibility has not been assessed.", "Problem-specific physical evidence is missing."),
        "visual": assessment("not_assessed" if visuals_requested else "not_applicable", "Requested visual evidence has not been assessed." if visuals_requested else "No visual evidence was requested.", "CaseSpec visual contract."),
    }


def normalize_qois(spec: dict[str, Any], supplied: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_name = {item.get("name") or item.get("qoi_id"): item for item in supplied}
    result = []
    for contract in spec.get("outputs", {}).get("qois", []):
        name = contract.get("qoi_id") or contract.get("name")
        item = by_name.pop(name, None) or {}
        status = item.get("status", "not_assessed")
        qoi = {
            "name": name,
            "status": status,
            "value": item.get("value"),
            "unit": item.get("unit", contract.get("unit")),
            "method": item.get("method", contract.get("method", "")),
            "acceptance_criterion": item.get("acceptance_criterion", contract.get("acceptance_criterion")),
            "status_basis": item.get("status_basis", ""),
            "summary": item.get("summary", "Requested QoI has not been assessed."),
            "evidence_refs": item.get("evidence_refs", []),
        }
        if status in {"passed", "failed"} and (not qoi["acceptance_criterion"] or not qoi["status_basis"] or not qoi["evidence_refs"]):
            qoi["status"] = "limited"
            qoi["status_basis"] = "Pass/fail requires a criterion, basis, and evidence reference."
            qoi["summary"] = "QoI value is available but does not support the requested pass/fail claim."
        result.append(qoi)
    for name, item in by_name.items():
        item = dict(item)
        item.setdefault("name", name)
        item.setdefault("status", "not_assessed")
        item.setdefault("value", None)
        item.setdefault("unit", None)
        item.setdefault("method", "")
        item.setdefault("acceptance_criterion", None)
        item.setdefault("status_basis", "")
        item.setdefault("summary", "Additional QoI observation.")
        item.setdefault("evidence_refs", [])
        result.append(item)
    return result


def normalize_outputs(workflow: dict[str, Any], supplied: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_name = {item["name"]: item for item in supplied}
    result = []
    for name in workflow.get("requested_scope", {}).get("outputs", []):
        result.append(by_name.pop(name, {"name": name, "status": "blocked", "path": None, "summary": "Requested output is not recorded as available."}))
    result.extend(by_name.values())
    return result


OUTPUT_STATUS_MAP = {
    "available": "passed",
    "not_applicable": "not_applicable",
    "failed": "failed",
    "blocked": "blocked",
}


def compute_overall(
    assessments: dict[str, dict[str, Any]],
    qois: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
    workflow_status: str,
) -> str:
    statuses = (
        [block["status"] for block in assessments.values()]
        + [item["status"] for item in qois]
        + [OUTPUT_STATUS_MAP[item["status"]] for item in outputs]
    )
    if "blocked" in statuses or workflow_status == "blocked":
        return "blocked"
    if "failed" in statuses or workflow_status == "failed":
        return "failed"
    if any(status in {"limited", "not_assessed"} for status in statuses):
        return "limited"
    return "passed"


def highest_claim(assessments: dict[str, dict[str, Any]], qois: list[dict[str, Any]]) -> str:
    if assessments["requirement"]["status"] != "passed":
        return "none"
    claim = "case_defined"
    if assessments["case_contract"]["status"] != "passed":
        return claim
    claim = "case_materialized"
    if assessments["mesh"]["status"] != "passed":
        return claim
    claim = "mesh_credible"
    if assessments["execution"]["status"] != "passed":
        return claim
    claim = "executed"
    if assessments["numerical"]["status"] != "passed":
        return claim
    claim = "numerically_credible"
    if assessments["physical"]["status"] != "passed":
        return claim
    claim = "physically_credible"
    if qois and all(item["status"] in {"passed", "not_applicable"} for item in qois):
        claim = "validated_for_requested_qois"
    return claim


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--assessment", action="append", default=[], help="JSON object with category/status/summary/status_basis/evidence_refs/limitations/observations")
    parser.add_argument("--qoi", action="append", default=[])
    parser.add_argument("--required-output", action="append", default=[])
    parser.add_argument("--limitation", action="append", default=[])
    parser.add_argument("--claim-boundary", action="append", default=[])
    parser.add_argument("--review-item", action="append", default=[])
    parser.add_argument("--finalize-workflow", choices=["in_progress", "succeeded", "failed", "blocked"])
    args = parser.parse_args()

    workflow_path = args.run_dir / "workflow.json"
    case_spec_path = args.run_dir / "case_spec.json"
    for path, schema in [(workflow_path, "workflow.schema.json"), (case_spec_path, "case_spec.schema.json")]:
        errors = validate(path, ROOT / "schemas" / schema)
        if errors:
            raise RuntimeError(f"invalid {path.name}: {'; '.join(errors)}")
    workflow = load(args.run_dir)
    spec = read_json(case_spec_path)
    assessments = defaults(args.run_dir, workflow, spec)
    for item in parse_objects(args.assessment, "assessment"):
        category = item.pop("category", None)
        if category not in CATEGORIES:
            raise ValueError(f"assessment category must be one of {CATEGORIES}")
        status = item.get("status", "not_assessed")
        if status not in STATUSES:
            raise ValueError(f"invalid assessment status: {status}")
        assessments[category] = assessment(
            status,
            item.get("summary", ""),
            item.get("status_basis", ""),
            item.get("evidence_refs", []),
            item.get("limitations", []),
            item.get("observations", {}),
        )

    open_blockers = [
        item for item in spec.get("review_required", {}).get("items", [])
        if item.get("blocking") and item.get("status") == "open"
    ]
    if open_blockers and assessments["requirement"]["status"] == "passed":
        raise ValueError("requirement assessment cannot pass while CaseSpec has open decisive review items")
    if not workflow.get("artifacts", {}).get("formal_case") and assessments["case_contract"]["status"] == "passed":
        raise ValueError("case-contract assessment cannot pass without a validated formal_case record")
    formal_run_ref, formal_run = latest_formal_run(args.run_dir, workflow)
    if formal_run is None and assessments["execution"]["status"] == "passed":
        raise ValueError("execution assessment cannot pass without a schema-valid formal/resume run_record.json")

    qois = normalize_qois(spec, parse_objects(args.qoi, "qoi"))
    outputs = normalize_outputs(workflow, parse_objects(args.required_output, "required-output"))
    highest = highest_claim(assessments, qois)
    overall = compute_overall(assessments, qois, outputs, workflow["status"])

    limitations = list(args.limitation)
    for block in assessments.values():
        limitations.extend(block["limitations"])
    for output in outputs:
        if output["status"] not in {"available", "not_applicable"}:
            limitations.append(output["summary"])
    limitations = sorted(set(item for item in limitations if item))
    implied_status = {
        "passed": "succeeded",
        "limited": "in_progress",
        "failed": "failed",
        "blocked": "blocked",
    }[overall]
    if args.finalize_workflow and args.finalize_workflow != implied_status:
        raise ValueError(
            f"requested Workflow finalization {args.finalize_workflow} is inconsistent with evidence outcome {overall}; "
            f"expected {implied_status}"
        )
    final_status = args.finalize_workflow or implied_status

    summary = {
        "schema_version": "2.1",
        "workflow_id": workflow["workflow_id"],
        "case_id": workflow["case_id"],
        "workflow_status": final_status,
        "overall": {
            "status": overall,
            "highest_supported_claim": highest,
            "summary": f"Highest supported claim: {highest}. Overall evidence status: {overall}.",
        },
        "assessments": assessments,
        "qoi_results": qois,
        "required_outputs": outputs,
        "limitations": limitations,
        "claim_boundaries": list(dict.fromkeys(args.claim_boundary + [
            "Execution success does not by itself establish numerical or physical credibility.",
            "Smoke or diagnostic execution cannot replace formal-run evidence.",
            "A value alone does not establish QoI acceptance.",
            "Visual evidence cannot replace conservation or quantitative checks.",
        ])),
        "user_review": {
            "required": overall != "passed" or bool(args.review_item),
            "items": list(dict.fromkeys(args.review_item + limitations)),
        },
    }

    record_artifact(workflow, "evidence_summary", "evidence_summary.json")
    for item in outputs:
        if item["status"] == "available" and item.get("path"):
            record_artifact(workflow, "requested_output", item["path"])
    add_evidence(
        workflow,
        "final_evidence_summary",
        "postprocess",
        "passed" if overall == "passed" else "failed" if overall == "failed" else "blocked" if overall == "blocked" else "limited",
        summary["overall"]["summary"],
        "evidence_summary.json",
    )
    if overall == "passed":
        advance(workflow, "postprocess")
    elif overall == "limited":
        add_issue(workflow, "limitation", "postprocess", summary["overall"]["summary"], ["evidence_summary.json"])
        route_reason = "Additional evidence or user review remains required before Postprocess can complete."
        workflow["status"] = "in_progress"
        workflow["active_or_last_stage"] = "postprocess"
        workflow["active_specialist"] = None
        workflow["next_action"] = {"target_stage": "postprocess", "target_specialist": None, "reason": route_reason}
    else:
        add_issue(
            workflow,
            "blocker" if overall == "blocked" else "limitation",
            "postprocess",
            summary["overall"]["summary"],
            ["evidence_summary.json"],
        )
        finish(workflow, final_status, "postprocess")

    summary_errors = validate_json_value(
        summary,
        ROOT / "schemas" / "evidence_summary.schema.json",
        directory=args.run_dir,
    )
    workflow_semantic = semantic_errors(workflow)
    workflow_errors = validate_json_value(
        workflow,
        ROOT / "schemas" / "workflow.schema.json",
        directory=args.run_dir,
    )
    all_errors = summary_errors + [f"workflow semantic: {item}" for item in workflow_semantic] + [f"workflow schema: {item}" for item in workflow_errors]
    if all_errors:
        print(json.dumps({"status": "failed", "errors": all_errors}, ensure_ascii=False, indent=2))
        return 1

    output = args.run_dir / "evidence_summary.json"
    write_json_atomic(output, summary)
    save(args.run_dir, workflow)
    print(json.dumps({"status": "passed", "output": output.as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
