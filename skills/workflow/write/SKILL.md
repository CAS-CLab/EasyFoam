---
name: workflow-write
description: Coordinate mesh preparation and formal OpenFOAM case authoring.
---

# Write

Write materializes the released CaseSpec as one formal OpenFOAM case. It does not execute the requested solver run.

## 1. Preconditions

Require a released `case_spec.json`, the user-scoped geometry or mesh inputs it references, and a writable relative case path.

## 2. Specialist Routing

| Need | Specialist |
| --- | --- |
| Generate a mesh from declared geometry | `workflow/write/mesh-generation` |
| Import, convert, map, or inspect an external/existing mesh | `workflow/write/mesh-import` |
| Write and audit fields, dictionaries, models, numerics, and controls | `workflow/write/case-authoring` |

Mesh specialists own the actual patch and zone inventory. `case-authoring` consumes that inventory and makes fields and dictionaries consistent with it.

## 3. Orchestration

1. Verify both CaseSpec Schema validity and the semantic release gate; a schema-valid but blocked CaseSpec is not released.
2. Route to the applicable mesh specialist when mesh work is required.
3. Pass the accepted actual mesh inventory to `case-authoring`.
4. Validate the formal case against the CaseSpec.
5. Record the formal case path, content hash, optional mesh hash, and decisive validation evidence in `workflow.json`.

## 4. Stage Result

Write modifies the formal `case/` tree and `workflow.json`. It does not create default mesh, import, hash, or first-generation manifest JSON files. Command logs are retained only when mesh utilities or validators are actually executed.

Write succeeds when the applicable mesh contract and case-authoring contract pass and the formal case hash is recorded.

## 5. Failure and Return Routing

Requirement gaps return to Plan. Mesh defects remain with the active mesh specialist. Field, dictionary, model, numerical, or control defects remain with `case-authoring`. A formal case change after Run requires Write revalidation before another formal attempt.
