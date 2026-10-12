# Complex Geometry and Mesh-Source Policy

## Complex geometry indicators

Treat named vehicles, aerofoils, pumps, turbines, blades, propellers, rotors, manifolds, biological anatomy, complex internal passages, STL/OBJ/CAD surfaces, and supplied industrial meshes as complex unless the user explicitly defines a simplified parametric surrogate.

## Required source

A complex-geometry claim requires one of:

- user-provided surface/CAD files;
- user-provided mesh;
- a named existing case whose geometry/mesh may be reused;
- a user-approved, explicitly described parametric surrogate.

Do not generate a box or cylinder and claim it represents a missing named geometry.

## Required planning metadata

Record available units, scale, bounds, reference axes, body kind, source paths, expected patches, moving/rotating regions, periodic interfaces, and QoI-relevant locations.

## Mesh route

- simple structured domains may use `blockMesh`;
- surface-based geometry commonly requires background mesh, feature preparation, `snappyHexMesh`, and patch/zone verification;
- external meshes require converter, scale, orientation, patch/zone mapping, and provenance;
- existing `polyMesh` requires consistency and quality audit before reuse.

Missing decisive source data blocks Write.
