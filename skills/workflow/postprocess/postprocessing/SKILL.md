---
name: workflow-postprocessing
description: Generate requested quantitative data, derived fields, tables, plots, exports, and reports from available OpenFOAM outputs.
---

# Postprocessing

## 1. Entry Conditions

Use when requested quantitative or derived outputs are not already available. Do not make final physical-credibility decisions.

## 2. Required Inputs

- CaseSpec output contracts;
- selected run record and available case fields/functionObject outputs;
- requested result names, formats, locations, and time ranges;
- required postprocessing/runtime capability.

## 3. Decision Procedure

1. Reuse valid existing outputs before rerunning utilities.
2. Select the smallest functionObject or `postProcess`/`foamPostProcess` operation needed.
3. Generate only requested residual histories, probes, forces, sampled data, derived fields, scalar/time-series plots, tables, or exports.
4. Preserve field/time provenance and units.
5. Distinguish formal-run data from smoke/diagnostic data.
6. Verify output existence and basic readability before handoff.
7. Generate a narrative/HTML/Markdown report only when explicitly requested.

## 4. Output Contract

Write only user-requested files under `results/` or a user-approved path. Raw utility logs are retained only for commands actually executed. Do not create generic postprocess manifests, metrics JSON, or reports by default.

## 5. Completion Conditions

Pass when every required quantitative output is available and traceable, or explicitly reported unavailable/blocked with its cause.

## 6. Invariants

- Derived data does not silently modify the formal case contract.
- Units, time selection, source attempt, and calculation method remain traceable.
- Missing fields are not fabricated.
- A plot does not replace the underlying quantitative evidence.

## 7. Failure Routing

Missing fields/functionObjects caused by case design return to Write. Incomplete execution returns to Run. Missing user validation target returns to Plan. Backend-only failure remains here or blocks the requested output.

## 8. Scripts

```text
scripts/render_workflow_report.py   # only when a report is requested
```

OpenFOAM utilities run through the active environment and retain actual command logs only.

## 9. Conditional References

| Requested product | References |
| --- | --- |
| Probes, forces, averages, integrals, derived fields | `references/functionObjects.md`, `references/quantitative-postprocessing-patterns.md` |
| Existing-time utility execution | `references/foamPostProcess.md` |
| VTK export | `references/foamToVTK.md` |
| Residual history | `references/residual-analysis.md` |
| Explicit report | `references/case-report-mapping.md` |

