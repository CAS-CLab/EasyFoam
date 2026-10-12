# Zones, Motion, Sources, and Constraints

Zone-dependent models are valid only when the mesh contains the exact named entities consumed by their dictionaries.

## Zone contracts

For each consumer record:

- dictionary/model type;
- exact cellZone, faceZone, patch, region, or cellSet name;
- geometry or selection method that creates it;
- expected location and membership;
- coordinate system, origin, axis, and direction where applicable;
- parameters, units, provenance, and active time range.

## Common consumers

- MRF and rotating frames;
- rigid/dynamic mesh motion and overset regions;
- cyclicAMI and other paired interfaces;
- porous resistance and distributed momentum sources;
- heat, mass, species, or body-force sources;
- actuator regions;
- `fvModels` and `fvConstraints`;
- monitoring or sampling zones.

## Experience rules

- Never assume a zone is named `rotor`.
- A patch is not a cellZone, and a faceZone is not a boundary patch.
- Creating a geometrically plausible zone is insufficient; verify that it selects the intended cells/faces.
- Axis/origin errors may run but produce physically wrong results, so they require explicit audit.
- Source sign, volume normalization, selection mode, and dimensions must be traceable.
- Only the OpenFOAM-13 syntax supported by the active model should be written; do not mix historical `fvOptions` syntax with v13 contracts without evidence.

## Static checks

Compare mesh inventories with every consuming dictionary, reject unresolved names, inspect selection size/location, and verify paired interfaces and region ownership before Run.
