---
name: workflow-postprocess
description: Coordinate requested data products, visual evidence, validation, and final evidence synthesis.
---

# Postprocess

Postprocess turns available case and run evidence into bounded engineering claims. It does not upgrade missing evidence into PASS.

## 1. Preconditions

Use `case_spec.json`, `workflow.json`, selected run records and logs, available fields/mesh, and the requested output and validation contracts.

## 2. Specialist Routing

| Need | Specialist |
| --- | --- |
| Generate quantitative data, derived fields, tables, plots, exports, or a requested report | `workflow/postprocess/postprocessing` |
| Generate and verify mesh views, contours, slices, vectors, streamlines, or temporal visuals | `workflow/postprocess/visual-diagnostics` |
| Assess requirement, case, mesh, execution, numerical, physical, conservation, and QoI credibility; write the final summary | `workflow/postprocess/physics-validation` |

`physics-validation` is the sole writer of `evidence_summary.json`.

## 3. Orchestration

1. Determine the requested quantitative, visual, and validation outputs.
2. Invoke `postprocessing` for required data and derived quantities.
3. Invoke `visual-diagnostics` for requested visual evidence.
4. Invoke `physics-validation` after evidence is available or explicitly unavailable.
5. Record `evidence_summary.json` and requested output references in `workflow.json`.

## 4. Stage Result

Postprocess creates only `evidence_summary.json` and user-requested result files. It does not create default metrics, visual-contract, visual-manifest, or generic report files.

Postprocess completes only when the overall evidence result is `passed` and `evidence_summary.json` is schema-valid. A `limited` result keeps Postprocess `in_progress`; a `failed` or `blocked` result terminates the requested Workflow outcome without adding Postprocess to `completed_scope`.

## 5. Failure and Return Routing

Missing fields or function objects caused by case design return to Write. Incomplete execution returns to Run. Mesh credibility defects return to the applicable Write mesh specialist. Missing validation targets return to Plan.
