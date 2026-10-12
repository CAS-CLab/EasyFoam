---
name: workflow-debug-reviewer
description: Diagnose failed OpenFOAM commands or runtime states, verify the smallest repair, and route it to the earliest affected stage.
---

# Debug Reviewer

## 1. Entry Conditions

Use only after a preprocessing/solver command failed or a concrete invalid runtime state was recorded in `run_record.json` or its logs.

## 2. Required Inputs

- failed run record and logs;
- current formal case and CaseSpec;
- formal case hash and any controlled diagnostic copy;
- error-specific References selected after the first failure is known.

## 3. Decision Procedure

1. Identify the first deterministic error.
2. Classify the cause as requirement, case file/model/numerics, mesh, runtime invocation/environment, or postprocessing dependency.
3. Establish the smallest supported root-cause hypothesis from logs and case evidence.
4. Verify a minimal repair in a controlled diagnostic copy when possible.
5. Verify with the narrowest command that reproduces the original defect.
6. Route verified formal changes to Plan or Write for authoritative application and revalidation.
7. Keep command-only/environment-only corrections in Run.
8. Preserve the failed run record; do not rewrite it after repair.

## 4. Output Contract

Return the failure classification, root cause, repair scope, verification result, and earliest affected stage through stdout and update only `workflow.json` next action/blocker. Save a patch/diff only when a formal file changed and auditability requires it. Create an Experience record only after verification and only when passive capture is retained.

Do not create default failure-signature, fix-record, or verification JSON files.

## 5. Completion Conditions

Pass when the root cause is evidence-supported, the smallest repair is verified or explicitly blocked, and the earliest affected stage is unambiguous.

## 6. Invariants

- Fix the first deterministic cause, not its symptoms.
- Do not tune numerics to mask mesh/physics/file defects.
- A diagnostic-copy repair is not a formal repair until reapplied and revalidated by the owning stage.
- Failed evidence remains immutable.
- Injected faults are not eligible as natural Experience.

## 7. Failure Routing

Requirement decisions → Plan. Formal files/models/numerics or mesh → Write. Invocation/environment/restart-only changes → Run. Missing derived data after a completed run → Postprocess.

## 8. Scripts

```text
scripts/parse_openfoam_log.py
scripts/create_fix_record.py          # reads the failure log; stdout by default, optional --out only when audit persistence is requested
scripts/verify_case_fix.py
```

## 9. Conditional References

Load `references/common-errors.md` first, then one primary card:

| Evidence | Reference |
| --- | --- |
| Parser/keyword/dictionary/model error | `references/dictionary-errors.md`, selected solver-module card |
| Patch/field/zone/interface mismatch | `references/patch-field-errors.md` |
| Timestep/boundedness/scheme/relaxation instability | `references/numerical-stability.md` |
| Residual or equation divergence after static checks | `references/solver-divergence.md` |
| Runtime/bootstrap/MPI/path/permission/command issue | `references/environment-command-errors.md` |
