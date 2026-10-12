---
name: reference
description: Read-only router for versioned OpenFOAM-13, CFD, and Evolution governance References.
---

# Reference

Reference provides versioned, read-only knowledge to Workflow and Evolution. It does not plan a case, modify files, execute commands, update canonical state, or change formal Skills.

## 1. Scope

Use Reference only for a concrete unresolved decision involving:

- OpenFOAM-13 modules, applications, fields, dictionaries, utilities, and runtime behavior;
- physical models, material properties, boundary conditions, numerics, mesh, zones, and interfaces;
- QoIs, validation, postprocessing, visualization, and claim boundaries;
- tutorial-family structure and compatibility evidence;
- Experience eligibility, Candidate scope, validation evidence, promotion, retention, and rollback governance.

Reference must not contain case answers, hidden target configurations, or evaluation-specific shortcuts.

## 2. Required Inputs

Provide the specific decision question, relevant CaseSpec or active artifact context, target OpenFOAM version, and explicit user constraints. Load only the narrowest applicable card.

## 3. Routing

| Decision need | Route |
| --- | --- |
| Version-specific case, dictionary, model, mesh, runtime, or consistency knowledge | `openfoam13/` |
| Solver module, field family, algorithm, and dictionary compatibility | `solver_modules/` |
| Reusable tutorial-family structure | `tutorial_families/` |
| Indexed local tutorial patterns | `tutorial_patterns/` |
| Evolution artifact, evidence, scope, decision, retention, or rollback governance | `evolution/` |

The active specialist records accepted decisions and provenance in its owned artifact. Reference itself writes nothing.

## 4. Use Rules

1. Bind the query to one decision.
2. Select the narrowest version-compatible card.
3. Check applicability against physics, module, case state, and user constraints.
4. Use the card as evidence, not as an automatic answer.
5. Record the accepted decision, source path, rationale, and limitations in the calling specialist's artifact.

Tutorials and patterns provide structural evidence only. They do not override explicit requirements or justify copying an unrelated case.

## 5. Invariants

- Read-only during Workflow.
- Relative paths or stable logical identifiers only.
- No machine-specific paths, temporary runs, or private case data as formal Reference.
- No unsupported defaults for decisive physics, geometry, boundaries, materials, solver choices, or acceptance thresholds.
- Missing evidence remains `review_required` or `blocked` when decisive.
- Reference changes require explicit Evolution.

## 6. Scripts

None. Search, validation, artifact updates, and execution belong to the calling specialist.
