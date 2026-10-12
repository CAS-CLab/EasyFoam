# Domain Sizing Rules

Domain size is a physics and boundary-interaction decision, not a universal constant.

## Inputs

Use body/feature bounds, characteristic length, inflow direction, expected wake/jet/plume development, confinement, blockage, symmetry, periodicity, and target QoIs.

## External-flow considerations

- Provide enough upstream distance for the prescribed inlet profile to remain meaningful at the body.
- Provide enough downstream distance for wakes, pressure recovery, and outlet conditions not to dominate the QoI.
- Provide lateral/top clearance to control blockage and artificial acceleration.
- Ground planes, moving walls, rotating wheels, symmetry, and wind-tunnel confinement change the domain contract.
- Force coefficients require explicit reference area/length independent of domain dimensions.

## Internal-flow considerations

- Preserve actual inlet/outlet development lengths when they matter to profiles or pressure loss.
- Use periodic/cyclic sectors only when geometry and physics are periodic.
- Include plenums, bends, contractions, rotating/stationary regions, and interfaces required by the physical model.
- Do not enlarge or truncate an internal passage solely to make meshing easier without recording the modeling change.

## Resolution link

Domain sizing and mesh resolution are coupled. A large domain with unchanged cell count can under-resolve the body or wake; a tight domain can produce acceptable cell size but invalid boundary influence.

## Recording

Store the actual domain bounds, reference axes, characteristic length, rationale, source, and known limitations. When a trusted geometry is unavailable, do not invent numerical extents merely to release Plan.
