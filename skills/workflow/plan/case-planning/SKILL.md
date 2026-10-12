---
name: workflow-case-planning
description: Build, revise, reconstruct, and semantically audit a provenance-aware OpenFOAM-13 CaseSpec from the user-scoped requirement and evidence.
---

# Case Planning

## 1. Entry Conditions

Use for a new simulation, a CaseSpec revision/audit, or reconstruction of a missing CaseSpec for a user-scoped existing case. Do not write case files or execute OpenFOAM.

## 2. Required Inputs

- the current natural-language user requirement or a user-provided requirement TXT path;
- case ID and relative run root;
- target OpenFOAM version, normally Foundation v13;
- optional user geometry, mesh, existing-case, material, or output references;
- optional prior `case_spec.json` when revising;
- bounded Reference evidence returned by `tutorial-retrieval` or `reference/SKILL.md`.

## 3. Decision Procedure

### A. Parse and preserve requirements

1. Bind the exact current user requirement or read the user-provided TXT without copying or modifying it; preserve UTF-8 text and provenance.
2. Extract all explicit physics, geometry, mesh, boundary, material, solver, control, output, and validation requirements.
3. Record each value with unit, source, and SI form when clear.
4. Map each item to CaseSpec or mark as missing, conflicting, deferred, or not applicable.
5. Do not assume missing decisive information.

### B. Classify the CFD problem in fixed order

1. phase regime: single-phase or multiphase;
2. compressibility: incompressible, low-Mach, or compressible;
3. coupling: energy, species, reaction, etc.
4. time: steady or transient
5. turbulence: laminar, RAS, LES, DNS, or unresolved;
6. motion: static, MRF, moving mesh, overset, rigid-body motion, etc.
7. sources: gravity, buoyancy, surface tension, etc.
8. geometry and mesh type

Do not replace classification with solver names.

### C. Define OpenFOAM execution setup

1. Use user-specified OpenFOAM-13 module if valid.
2. Map legacy solvers only with verified support.
3. Determine algorithm (SIMPLE, PISO, PIMPLE) from physics, time behavior, and references.
4. Record module, solver, algorithm, and evidence separately.
5. If multiple valid choices affect results, mark as blocking.

### D. Resolve geometry and mesh route

1. Classify geometry as simple parametric, complex surface/CAD, external mesh, existing case, or unspecified.
2. Use `blockMesh` only for genuinely simple structured domains or a user-approved background domain.
3. Complex systems require real geometry or mesh input.
4. Record units, characteristic length, bounds, reference axes, body kind, expected patches, and required zones when available.
5. Ensure required zones for MRF, AMI, porous, etc.
6. Missing complex geometry or mesh input is blocking; never replace it with a box and claim the named system was modeled.

### E. Define fields, boundaries, and models

1. Identify all required fields.
2. Define patch types and roles.
3. Assign boundary conditions for each field on each patch.
4. Preserve special patch types ( `empty`, `wedge`, `cyclic`,etc.).
5. Ensure consistency across fields and dimensions.
6. Record material and model properties.
7. Keep simulationType separate from turbulence model.
8. Preserve units and sources.
9. Do not invent key values.


### F. Define execution controls

Include:

* preprocessing steps
* solver command
* start/restart settings
* end time or iterations
* timestep and control
* Courant limits
* output control
* parallel settings

User-defined values are mandatory. Defaults allowed only if non-critical and justified. Missing critical controls are blocking.

### G. Define outputs and validation

1. Convert outputs into QoIs and postprocessing tasks when applicable.
2. Define validation checks (numerical, physical, visual).
3. Preserve user acceptance criteria.
4. Do not invent thresholds; flag uncertain ones.
5. Clearly state limits of validation claims.

### H. Build and release CaseSpec
1. Generate `case_spec.json` per case.
2. Validate schema compliance.
3. Perform semantic checks:
    * missing critical data
    * solver-physics mismatch
    * algorithm consistency
    * field and patch completeness
    * geometry and mesh validity
    * zone availability
    * execution completeness
    * output feasibility
4. Set review status based on semantic results.
5. When blocking review items remain:
   - consolidate related items into the minimum set of concrete user questions;
   - ask only for information the user must authoritatively decide or provide;
   - do not ask for deterministic OpenFOAM implementation details that the responsible specialist can derive from released physics and Reference evidence;
   - preserve the blocked CaseSpec and stop before Write;
   - after the user replies, revise the same CaseSpec, resolve the corresponding review items, rerun schema and semantic validation, and ask again only if decisive ambiguity remains.
6. Release only if no blocking issues remain; otherwise stop with clear reasons.

## 4. Output Contract

Write only:

```text
case_spec.json
workflow.json 
```
Parser and audit results default to stdout. Do not generate parsed-requirement, requirement-audit, selection, or planning-report JSON files. Persist a separate planning report only when the user explicitly requests one.

## 5. Completion Conditions

Pass only when `case_spec.json` is schema-valid, all decisive requirements are resolved, solver/physics/algorithm and field/patch contracts are compatible, required geometry/mesh inputs and zones are available, and formal controls and requested evidence are feasible. Otherwise return an explicit blocker and keep Plan unreleased.

## 6. Invariants

- Decisive CFD information is never guessed.
- User values override Reference defaults.
- Schema validity does not equal semantic release.
- Never invent decisive physics, geometry, boundary, material, model, solver, control, QoI method, or acceptance threshold.
- A tutorial pattern is evidence, not a production case.
- Actual names required by dictionaries or mesh are not generic placeholders.

## 7. Failure Routing

Missing/contradictory decisive information remains in Plan. Unsupported OpenFOAM capability is blocked or returned for user choice. Existing-case structural defects discovered during reconstruction route to Write only after a releasable CaseSpec exists.

## 8. Scripts

```text
scripts/parse_requirement.py      # candidate observations to stdout
scripts/audit_requirement.py      # requirement mapping/audit to stdout
scripts/build_case_spec.py        # writes case_spec.json
scripts/validate_case_spec.py     # schema + semantic release check
```

`scripts/build_case_spec.py` accepts either `--requirement-text` or `--requirement-file` and writes schema version `1.2`; `scripts/validate_case_spec.py` calls `schemas/case_spec.schema.json` through `skills/_shared/scripts/schema_validate.py`.

## 9. Conditional References

| Decision | References |
| --- | --- |
| Missing, contradictory, or non-guessable information | `skills/reference/openfoam13/clarification_policy.md`, `skills/reference/openfoam13/defaults.md` |
| Physics classification | `references/physics-taxonomy.md` |
| Module, legacy mapping, algorithm, dictionary family | `references/solver-selection-v13.md`, `skills/reference/openfoam13/solver-module-map.md`, selected `skills/reference/solver_modules/<module>.md` |
| Geometry and mesh route | `references/geometry-classifier.md`, `references/domain-sizing-rules.md`, `skills/reference/openfoam13/complex-geometry-policy.md` |
| Fields, boundaries, models, patches, zones | `references/field-model-contracts.md`, selected solver-module card |
| Formal controls | `references/run-control-contracts.md` |
| QoI, validation, and visual intent | `references/output-validation-contracts.md` |
| CaseSpec fields and release audit | `references/case-plan-schema.md`, `references/validation-checklist.md`, `skills/reference/openfoam13/consistency_audit.md` |

Load only cards needed for the unresolved decision.
