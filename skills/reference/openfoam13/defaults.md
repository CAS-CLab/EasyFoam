# Defaults and Provenance

## Principle

Defaults reduce clerical burden; they must not define the scientific problem. Every accepted default records value, unit, source card, and rationale.

## Usually non-decisive defaults

Subject to the selected module and case context, these may be defaulted when unspecified:

- output precision and file format;
- log naming and result directory conventions;
- a conservative linear-solver tolerance starting point for a field whose solver family is already fixed;
- visualization image size and neutral camera reset;
- parser or report formatting options.

## Usually decisive and not defaultable

- geometry dimensions or replacement geometry;
- inlet/outlet values, wall motion, phase fractions, species composition;
- density, viscosity, thermophysical data, turbulence model;
- rotation speed, gravity vector, surface tension, porous coefficients;
- steady/transient intent, formal time horizon, timestep when explicitly required;
- mesh resolution required for the QoI;
- force coefficient reference area/length/directions;
- pass/fail thresholds for numerical or physical validation.

## Reference-derived numerical settings

Reference settings are starting contracts, not proof of suitability. They must cover all active equations and remain consistent with SIMPLE/PISO/PIMPLE, boundedness, transient controls, and mesh quality. Numerical changes made only to suppress a deeper mesh or physics defect are not valid defaults.
