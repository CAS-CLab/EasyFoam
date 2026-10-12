# `snappyHexMesh` Planning and Audit Rules

Use for a prepared real surface/CAD representation when surface-based meshing is appropriate.

## Preconditions

- confirmed surface units, orientation, watertightness/open-edge expectations, and region names;
- a valid background mesh with sufficient extent and base resolution;
- feature extraction strategy where sharp edges matter;
- an internal location that is truly inside the retained fluid region;
- explicit patch/zone/interface targets.

## Stage reasoning

- **Castellation:** refinement regions, feature capture, cell retention, zone creation.
- **Snapping:** surface conformance without destroying topology or quality.
- **Layers:** near-wall resolution and coverage only when geometry, base mesh, and quality support them.

## Experience rules

- Excessive refinement does not repair bad surface topology.
- `locationInMesh` errors can retain the wrong side even when the command completes.
- Region names in the surface and dictionary must match intended patch names.
- Layer addition should be assessed for coverage, thickness, termination, and resulting quality; partial layers must not be assumed acceptable.
- Zone creation for MRF/porous/source models must be validated spatially and by count.
- Tune one cause at a time and retain command logs for actual meshing attempts.

## Completion

Require successful meshing, expected patches/zones, acceptable topology and quality, and visual confirmation of critical interfaces/refinement/layers.
