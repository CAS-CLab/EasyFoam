# Geometry and Mesh-Source Classifier

Use before selecting mesh generation or import.

## Geometry classes

| Class | Appropriate route | Key evidence |
| --- | --- | --- |
| Simple parametric domain | generated mesh, often `blockMesh` | complete dimensions, axes, patch topology |
| Complex surface/CAD | surface preparation plus surface-based meshing | real surface files, units, watertightness, region names |
| External mesh | mesh import | source format, units, coordinate frame, patch/zone mapping |
| Existing case/polyMesh | reuse or audit | actual boundary/zone inventory and provenance |
| Unspecified | blocked when geometry is decisive | user artifact or approved source required |

## Complex-geometry triggers

Named vehicles, aerofoils, pumps, fans, impellers, turbines, rotors, propellers, anatomical structures, buildings, complex internals, STL/OBJ/CAD, and supplied meshes are not represented faithfully by an empty box. `blockMesh` may create a background domain but not the named body unless the geometry is genuinely block-constructible and explicitly approved.

## Required geometry contract

Capture when applicable:

- source type and relative reference;
- units and scaling;
- coordinate frame, streamwise/normal/spanwise axes;
- characteristic lengths and reference area/length;
- bounds and intended domain clearances;
- solid/fluid region interpretation;
- expected boundary region names;
- required cellZones/faceZones/interfaces;
- geometry limitations and provenance.

## Fail-fast rules

- Missing complex geometry/mesh source is blocking.
- Unknown units or orientation are blocking when they affect dimensions or BC directions.
- Do not synthesize a look-alike geometry unless the user explicitly requests a synthetic demonstration and the limitation is preserved.
- Do not infer patch or zone names from a domain stereotype.
- A valid surface file does not prove a valid volume mesh; surface and mesh evidence are separate.
