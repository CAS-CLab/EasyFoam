"""Execute one OpenFOAM attempt and create exactly one run_record.json."""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "skills" / "workflow" / "scripts"))

from skills._shared.scripts.artifact_io import read_json, utc_now, write_validated_json_atomic
from skills._shared.scripts.hashing import formal_input_digest, state_digest, tree_digest
from skills._shared.scripts.openfoam_env import build_openfoam_command, discover
from workflow_ledger import add_evidence, add_issue, advance, finish, load, record_artifact, reopen_from, route, save

Executor = Callable[[list[str], Path], subprocess.CompletedProcess[str]]
FORMAL_MODES = {"formal", "resume"}
AUXILIARY_MODES = {"smoke", "diagnostic"}


def _inside(path: Path, root: Path, *, must_exist: bool = True) -> Path:
    resolved_root = root.resolve(strict=True)
    resolved_path = path.resolve(strict=must_exist)
    if not resolved_path.is_relative_to(resolved_root):
        raise ValueError(f"path must remain inside Workflow root: {path}")
    return resolved_path


def _rel(path: Path, run_dir: Path) -> str:
    return _inside(path, run_dir).relative_to(run_dir.resolve(strict=True)).as_posix()


def _default_executor(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        build_openfoam_command(command, cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=None,
    )


def _commands(spec: dict[str, Any], overrides: list[str]) -> list[list[str]]:
    if overrides:
        return [command for item in overrides if (command := shlex.split(item))]
    commands = [
        shlex.split(item)
        for item in spec.get("run", {}).get("preprocessing_commands", [])
        if item and not item.startswith("<")
    ]
    solver = spec.get("run", {}).get("solver_command")
    if solver:
        commands.append(shlex.split(solver))
    return commands


def _first_error(text: str) -> str | None:
    for line in text.splitlines():
        if re.search(r"FOAM FATAL|fatal error|\bERROR\b|undefined|segmentation fault", line, re.I):
            return line.strip()
    return None


def _numeric(value: Any) -> float | None:
    try:
        # OpenFOAM commonly prints terminal times with a unit suffix
        # (for example ``Time = 0.005s``), while CaseSpec stores a number.
        # Accept that presentation without weakening numeric validation.
        if isinstance(value, str):
            value = value.strip()
            if value.lower().endswith("s"):
                value = value[:-1].strip()
        return float(value)
    except (TypeError, ValueError):
        return None


def _last_time(text: str) -> str | None:
    matches = re.findall(r"^Time\s*=\s*([^\s]+)", text, re.M)
    return matches[-1] if matches else None


def _terminal_contract(spec: dict[str, Any], output: str) -> tuple[str, str, str | None, dict[str, Any]]:
    expected_raw = spec.get("run", {}).get("controls", {}).get("end_time", {}).get("value")
    actual_raw = _last_time(output)
    expected = _numeric(expected_raw)
    actual = _numeric(actual_raw)
    observations = {
        "expected_end_time_or_iteration": expected_raw,
        "actual_end_time_or_iteration": actual_raw,
    }
    if expected is None:
        return "blocked", "Formal terminal target is unresolved in CaseSpec.", actual_raw, observations
    if actual is None:
        return "blocked", "Solver returned zero but no verifiable 'Time =' terminal value was found.", actual_raw, observations
    tolerance = max(1.0e-12, abs(expected) * 1.0e-9)
    if actual + tolerance < expected:
        return "failed", f"Solver stopped at {actual_raw}, before declared end {expected_raw}.", actual_raw, observations
    return "succeeded", f"Declared terminal target {expected_raw} was reached at {actual_raw}.", actual_raw, observations


def _expected_version(value: str | None) -> str | None:
    match = re.search(r"(\d+)$", value or "")
    return match.group(1) if match else None


def _latest_parent_run(run_dir: Path, workflow: dict[str, Any]) -> str | None:
    for ref in reversed(workflow.get("artifacts", {}).get("run_records", [])):
        path = run_dir / ref
        if not path.is_file():
            continue
        record = read_json(path)
        if record.get("mode") in FORMAL_MODES and record.get("terminal_status") == "succeeded":
            return ref
    return None


def _latest_numeric_time(case_dir: Path) -> str | None:
    values: list[tuple[float, str]] = []
    for path in case_dir.iterdir():
        if path.is_dir() and path.name != "0":
            numeric = _numeric(path.name)
            if numeric is not None:
                values.append((numeric, path.name))
    return max(values)[1] if values else None


def _restart_contract(
    run_dir: Path,
    case_dir: Path,
    workflow: dict[str, Any],
    spec: dict[str, Any],
    requested_time: str | None,
) -> dict[str, Any]:
    start_from = spec.get("run", {}).get("controls", {}).get("start_from", {}).get("value")
    declared_start = spec.get("run", {}).get("controls", {}).get("start_time", {}).get("value")
    if requested_time:
        time_name = requested_time
    elif str(start_from).lower() == "latesttime":
        time_name = _latest_numeric_time(case_dir)
    else:
        time_name = str(declared_start) if declared_start not in {None, ""} else None
    if not time_name or time_name == "0":
        raise RuntimeError("resume requires an explicit non-zero restart time or startFrom latestTime")
    state_dir = _inside(case_dir / time_name, run_dir)
    required_fields = [field["name"] for field in spec.get("fields", []) if field.get("required")]
    missing_fields = [name for name in required_fields if not (state_dir / name).is_file()]
    if missing_fields:
        raise RuntimeError(f"restart state {time_name} is missing required fields: {missing_fields}")
    parent = _latest_parent_run(run_dir, workflow)
    if not parent:
        raise RuntimeError("resume requires a prior succeeded formal/resume run record")
    return {
        "parent_attempt_ref": parent,
        "restart_time": time_name,
        "restart_state_sha256": state_digest(case_dir, time_name)["tree_sha256"],
        "compatibility_status": "passed",
    }


def run_attempt(
    run_dir: Path,
    case_dir: Path,
    mode: str,
    modifications: list[str],
    command_overrides: list[str],
    executor: Executor | None = None,
    runtime: dict[str, Any] | None = None,
    *,
    allow_formal_command_override: bool = False,
    override_reason: str | None = None,
    restart_time: str | None = None,
) -> dict[str, Any]:
    run_dir = run_dir.resolve(strict=True)
    case_dir = _inside(case_dir, run_dir)
    spec = read_json(run_dir / "case_spec.json")
    workflow = load(run_dir)
    formal = workflow.get("artifacts", {}).get("formal_case")
    if not formal:
        raise RuntimeError("workflow.json has no validated formal_case record")

    current_input_hash = formal_input_digest(case_dir)["tree_sha256"]
    current_mesh_hash = tree_digest(case_dir / "constant" / "polyMesh")["tree_sha256"]
    if mode in FORMAL_MODES:
        if current_input_hash != formal["input_sha256"]:
            raise RuntimeError("formal input hash does not match workflow.json; return to Write")
        if current_mesh_hash != formal["mesh_sha256"]:
            raise RuntimeError("mesh hash does not match workflow.json; return to Write")
    if mode == "formal":
        current_initial_hash = state_digest(case_dir, "0")["tree_sha256"]
        if current_initial_hash != formal["initial_state_sha256"]:
            raise RuntimeError("initial state hash does not match workflow.json; return to Write")
    if mode in AUXILIARY_MODES:
        formal_case_dir = _inside(run_dir / formal["path"], run_dir)
        if case_dir == formal_case_dir:
            raise RuntimeError("smoke/diagnostic attempt must use a separate case copy")
        if not modifications:
            raise RuntimeError("smoke/diagnostic attempt requires at least one --modification")
    if command_overrides and mode in FORMAL_MODES:
        if not allow_formal_command_override or not override_reason:
            raise RuntimeError("formal/resume command override requires explicit approval and --override-reason")
        modifications = list(modifications) + [f"approved command override: {override_reason}"]

    restart = _restart_contract(run_dir, case_dir, workflow, spec, restart_time) if mode == "resume" else None
    if mode in FORMAL_MODES and "run" in workflow["completed_scope"]:
        reopen_from(
            workflow,
            "run",
            "skills/workflow/run/runner/SKILL.md",
            f"A new {mode} attempt invalidates prior Run and downstream completion claims.",
        )
        save(run_dir, workflow)
    attempt_id = f"{mode}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid4().hex[:8]}"
    attempt_dir = run_dir / "runs" / attempt_id
    attempt_dir.mkdir(parents=True, exist_ok=False)
    started = utc_now()
    runtime = runtime if runtime is not None else discover()
    commands = _commands(spec, command_overrides)
    current_case_hash = tree_digest(case_dir)["tree_sha256"]
    record: dict[str, Any] = {
        "schema_version": "1.1",
        "attempt_id": attempt_id,
        "workflow_id": workflow["workflow_id"],
        "case_id": workflow["case_id"],
        "mode": mode,
        "case_ref": _rel(case_dir, run_dir),
        "case_sha256": current_case_hash,
        "input_sha256": current_input_hash,
        "mesh_sha256": current_mesh_hash,
        "modifications": modifications,
        "environment": runtime,
        "commands": [],
        "terminal_status": "blocked",
        "terminal_reason": "OpenFOAM runtime unavailable.",
        "completed_time_or_iteration": None,
        "first_deterministic_error": None,
        "runtime_summary": {
            "command_chain_status": "not_run",
            "formal_terminal_status": "not_applicable" if mode in AUXILIARY_MODES else "not_run",
        },
        "produced_output_refs": [],
        "started_at": started,
        "completed_at": started,
    }
    if restart:
        record["restart"] = restart

    expected_version = _expected_version(spec.get("openfoam_version"))
    workflow_version = _expected_version(workflow.get("openfoam_version"))
    runtime_version = str(runtime.get("openfoam_version")) if runtime.get("openfoam_version") is not None else None
    if not runtime.get("available"):
        record["terminal_reason"] = str(runtime.get("reason") or "OpenFOAM runtime unavailable.")
    elif expected_version != workflow_version or runtime_version != expected_version:
        record["terminal_reason"] = (
            f"OpenFOAM version mismatch: CaseSpec={expected_version}, "
            f"Workflow={workflow_version}, runtime={runtime_version}."
        )
    elif not commands:
        record["terminal_reason"] = "No executable preprocessing or solver command was resolved."
    else:
        executor = executor or _default_executor
        all_output: list[str] = []
        record["runtime_summary"]["command_chain_status"] = "succeeded"
        for index, command in enumerate(commands, start=1):
            command_started = utc_now()
            tic = time.monotonic()
            completed = executor(command, case_dir)
            elapsed = time.monotonic() - tic
            command_completed = utc_now()
            safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(command[0]).name)
            stdout = attempt_dir / f"{index:02d}-{safe_name}.stdout.log"
            stderr = attempt_dir / f"{index:02d}-{safe_name}.stderr.log"
            stdout.write_text(completed.stdout or "", encoding="utf-8")
            stderr.write_text(completed.stderr or "", encoding="utf-8")
            output = (completed.stdout or "") + "\n" + (completed.stderr or "")
            all_output.append(output)
            record["commands"].append({
                "argv": command,
                "cwd": record["case_ref"],
                "started_at": command_started,
                "completed_at": command_completed,
                "elapsed_seconds": elapsed,
                "return_code": completed.returncode,
                "stdout_ref": _rel(stdout, run_dir),
                "stderr_ref": _rel(stderr, run_dir),
            })
            if completed.returncode != 0:
                record["runtime_summary"]["command_chain_status"] = "failed"
                record["terminal_status"] = "failed"
                record["terminal_reason"] = f"Command failed: {shlex.join(command)}"
                record["first_deterministic_error"] = _first_error(output)
                break
        else:
            joined = "\n".join(all_output)
            if mode in FORMAL_MODES:
                status, reason, actual, observations = _terminal_contract(spec, joined)
                record["terminal_status"] = status
                record["terminal_reason"] = reason
                record["completed_time_or_iteration"] = actual
                record["runtime_summary"].update(observations)
                record["runtime_summary"]["formal_terminal_status"] = (
                    "passed" if status == "succeeded" else "failed" if status == "failed" else "blocked"
                )
            else:
                record["terminal_status"] = "succeeded"
                record["terminal_reason"] = "Auxiliary command chain completed; no formal terminal claim was made."
                record["completed_time_or_iteration"] = _last_time(joined)

    record["completed_at"] = utc_now()
    record_path = attempt_dir / "run_record.json"
    write_validated_json_atomic(record_path, record, ROOT / "schemas" / "run_record.schema.json")

    ref = _rel(record_path, run_dir)
    record_artifact(workflow, "run_record", ref)
    evidence_status = {"succeeded": "passed", "failed": "failed", "blocked": "blocked"}[record["terminal_status"]]
    claim = "formal_execution_attempt" if mode in FORMAL_MODES else "auxiliary_execution_attempt"
    add_evidence(
        workflow,
        claim,
        "run",
        evidence_status if mode in FORMAL_MODES else ("limited" if record["terminal_status"] == "succeeded" else evidence_status),
        f"Attempt {attempt_id} ended as {record['terminal_status']}: {record['terminal_reason']}",
        ref,
    )
    run_already_complete = "run" in workflow["completed_scope"]
    if mode in FORMAL_MODES and record["terminal_status"] == "succeeded":
        next_stage = "postprocess" if "postprocess" in workflow["requested_scope"]["stages"] and "postprocess" not in workflow["completed_scope"] else None
        advance(
            workflow,
            "run",
            next_stage,
            None,
            "Formal execution succeeded; assess requested evidence." if next_stage else None,
        )
    elif mode in FORMAL_MODES and record["terminal_status"] == "failed":
        route(workflow, "run", "skills/workflow/run/debug-reviewer/SKILL.md", "Diagnose the failed command chain or terminal contract.")
    elif mode in FORMAL_MODES:
        add_issue(workflow, "blocker", "run", record["terminal_reason"], [ref])
        finish(workflow, "blocked", "run")
    elif not run_already_complete and record["terminal_status"] == "succeeded":
        route(workflow, "run", "skills/workflow/run/runner/SKILL.md", "Auxiliary attempt completed; formal or resume execution remains required.")
    elif not run_already_complete and record["terminal_status"] == "failed":
        route(workflow, "run", "skills/workflow/run/debug-reviewer/SKILL.md", "Diagnose the auxiliary attempt before formal execution.")
    elif not run_already_complete:
        add_issue(workflow, "blocker", "run", record["terminal_reason"], [ref])
        finish(workflow, "blocked", "run")
    # Auxiliary attempts after a completed formal Run only add evidence; they do
    # not reopen, complete, fail, or block the formal Workflow state.
    save(run_dir, workflow)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--case-dir", type=Path)
    parser.add_argument("--mode", choices=["formal", "smoke", "diagnostic", "resume"], default="formal")
    parser.add_argument("--modification", action="append", default=[])
    parser.add_argument("--command", action="append", default=[])
    parser.add_argument("--allow-formal-command-override", action="store_true")
    parser.add_argument("--override-reason")
    parser.add_argument("--restart-time")
    args = parser.parse_args()
    record = run_attempt(
        args.run_dir,
        args.case_dir or args.run_dir / "case",
        args.mode,
        args.modification,
        args.command,
        allow_formal_command_override=args.allow_formal_command_override,
        override_reason=args.override_reason,
        restart_time=args.restart_time,
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record["terminal_status"] == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
