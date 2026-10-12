---
name: workflow-physics-validation
description: Assess requirement, case, mesh, execution, numerical, physical, QoI, and visual evidence and write the final evidence summary.
---

# Physics Validation

## 1. Entry Conditions

Use after the relevant quantitative and visual evidence is available or explicitly unavailable. This Skill is the sole writer of `evidence_summary.json`.

## 2. Required Inputs

- schema-valid CaseSpec, Workflow, selected run record(s), and logs;
- formal case/mesh evidence;
- residual, timestep, boundedness, conservation, physical, QoI, and visual evidence applicable to requested claims;
- stated criteria or comparison sources.
- explicit limitations and unavailable evidence.

## 3. Decision Procedure

1. Validate canonical input artifacts against their Schemas.
2. Assess requirement fidelity and formal case contract separately.
3. Assess mesh topology, required patches/zones, quality, and resolution.
4. Assess formal execution terminal evidence.
5. Assess residual/monitored/timestep/boundedness/conservation behavior appropriate to steady/transient intent.
6. Assess problem-specific physical principles and comparisons.
7. Evaluate each requested QoI with method, unit, criterion, status basis, and evidence.
8. Assess requested visuals only for availability/provenance and interpretive purpose.
9. Do not mark a QoI PASS merely because a value exists.
10. Treat mesh credibility as a prerequisite for mesh-sensitive numerical, physical, and QoI claims.
11. Select the highest cumulative supported claim and write the final summary.

## 4. Output Contract

Write only:

```text
evidence_summary.json
workflow.json  # final reference/status update with Postprocess-scoped evidence
```

Metric extractors default to stdout. No separate validation, conservation, residual, mesh, or QoI manifest is generated unless the user explicitly requests a report.

## 5. Completion Conditions

Pass only when all required assessment categories and QoIs are represented with evidence-supported `passed` or `not_applicable` outcomes, required outputs are available or legitimately not applicable, claim boundaries are respected, and `evidence_summary.json` validates. A `limited` result remains in progress; `failed` or `blocked` does not complete the Postprocess stage.

## 6. Invariants

- File correctness, execution, numerical credibility, physical credibility, and QoI acceptance are distinct.
- Smoke/diagnostic runs cannot support formal convergence claims.
- Final residual values alone do not establish convergence.
- Visuals do not replace conservation or quantitative QoI checks.
- Missing evidence never becomes PASS.
- A single mesh does not prove mesh independence.
- Visual reasonableness is not physical validation.

## 7. Failure Routing

Requirement target gaps → Plan. Case/mesh contract defects → Write. Incomplete/failed formal execution → Run. Missing derived data with available fields → `postprocessing`. Missing visual output → `visual-diagnostics`. Otherwise record limited/blocked/failed evidence.

## 8. Scripts

```text
scripts/extract_runtime_metrics.py
scripts/extract_residuals.py
scripts/extract_mesh_metrics.py
scripts/evaluate_qois.py
scripts/build_evidence_summary.py
```

`scripts/build_evidence_summary.py` writes evidence-summary schema version `2.1`, validates Workflow schema version `2.2`, `case_spec.json`, available `run_record.json`, and final `evidence_summary.json`, then updates Workflow through the central ledger. Experience capture is handed to `skills/evolution/case-specific-fix/SKILL.md`; this Skill does not write Experience directly.

## 9. Conditional References

| Assessment | References |
| --- | --- |
| Cumulative claim ordering | `references/claim-levels.md` |
| Residual and steady/transient convergence | `references/residual-and-convergence.md` |
| Mass/energy/phase/species conservation and bounds | `references/conservation-and-boundedness.md` |
| QoI method, criterion, and comparison | `references/qoi-validation.md` |
| Problem-specific physical credibility | `references/physical-credibility.md`, selected solver/tutorial-family card |
| Resolution and mesh independence | `references/mesh-independence.md` |
