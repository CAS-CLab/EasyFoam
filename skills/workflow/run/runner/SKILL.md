---
name: workflow-runner
description: Execute one immutable OpenFOAM attempt and record its complete terminal command evidence.
---

# Runner

## 1. Entry Conditions

Use for a formal, smoke, diagnostic, resume, or rerun attempt after the required CaseSpec and formal-case validation are available.

## 2. Required Inputs

- `case_spec.json`;
- `workflow.json` with formal case path plus content, formal-input, mesh, and initial-state hashes;
- selected case path and attempt mode;
- declared preprocessing/solver command chain;
- runtime and parallel configuration;
- explicit modifications for non-formal attempts.

## 3. Decision Procedure

1. Resolve the selected case through the Workflow root and reject path traversal or symbolic-link escape.
2. For `formal` and `resume`, verify formal-input and mesh hashes against `workflow.json`; for `formal`, also verify the initial-state hash.
3. For `resume`, require a prior succeeded formal/resume record, a non-zero restart state, all required restart fields, and recorded restart provenance.
4. Require a separate case copy and explicit modification list for smoke/diagnostic attempts.
5. Discover the OpenFOAM runtime through the configured backend: Windows host → WSL, Linux/WSL session → native shell, unless `EASYFOAM_EXEC_BACKEND` explicitly selects a supported backend. Require runtime version 13 to match CaseSpec and Workflow.
6. Resolve a non-empty command chain. Formal/resume overrides require explicit approval and a recorded reason.
7. Create a collision-resistant `runs/<attempt_id>/` directory.
8. Execute commands in declared order and stop at the first non-zero return code.
9. Save each command's stdout/stderr and record argv, cwd, timestamps, elapsed time, and return code.
10. For formal/resume, verify that the declared terminal time or iteration is actually reached; a zero return code alone is insufficient.
11. Record command-chain state, terminal-contract state, restart provenance when applicable, first deterministic error, and runtime observations in one `run_record.json`.
12. Validate the run record before replacing any canonical file, then append its reference to `workflow.json`.

## 4. Output Contract

Each actual attempt creates only:

```text
runs/<attempt_id>/run_record.json
runs/<attempt_id>/<NN>-<command>.stdout.log
runs/<attempt_id>/<NN>-<command>.stderr.log
```

No separate command, runtime-metrics, hash-check, or attempt-manifest JSON is created.

## 5. Completion Conditions

A formal/resume attempt completes Run only when `run_record.json` is schema-valid, every declared command succeeds, and the formal terminal contract is verified. Smoke/diagnostic success records limited auxiliary evidence and never completes or reopens the formal Run stage. Execution success still does not establish numerical convergence, conservation, or physical validity.

## 6. Invariants

- Attempt directories are immutable and never overwritten.
- The formal case is not shortened or modified for diagnostic convenience.
- Non-formal modes remain explicitly labelled.
- The first deterministic failure is preserved.
- Absolute machine paths are not stored as canonical references.

## 7. Failure Routing

Failed commands route to `debug-reviewer`. Runtime/call corrections remain in Run. Any formal file, mesh, or planning change returns to Write or Plan before a new formal attempt.

## 8. Scripts

```text
scripts/run_openfoam.py
skills/workflow/scripts/workflow_ledger.py
```

`scripts/run_openfoam.py` writes run-record schema version `1.1`, validates `run_record.json` transactionally, records Run-scoped command-chain and formal-terminal evidence, and uses the ledger `advance` operation on formal success. The Workflow ledger performs both Schema and semantic scope/state validation before every `workflow.json` update.

## 9. Conditional References

| Execution need | References |
| --- | --- |
| Command ordering | `references/run-sequence-patterns.md` |
| Parallel execution | `references/parallel-run-patterns.md` |
| Restart/resume | `references/restart-resume-patterns.md` |
| Case-copy, path, command, and evidence safety | `references/safety-rules.md` |
| Module execution details | selected solver-module card |
