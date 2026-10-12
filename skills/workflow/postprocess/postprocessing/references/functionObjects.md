# FunctionObject Selection

Use runtime functionObjects when the requested evidence is known before or during execution and the active module supports the operation.

## Common purposes

- probes and sampled values;
- forces and force coefficients;
- field/area/volume averages and integrals;
- residual or solver-information recording;
- wall quantities such as y+ or wall shear/heat flux;
- derived fields and statistics;
- sets/surfaces sampling.

## Required contract

Record actual fields, patches/regions, locations/geometries, coordinate frame, density/reference convention, sign directions, write control, start/end window, averaging/integration and units.

## Experience rules

- A functionObject can run while measuring the wrong patch, direction, region or reference quantities.
- Force coefficients are invalid without patches, density treatment, reference area/length, lift/drag directions and moment center.
- Probe locations must lie in the intended mesh region.
- Statistics need adequate transient duration and stationarity evidence.
- Do not add unrequested expensive outputs by default.

Use output files as evidence referenced by final artifacts; do not create a generic functionObject manifest.
