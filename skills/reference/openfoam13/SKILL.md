---
name: reference-openfoam13
description: Read-only router for OpenFOAM Foundation v13 case, module, dictionary, mesh, runtime, and validation knowledge.
---

# OpenFOAM-13 Reference

Use this router for one version-specific case or runtime decision. Custom OpenFOAM C++ development is outside the current library scope.

## Routing

| Decision | Reference |
| --- | --- |
| Requirement clarification and non-guessable information | `clarification_policy.md` |
| Allowed non-decisive defaults and provenance | `defaults.md` |
| CaseSpec semantics and release | `case_spec.md` |
| Cross-file and cross-stage consistency | `consistency_audit.md` |
| Solver module and legacy mapping | `solver-module-map.md`, then `../solver_modules/<module>.md` |
| Complex geometry and real mesh-source policy | `complex-geometry-policy.md` |
| Tutorial-family structure | `../tutorial_families/`, `../tutorial_patterns/` |
| Specialist-specific fields, models, boundaries, mesh, numerics, run, and validation | the active specialist's listed decision cards |

## Use Boundaries

- Prefer the selected solver-module card over generic examples.
- Confirm OpenFOAM Foundation v13 names from the local runtime or official local installation when a name is uncertain.
- Do not infer actual energy, phase, or species field names from a broad module family alone.
- Do not treat successful parsing as physical compatibility.
- Do not load unrelated cards or source-development material for ordinary case execution.
