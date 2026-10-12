# Zone and Interface Contracts

Use whenever physics or coupling consumes cellZones, faceZones, patches, regions, cyclic pairs, AMI interfaces, overset zones, or porous/actuator selections.

## Required fields

For each entity record exact name, entity type, producer, consumer, expected location/extent, paired entity if any, coordinate system, and validation method.

## Common contracts

- **MRF:** rotating cellZone, origin, axis, angular speed and relative/absolute treatment.
- **cyclic/cyclicAMI:** two compatible boundary patches, pairing, transform/rotation relation, area/overlap credibility.
- **porous/source region:** cell selection, coefficient directions, dimensions, sign and normalization.
- **overset:** donor/acceptor region structure, interpolation zone and hole-cutting intent.
- **multi-region:** region boundaries and coupled interface ownership.

## Experience rules

- Similar names are not sufficient; exact dictionary references must exist in the mesh.
- A nonempty zone can still be spatially wrong.
- AMI command success does not prove adequate overlap or correct rotation mapping.
- Interface mesh types and field conditions must agree.
- Do not derive a missing rotating/porous zone name from common examples.

## Validation

Use mesh inventory, counts, spatial visualization, paired-area/overlap diagnostics where available, and static dictionary cross-reference before Run.
