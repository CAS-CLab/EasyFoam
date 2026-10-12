# External Mesh Import Contract

Importing preserves a user-provided mesh while converting it into a verified OpenFOAM case mesh.

## Required inputs

- source format/file and provenance;
- source units and required scale;
- coordinate frame/orientation and dimensionality;
- source region/zone/boundary inventory;
- desired OpenFOAM patch types and names;
- required cellZones/faceZones/interfaces;
- converter availability in the active environment.

## Procedure principles

1. Preserve an immutable source copy.
2. Run the narrowest supported converter with explicit scale/options.
3. Inspect actual imported patches, regions and zones.
4. Map names/types deliberately; do not rely on converter defaults silently.
5. Verify orientation, bounds and physical size.
6. Run `checkMesh` and inspect critical regions visually.
7. Reconcile the imported inventory with fields and model dictionaries.

## Failure experience

Common issues include wrong unit scale, flipped axes, collapsed 2D thickness, generic patch names, missing volume zones, non-manifold or duplicate entities, unsupported high-order elements, and boundary groups converted into internal faces. A converter exit code alone is not acceptance.
