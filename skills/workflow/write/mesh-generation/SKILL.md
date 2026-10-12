---
name: workflow-mesh-generation
description: Generate and verify a CaseSpec-defined OpenFOAM mesh from released geometry and mesh requirements.
---

# Mesh Generation

## 1. Entry Conditions

Use when `case_spec.json` selects generated `blockMesh`, `snappyHexMesh`, or a declared combined workflow. The required geometry source, units, patch roles, zones/interfaces, and dimensionality are resolved.

## 2. Required Inputs

- released geometry and mesh contracts;
- relative case path and user-provided surfaces when required;
- real surface/CAD files or complete simple parametric dimensions;
- expected patches, zones, interfaces, refinement and quality intent;
- QoI-sensitive regions and wall-treatment needs.

## 3. Decision Procedure

1. Select `blockMesh`, surface-based meshing, or a combined route according to geometry complexity and available geometry input.
2. Validate geometry scale, orientation, topology, regions, features, and dimensional semantics.
3. Define the domain, patches, interfaces, required zones, refinement, layers, and `locationInMesh` as applicable.
4. Execute only the required mesh utilities and retain logs for commands actually run.
5. Parse the generated patch and zone inventory, and assess `checkMesh` evidence when applicable.
6. Compare the resulting mesh with the CaseSpec. Return the accepted mesh inventory and evidence to Case Authoring, or report any contract or quality failure.


## 4. Output Contract

Modify only the required mesh dictionaries, user-scoped geometry copies/links, and `case/constant/polyMesh/`. Save stdout/stderr logs only for mesh commands actually executed. Return parsed inventory and quality results through stdout; do not create default mesh manifests or quality JSON files.

## 5. Completion Conditions

Pass when the method matches the geometry, required geometry entered the mesh, patches/zones and dimensionality are correct, generation commands completed, and required mesh-quality gates pass.

## 6. Invariants

- Missing named geometry is never replaced by a toy domain.
- Missing body patches or required zones are hard failures.
- Severe mesh defects are not hidden through numerical tuning.
- Patch names/types remain stable interfaces to fields.

## 7. Failure Routing

Incomplete geometry contracts return to Plan. Field mismatch after a valid mesh routes to `case-authoring`. Imported meshes route to `mesh-import`. Mesh generation or quality defects remain here.

## 8. Scripts

```text
scripts/validate_mesh_plan.py
scripts/validate_patch_inventory.py
scripts/parse_checkmesh.py
```

Scripts validate or summarize to stdout; command logs come from actual OpenFOAM utilities.

## 9. Conditional References

| Mesh decision | References |
| --- | --- |
| Simple structured geometry | `references/blockMesh-rules.md` |
| Surface-based mesh | `references/snappyHexMesh-rules.md`, `skills/reference/openfoam13/complex-geometry-policy.md` |
| Surface repair/features | `references/surface-feature-preparation.md` |
| MRF/cyclicAMI/porous/actuator zones and interfaces | `references/zone-interface-contracts.md` |
| Quality and resolution | `references/mesh-quality-rules.md`, `references/checkMesh-diagnosis.md` |
