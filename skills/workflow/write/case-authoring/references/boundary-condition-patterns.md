# Boundary-Condition Compatibility Patterns

Select boundary conditions from physical role, mesh patch type, solved variable, flow direction, and selected model. A familiar inlet/outlet template is not universally well posed.

## General rules

- Mesh patch type and field boundary condition are separate but must be compatible.
- Every actual patch needs an entry for every required field.
- Preserve `empty`, `wedge`, `symmetryPlane`, `cyclic`, and `cyclicAMI` semantics across all fields.
- Wall velocity, slip, moving-wall, rotating-wall, thermal, species, phase, and turbulence behavior must match the physical contract.
- Direction-dependent conditions require a defined coordinate frame and sign convention.

## Pressure–velocity pairing

- Ensure the domain has a pressure/reference mechanism appropriate to incompressible or compressible formulation.
- Avoid over-specifying both pressure and velocity at all boundaries.
- Backflow-sensitive outlets may require compatible inlet/outlet treatment for all transported variables.
- Mass-flow, total-pressure, static-pressure, and fixed-velocity conditions imply different information and cannot be substituted silently.

## Thermal/species/phase rules

- Thermal conditions must match the solved energy variable and thermophysical model.
- Species boundaries require actual species names and closure/inert-species logic.
- Phase-fraction boundaries require bounded values and interface-consistent behavior.
- Conjugate/coupled interfaces require matching region and coupling semantics.

## Turbulence and walls

Turbulence field conditions and wall functions must be compatible with simulation type, turbulence model, near-wall resolution, and wall treatment. A successful parse does not prove wall treatment is appropriate.

## Audit order

Check patch inventory → physical role → field coverage → type compatibility → dimensions/values → paired/coupled relations → model-specific requirements.
