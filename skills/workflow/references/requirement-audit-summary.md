# Requirement Audit and Summary

Before authoring or running a case, compare the user requirement with OpenFOAM-13 capabilities, solver/module choice, fields, physics assumptions, and available case data.

Record the audit in the final case summary. Do not hide corrections as implementation details.

## Required Audit Items

- `stated_requirement`: compact copy of the user goal.
- `detected_issues`: contradictions, impossible requests, outdated solver names, missing boundary data, missing material properties, missing geometry, missing turbulence/thermo model details, or unsupported requested outputs.
- `resolved_settings`: values actually used for solver/module, physics model, material properties, numerics, mesh assumptions, post-processing, and visualization.
- `assumptions`: values chosen because the prompt was incomplete.
- `deviations_from_request`: anything intentionally changed from the prompt, with reason.
- `unresolved_items`: items not fixed and why they do not block the current run, or why they remain a blocker.

## Examples

- If the prompt says `Ma=0.5` and `incompressibleFluid`, record that Mach is treated as a reference condition only unless a compressible module is selected.
- If the prompt names a legacy solver, record the OpenFOAM-13 `foamRun -solver <module>` mapping or the confirmed legacy application actually used.
- If boundary conditions, dimensions, mesh resolution, reference values, or turbulence constants are missing, record the chosen defaults.
- If requested visual outputs need fields that are absent, record the required functionObject or native post-processing used to generate them.

## Canonical Mapping

Requirement audit information is stored in:

- `case_spec.json.requirement_fidelity`;
- `case_spec.json.assumptions`;
- `case_spec.json.review_required`;
- the final requirement assessment and limitations in `evidence_summary.json`.

Do not create `workflow_summary.json` or `workflow_summary.md` by default. A human-readable report may be generated only when explicitly requested and remains a presentation artifact rather than canonical state.
