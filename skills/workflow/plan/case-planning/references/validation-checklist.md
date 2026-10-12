# CaseSpec Semantic Release Checklist

Use after Schema validation and before Plan handoff.

## Requirement fidelity

- Exact requirement preserved and every explicit request mapped.
- Units and conversions traceable.
- Contradictions and missing decisive information visible.
- No user-explicit formal control silently changed.

## Physics and solver

- Phase, compressibility, energy/species/reaction, time behavior, turbulence, motion, and sources are mutually consistent.
- Selected OpenFOAM-13 module/application supports the contract.
- Algorithm, dictionary family, fields, and run command agree.

## Geometry and mesh

- Real geometry/mesh source exists for complex named systems.
- Units, axes, bounds, patch roles, zones, and interfaces are explicit where required.
- Mesh route and preprocessing commands are feasible.

## Fields, boundaries, and models

- Actual solved/model fields identified.
- Every required field has a condition on every expected patch.
- Pressure/reference, energy, phase, species, turbulence, wall, and interface semantics are complete.
- Required material/model values and exact names are resolved.

## Controls and outputs

- Start/restart, end, timestep/Courant, write, parallel, and functionObject contracts are complete.
- QoI methods and decisive parameters are executable.
- Validation and visual requests identify required evidence without invented thresholds.

## Release outcome

Release only when all blocking review items are closed. Otherwise preserve a schema-valid blocked CaseSpec and state the precise next user/reference decision.
