---
name: workflow-run
description: Coordinate one or more OpenFOAM execution attempts and runtime diagnosis.
---

# Run

Run executes the validated formal case or an explicitly scoped derivative. It owns attempt selection and terminal execution evidence, not CFD credibility claims.

## 1. Preconditions

Require a released `case_spec.json`, a validated formal case reference and hash in `workflow.json`, and the requested execution scope.

## 2. Specialist Routing

| Need | Specialist |
| --- | --- |
| Execute, resume, or rerun the command chain | `workflow/run/runner` |
| Diagnose a failed command or invalid runtime state | `workflow/run/debug-reviewer` |

## 3. Orchestration

1. Invoke `runner` for the requested attempt.
2. Accept one immutable `runs/<attempt_id>/run_record.json` and its command logs.
3. On failure, invoke `debug-reviewer`.
4. Route any verified formal-case repair through the ledger `reopen` operation to the earliest affected stage before another formal attempt; invalidate dependent stage-scoped evidence without deleting immutable run records.
5. Record the selected run record and next action in `workflow.json`.

## 4. Stage Result

Run creates one attempt directory containing `run_record.json` and stdout/stderr logs for commands that were actually executed. It does not create separate command, runtime-metrics, failure-signature, or attempt-manifest files by default.

Run succeeds when the requested attempt has a schema-valid run record with `terminal_status=succeeded`. This proves execution only, not numerical or physical credibility.

## 5. Failure and Return Routing

Runtime-only invocation or environment corrections remain in Run. Formal case, mesh, or planning changes return to Write or Plan as identified by `debug-reviewer`.
