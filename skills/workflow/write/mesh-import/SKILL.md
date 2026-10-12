---
name: workflow-mesh-import
description: Import, convert, map, and audit a user-provided mesh or existing polyMesh while preserving provenance and topology.
---

# Mesh Import

## 1. Entry Conditions

Use when the CaseSpec selects `import` or `reuse`, or the user supplies a mesh, converter input, or existing `constant/polyMesh`.

## 2. Required Inputs

- relative source reference and declared format;
- source format, units, coordinate frame, dimensionality, provenance;
- released patch/zone/dimensionality contract;
- relative case path;
- selected converter/runtime capability and the exact executable conversion command when conversion is required.

## 3. Decision Procedure

1. Verify that the source is user-scoped, accessible, and represented by a portable reference.
2. Confirm the source format, exact converter command, converter availability, and explicit scaling/orientation. A placeholder such as `<converter>` is not executable and must remain a blocking Plan item.
3. Inspect scale, orientation, dimensionality, boundary types, and cell/face/point zones.
4. Inspect actual inventory and compare with CaseSpec.
5. Preserve specialized patch and rotating/interface semantics.
6. Run `checkMesh` when required and available.
7. Return the accepted actual inventory to `case-authoring`.

## 4. Output Contract

Modify `case/constant/polyMesh/` and only the mapping files required for the import. Save raw converter/checkMesh logs only when commands are executed. Inventory and contract validators print to stdout; optional `--out` is used only when the user explicitly requests a retained import audit.

## 5. Completion Conditions

Pass when source provenance/transformations are known, conversion/reuse succeeds, required patches/zones/interfaces are preserved or explicitly mapped, and blocking mesh defects are absent.

## 6. Invariants

- Source topology and provenance are preserved.
- Zones are not silently deleted or merged.
- Failed import is not replaced by blockMesh.
- Converter success alone does not prove mesh credibility.
- Preserve interface and zone metadata required by physics.

## 7. Failure Routing

Missing source/capability is blocked here. Unknown geometry scale or intended semantics returns to Plan. Mapping/topology/quality defects remain here. Valid mesh with field mismatch routes to `case-authoring`.

## 8. Scripts

```text
scripts/validate_import_contract.py
scripts/summarize_import_inventory.py
```

Converter and `checkMesh` commands are executed through the Run environment and retain only actual logs.

## 9. Conditional References

- `references/external-mesh-import.md` for provenance, scale, mapping, and acceptance;
- `references/mesh-format-conversion.md` for converter selection and information-loss risks;
- `../mesh-generation/references/zone-interface-contracts.md` for zones/interfaces;
- `../mesh-generation/references/mesh-quality-rules.md` and `../mesh-generation/references/checkMesh-diagnosis.md` for quality;
- `skills/reference/openfoam13/complex-geometry-policy.md` for named complex systems.
