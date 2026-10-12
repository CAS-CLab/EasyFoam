# `checkMesh` Diagnosis

Read `checkMesh` as structured evidence rather than a single pass/fail phrase.

## Diagnosis order

1. Confirm the command ran on the intended mesh/region.
2. Check dimensionality, bounds, cell/face/point counts and region count.
3. Check topology and geometry fatal errors.
4. Confirm required patches, coupled pairs, cellZones and faceZones.
5. Inspect quality metrics and where problematic cells are located.
6. Relate the findings to solver, schemes, wall/interface treatment, and QoIs.

## Outcome mapping

- `failed`: fatal topology/geometry, negative volume, missing required entity, invalid region/interface.
- `limited`: command passes but material quality/resolution concerns remain.
- `passed`: required topology/entities pass and no unresolved quality concern blocks intended claims.
- `not_assessed`: no valid output for the intended mesh.

## Common mistakes

Do not treat the final “OK” line alone as proof of resolution, layer quality, AMI credibility, wall treatment, or physical validity. Do not suppress errors through tolerance changes without understanding the geometry.
