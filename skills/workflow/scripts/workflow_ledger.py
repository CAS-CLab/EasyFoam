"""Read and update the minimal canonical EasyFoam ``workflow.json``.

The ledger stores the user-scoped target, current or final Workflow state,
canonical artifact references, stage-scoped decisive evidence,
limitations/blockers, and one next action. Specialist histories and temporary
reasoning are not stored here.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from skills._shared.scripts.artifact_io import read_json, utc_now, validate_json_value, write_json_atomic

STAGES = ("plan", "write", "run", "postprocess")
ARTIFACT_KINDS = (
    "case_spec",
    "formal_case",
    "run_record",
    "evidence_summary",
    "requested_output",
    "experience_record",
)
EVIDENCE_STATUSES = ("passed", "failed", "blocked", "limited", "not_assessed")


def initial(
    workflow_id: str,
    case_id: str,
    goal: str,
    stages: list[str],
    outputs: list[str] | None = None,
    target_ref: str | None = None,
    openfoam_version: str = "Foundation-v13",
) -> dict[str, Any]:
    requested = set(stages)
    ordered = [stage for stage in STAGES if stage in requested]
    if not ordered:
        raise ValueError("at least one Workflow stage is required")
    now = utc_now()
    return {
        "schema_version": "2.2",
        "workflow_id": workflow_id,
        "case_id": case_id,
        "openfoam_version": openfoam_version,
        "requested_scope": {
            "goal": goal,
            "target_ref": target_ref,
            "stages": ordered,
            "outputs": list(dict.fromkeys(outputs or [])),
            "extensions": [],
        },
        "status": "in_progress",
        "active_or_last_stage": ordered[0],
        "active_specialist": None,
        "completed_scope": [],
        "artifacts": {
            "case_spec": None,
            "formal_case": None,
            "run_records": [],
            "evidence_summary": None,
            "requested_outputs": [],
            "experience_records": [],
        },
        "decisive_evidence": [],
        "limitations_or_blockers": [],
        "next_action": {
            "target_stage": ordered[0],
            "target_specialist": None,
            "reason": "Begin the earliest requested stage.",
        },
        "created_at": now,
        "updated_at": now,
    }


def _infer_legacy_evidence_stage(item: dict[str, Any], workflow: dict[str, Any]) -> str:
    claim = str(item.get("claim", "")).lower()
    ref = str(item.get("ref", "")).lower()
    if "formal_case" in claim or ref == "case" or ref.startswith("case/"):
        return "write"
    if "execution" in claim or "attempt" in claim or ref.startswith("runs/"):
        return "run"
    if "evidence_summary" in claim or ref.endswith("evidence_summary.json"):
        return "postprocess"
    active = workflow.get("active_or_last_stage")
    return active if active in STAGES else "plan"


def load(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "workflow.json"
    if not path.is_file():
        raise FileNotFoundError(f"workflow.json not found: {path}")
    workflow = read_json(path)
    if workflow.get("schema_version") == "2.1":
        for item in workflow.get("decisive_evidence", []):
            item.setdefault("source_stage", _infer_legacy_evidence_stage(item, workflow))
        workflow["schema_version"] = "2.2"
    return workflow


def semantic_errors(workflow: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    requested = set(workflow["requested_scope"]["stages"])
    completed = set(workflow["completed_scope"])
    if not completed <= requested:
        errors.append(f"completed_scope contains unrequested stages: {sorted(completed - requested)}")
    active = workflow["active_or_last_stage"]
    if active != "complete" and active not in requested:
        errors.append(f"active_or_last_stage is outside requested scope: {active}")
    next_action = workflow.get("next_action")
    if next_action and next_action["target_stage"] not in requested:
        errors.append(f"next_action targets an unrequested stage: {next_action['target_stage']}")
    if workflow["status"] == "succeeded" and completed != requested:
        errors.append("succeeded Workflow must complete exactly the requested stages")
    if workflow["status"] == "in_progress" and next_action is None:
        errors.append("in_progress Workflow requires next_action")
    if next_action and next_action["target_stage"] in completed:
        errors.append(f"next_action targets an already completed stage: {next_action['target_stage']}")
    if workflow.get("schema_version") == "2.2":
        missing_stage = [item.get("claim", "<unnamed>") for item in workflow.get("decisive_evidence", []) if item.get("source_stage") not in STAGES]
        if missing_stage:
            errors.append("Workflow 2.2 decisive evidence requires source_stage: " + ", ".join(missing_stage))
    return errors


def _validate_value(run_dir: Path, workflow: dict[str, Any]) -> None:
    semantic = semantic_errors(workflow)
    if semantic:
        raise RuntimeError("workflow.json semantic validation failed: " + "; ".join(semantic))
    errors = validate_json_value(workflow, ROOT / "schemas" / "workflow.schema.json", directory=run_dir)
    if errors:
        raise RuntimeError("workflow.json validation failed: " + "; ".join(errors))


def _require_requested(workflow: dict[str, Any], stage: str) -> None:
    if stage not in workflow["requested_scope"]["stages"]:
        raise ValueError(f"Workflow stage is outside requested scope: {stage}")


def extend_scope(workflow: dict[str, Any], stage: str, reason: str) -> None:
    if stage not in STAGES:
        raise ValueError(f"unsupported Workflow stage: {stage}")
    if stage not in workflow["requested_scope"]["stages"]:
        workflow["requested_scope"]["stages"].append(stage)
        workflow["requested_scope"]["stages"] = [item for item in STAGES if item in workflow["requested_scope"]["stages"]]
        workflow["requested_scope"].setdefault("extensions", []).append({
            "stage": stage,
            "reason": reason,
            "recorded_at": utc_now(),
        })


def save(run_dir: Path, workflow: dict[str, Any]) -> Path:
    workflow["updated_at"] = utc_now()
    _validate_value(run_dir, workflow)
    path = run_dir / "workflow.json"
    write_json_atomic(path, workflow)
    return path


def route(workflow: dict[str, Any], stage: str, specialist: str | None, reason: str) -> None:
    if stage not in STAGES:
        raise ValueError(f"unsupported Workflow stage: {stage}")
    _require_requested(workflow, stage)
    if stage in workflow["completed_scope"]:
        raise ValueError(f"cannot route to an already completed stage: {stage}; reopen it first")
    workflow["status"] = "in_progress"
    workflow["active_or_last_stage"] = stage
    workflow["active_specialist"] = specialist
    workflow["next_action"] = {
        "target_stage": stage,
        "target_specialist": specialist,
        "reason": reason,
    }


def complete_stage(workflow: dict[str, Any], stage: str) -> None:
    """Internal primitive. Public callers should normally use ``advance``."""
    if stage not in STAGES:
        raise ValueError(f"unsupported Workflow stage: {stage}")
    _require_requested(workflow, stage)
    if stage not in workflow["completed_scope"]:
        workflow["completed_scope"].append(stage)
    workflow["completed_scope"] = [item for item in STAGES if item in workflow["completed_scope"]]
    workflow["active_or_last_stage"] = stage


def advance(
    workflow: dict[str, Any],
    stage: str,
    next_stage: str | None = None,
    next_specialist: str | None = None,
    reason: str | None = None,
) -> None:
    """Atomically complete one stage and route to the next requested stage."""
    if stage in workflow["completed_scope"]:
        raise ValueError(f"stage is already complete: {stage}; reopen it before completing it again")
    complete_stage(workflow, stage)
    remaining = [item for item in workflow["requested_scope"]["stages"] if item not in workflow["completed_scope"]]
    if next_stage is not None:
        if next_stage not in remaining:
            raise ValueError(f"next stage must be requested and incomplete: {next_stage}")
        if not reason:
            raise ValueError("advance with a next stage requires --reason")
        route(workflow, next_stage, next_specialist, reason)
    elif remaining:
        raise ValueError(f"remaining requested stages require --next-stage: {remaining}")
    else:
        finish(workflow, "succeeded", stage)


def reopen_from(workflow: dict[str, Any], stage: str, specialist: str | None, reason: str) -> None:
    """Invalidate a completed stage and its downstream claims, then route to it.

    Immutable run directories remain referenced for audit. Only their current
    stage-completion and decisive-evidence claims are invalidated.
    """
    if stage not in STAGES:
        raise ValueError(f"unsupported Workflow stage: {stage}")
    _require_requested(workflow, stage)
    affected = set(STAGES[STAGES.index(stage):])
    workflow["completed_scope"] = [item for item in workflow["completed_scope"] if item not in affected]
    artifacts = workflow["artifacts"]
    if "plan" in affected:
        artifacts["case_spec"] = None
    if "write" in affected:
        artifacts["formal_case"] = None
    if "postprocess" in affected:
        artifacts["evidence_summary"] = None
        artifacts["requested_outputs"] = []
    workflow["decisive_evidence"] = [
        item for item in workflow["decisive_evidence"] if item.get("source_stage") not in affected
    ]
    workflow["limitations_or_blockers"] = [
        item for item in workflow["limitations_or_blockers"] if item.get("source_stage") not in affected
    ]
    route(workflow, stage, specialist, reason)


def record_artifact(
    workflow: dict[str, Any],
    kind: str,
    path: str,
    content_sha256: str | None = None,
    mesh_sha256: str | None = None,
    input_sha256: str | None = None,
    initial_state_sha256: str | None = None,
) -> None:
    artifacts = workflow["artifacts"]
    if kind == "case_spec":
        artifacts["case_spec"] = path
    elif kind == "formal_case":
        if not all([content_sha256, mesh_sha256, input_sha256, initial_state_sha256]):
            raise ValueError("formal_case requires content, input, mesh, and initial-state hashes")
        artifacts["formal_case"] = {
            "path": path,
            "content_sha256": content_sha256,
            "input_sha256": input_sha256,
            "mesh_sha256": mesh_sha256,
            "initial_state_sha256": initial_state_sha256,
        }
    elif kind == "run_record":
        if path not in artifacts["run_records"]:
            artifacts["run_records"].append(path)
    elif kind == "evidence_summary":
        artifacts["evidence_summary"] = path
    elif kind == "requested_output":
        if path not in artifacts["requested_outputs"]:
            artifacts["requested_outputs"].append(path)
    elif kind == "experience_record":
        if path not in artifacts["experience_records"]:
            artifacts["experience_records"].append(path)
    else:
        raise ValueError(f"unsupported artifact kind: {kind}")


def add_evidence(
    workflow: dict[str, Any],
    claim: str,
    source_stage: str,
    status: str,
    summary: str,
    ref: str,
) -> None:
    if source_stage not in STAGES:
        raise ValueError(f"unsupported evidence source stage: {source_stage}")
    if status not in EVIDENCE_STATUSES:
        raise ValueError(f"unsupported evidence status: {status}")
    item = {
        "claim": claim,
        "source_stage": source_stage,
        "status": status,
        "ref": ref,
        "summary": summary,
    }
    if item not in workflow["decisive_evidence"]:
        workflow["decisive_evidence"].append(item)


def add_issue(
    workflow: dict[str, Any],
    kind: str,
    source_stage: str,
    summary: str,
    refs: list[str] | None = None,
) -> None:
    if kind not in {"limitation", "blocker"}:
        raise ValueError("issue kind must be limitation or blocker")
    if source_stage not in STAGES:
        raise ValueError(f"unsupported issue source stage: {source_stage}")
    item = {
        "kind": kind,
        "summary": summary,
        "source_stage": source_stage,
        "evidence_refs": list(dict.fromkeys(refs or [])),
    }
    if item not in workflow["limitations_or_blockers"]:
        workflow["limitations_or_blockers"].append(item)


def finish(
    workflow: dict[str, Any],
    status: str,
    last_stage: str,
    next_stage: str | None = None,
    next_specialist: str | None = None,
    reason: str | None = None,
) -> None:
    if status not in {"in_progress", "succeeded", "failed", "blocked"}:
        raise ValueError(f"unsupported Workflow status: {status}")
    if status == "succeeded":
        missing = [stage for stage in workflow["requested_scope"]["stages"] if stage not in workflow["completed_scope"]]
        if missing:
            raise ValueError(f"cannot succeed before requested stages are complete: {missing}")
    if status in {"failed", "blocked"}:
        decisive_failure = any(item["status"] in {"failed", "blocked"} for item in workflow["decisive_evidence"])
        if not workflow["limitations_or_blockers"] and not decisive_failure:
            raise ValueError(f"{status} requires a recorded blocker, limitation, or decisive failure evidence")
    workflow["status"] = status
    workflow["active_or_last_stage"] = "complete" if status == "succeeded" else last_stage
    workflow["active_specialist"] = None
    if next_stage is not None:
        _require_requested(workflow, next_stage)
        if next_stage in workflow["completed_scope"]:
            raise ValueError(f"next stage is already complete: {next_stage}")
        if reason is None:
            raise ValueError("a routed next action requires a reason")
        workflow["next_action"] = {
            "target_stage": next_stage,
            "target_specialist": next_specialist,
            "reason": reason,
        }
    elif status == "in_progress":
        raise ValueError("in_progress requires a next action")
    else:
        workflow["next_action"] = None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "extend-scope", "route", "advance", "reopen", "artifact", "evidence", "issue", "finish", "validate"])
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--workflow-id")
    parser.add_argument("--case-id")
    parser.add_argument("--goal")
    parser.add_argument("--stage", choices=STAGES)
    parser.add_argument("--required-stage", action="append", choices=STAGES, default=[])
    parser.add_argument("--output", action="append", default=[])
    parser.add_argument("--target-ref")
    parser.add_argument("--openfoam-version", default="Foundation-v13")
    parser.add_argument("--specialist")
    parser.add_argument("--reason")
    parser.add_argument("--kind", choices=ARTIFACT_KINDS)
    parser.add_argument("--path")
    parser.add_argument("--content-sha256")
    parser.add_argument("--mesh-sha256")
    parser.add_argument("--input-sha256")
    parser.add_argument("--initial-state-sha256")
    parser.add_argument("--claim")
    parser.add_argument("--evidence-status", choices=EVIDENCE_STATUSES)
    parser.add_argument("--summary")
    parser.add_argument("--evidence-ref", action="append", default=[])
    parser.add_argument("--issue-kind", choices=["limitation", "blocker"])
    parser.add_argument("--status", choices=["in_progress", "succeeded", "failed", "blocked"])
    parser.add_argument("--next-stage", choices=STAGES)
    parser.add_argument("--next-specialist")
    args = parser.parse_args()

    args.run_dir.mkdir(parents=True, exist_ok=True)
    if args.action == "init":
        if not all([args.workflow_id, args.case_id, args.goal, args.required_stage]):
            parser.error("init requires --workflow-id, --case-id, --goal, and --required-stage")
        workflow = initial(args.workflow_id, args.case_id, args.goal, args.required_stage, args.output, args.target_ref, args.openfoam_version)
    else:
        workflow = load(args.run_dir)
        if args.action == "extend-scope":
            if not args.stage or not args.reason:
                parser.error("extend-scope requires --stage and --reason")
            extend_scope(workflow, args.stage, args.reason)
        elif args.action == "route":
            if not args.stage or not args.reason:
                parser.error("route requires --stage and --reason")
            route(workflow, args.stage, args.specialist, args.reason)
        elif args.action == "advance":
            if not args.stage:
                parser.error("advance requires --stage")
            advance(workflow, args.stage, args.next_stage, args.next_specialist, args.reason)
        elif args.action == "reopen":
            if not args.stage or not args.reason:
                parser.error("reopen requires --stage and --reason")
            reopen_from(workflow, args.stage, args.specialist, args.reason)
        elif args.action == "artifact":
            if not args.kind or not args.path:
                parser.error("artifact requires --kind and --path")
            record_artifact(workflow, args.kind, args.path, args.content_sha256, args.mesh_sha256, args.input_sha256, args.initial_state_sha256)
        elif args.action == "evidence":
            if not all([args.claim, args.stage, args.evidence_status, args.summary, args.path]):
                parser.error("evidence requires --claim, --stage, --evidence-status, --summary, and --path")
            add_evidence(workflow, args.claim, args.stage, args.evidence_status, args.summary, args.path)
        elif args.action == "issue":
            if not all([args.issue_kind, args.stage, args.summary]):
                parser.error("issue requires --issue-kind, --stage, and --summary")
            add_issue(workflow, args.issue_kind, args.stage, args.summary, args.evidence_ref)
        elif args.action == "finish":
            if not args.status or not args.stage:
                parser.error("finish requires --status and --stage")
            finish(workflow, args.status, args.stage, args.next_stage, args.next_specialist, args.reason)
        elif args.action == "validate":
            pass
    path = save(args.run_dir, workflow)
    print(json.dumps({"status": "passed", "workflow": path.as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
