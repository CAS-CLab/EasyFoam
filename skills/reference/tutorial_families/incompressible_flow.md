# Tutorial Family: Incompressible Single-Phase Flow

## Use

Structural reference for `incompressibleFluid` cases when the active physics, algorithm and dictionary family match.

## Match dimensions

- steady SIMPLE or transient PISO/PIMPLE;
- laminar/RAS/LES treatment;
- internal/external flow and pressure-reference style;
- mesh and boundary topology;
- optional MRF, buoyancy or source features;
- requested probes/forces/sampling.

## Reusable structure

Module invocation, basic directory family, pressure–velocity algorithm layout, transport/momentum model placement, field header/dimension patterns, and utility ordering may be reusable after active-case verification.

## Never copy blindly

Geometry, patch/zone names, viscosity, turbulence model/coefficients, inlet/outlet values, relaxation/tolerances, timestep/end time, force reference values, mesh resolution or acceptance thresholds.

## Typical checks

Pressure/reference well-posedness, actual patch coverage, turbulence/wall treatment, schemes/solvers for active fields, mesh credibility, convergence/continuity and requested QoI stabilization.
