---
name: workflow-case-authoring
description: Materialize and audit OpenFOAM-13 fields, dictionaries, models, numerics, and controls against the released CaseSpec and actual mesh inventory.
---
# Case Authoring

## 1. Entry Conditions

Use only after the CaseSpec passes both Schema and semantic release checks and after the actual mesh patch/zone inventory is known or explicitly deferred by the CaseSpec. Do not redesign decisive requirements.

## 2. Required Inputs

- released `case_spec.json`;
- relative formal case path;
- actual patch and zone inventory from mesh generation/import/reuse;
- selected module/field/dictionary References.
- user-provided files that must be preserved.

## 3. Decision Procedure

1. Create or update only the required `0/`, `constant/`, and `system/` files from CaseSpec and module.
2. Ensure every required solved field exists with correct dimensions, internal field, and boundary entry for every actual patch.
3. Preserve specialized patch semantics (`empty`, `wedge`, `symmetryPlane`, `cyclic`, `cyclicAMI`, `walls`, `interfaces`, etc.).
4. Write transport, thermophysical, turbulence, phase, MRF, gravity, source, and constraint dictionaries required by the selected module and physics.
5. Reconcile exact zone/interface/model names with consuming dictionaries.
6. Write `fvSchemes` for every active equation and field family.
7. Write `fvSolution` with compatible linear solvers, Final entries, and exactly the applicable algorithm controls.
8. Preserve formal `controlDict` time/output/functionObject contracts; do not shorten or replace them for convenience.
9. Check required function objects only when they are necessary for requested outputs and cannot be added safely after the run.
10. Re-run the CaseSpec semantic release gate before static case checks. Validate structure and algorithm contract, compute the formal case hash, then atomically advance Workflow from Write.

## 4. Output Contract

Modify the formal `case/` tree and `workflow.json`. Do not create structure, hash, first-generation, or model manifest JSON files. Static checks print to stdout; actual utility logs are kept only if commands run.

## 5. Completion Conditions

For the current automated single-region gate, pass when required files exist, actual patch/zone contracts match, required fields cover the actual patch inventory, the applicable algorithm block is present, no placeholder remains, and formal content/input/mesh/initial-state hashes are recorded. Model, dictionary, dimensional, numerical, and OpenFOAM-13 module compatibility remain specialist-reviewed until dedicated validators cover them.

## 6. Invariants

- Case files implement the released CaseSpec; they do not silently revise it.
- Mesh patch/zone inventory is authoritative for field materialization.
- No generic energy/phase/species field placeholders.
- Missing model/field/solver entries are repaired explicitly, not hidden.
- Numerical tuning does not mask mesh, boundary, or model defects.
- Formal controls are not shortened automatically.


## 7. Failure Routing

Requirement ambiguity returns to Plan. Patch/zone/topology defects return to the active mesh specialist. Dictionary, field, model, algorithm, or control defects remain here. Any formal case change after a run requires revalidation and a new hash.

## 8. Scripts

```text
scripts/check_case_structure.py
scripts/validate_algorithm_contract.py
scripts/validate_and_hash_case.py
```

`scripts/validate_and_hash_case.py` first reuses the CaseSpec semantic release checks, then performs the implemented single-region structural inventory, patch/zone/field coverage, algorithm-block, placeholder, and hashing gates before updating `workflow.json` through the ledger `advance` operation. It does not author missing files and does not by itself prove full model or numerical compatibility.


## 9. Conditional References

| Authoring decision | References |
| --- | --- |
| Required files and directory family | `references/case-file-structure-v13.md`, selected solver-module card |
| Field class, dimensions, actual names, patch coverage | `references/field-file-patterns.md` |
| Boundary compatibility | `references/boundary-condition-patterns.md` |
| Physical/model dictionaries | `references/physical-model-dictionaries-v13.md`, selected solver-module card |
| Zones, MRF, motion, sources, constraints | `references/zones-motion-and-sources.md` |
| Discretization | `references/fvSchemes-patterns.md` |
| Linear solvers and algorithm controls | `references/fvSolution-patterns.md` |
| Formal run/functionObject controls | `references/controlDict-patterns.md` |
| Final consistency | `skills/reference/openfoam13/consistency_audit.md` |
