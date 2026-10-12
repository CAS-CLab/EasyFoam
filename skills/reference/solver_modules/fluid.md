# `fluid` Module Card

## Intended family

General pressure-based fluid workflows in Foundation v13, commonly including compressible or thermally coupled single-phase cases. The exact formal contract is selected from the active local module and thermophysical dictionaries.

## Legacy lineage

Common explanatory lineage may include `rhoSimpleFoam` or `rhoPimpleFoam` families. Legacy lineage does not determine the current dictionary family or actual energy variable.

## Planning contract

Resolve explicitly:

- compressibility/low-Mach treatment and equation of state;
- steady/transient intent and SIMPLE/PIMPLE/PISO support;
- actual solved energy variable (`T`, `h`, `e`, or model-specific field);
- thermophysical mixture, transport and energy model;
- turbulence treatment and model fields;
- pressure/density/temperature reference and boundary conventions;
- gravity/buoyancy, MRF/motion and sources;
- material data, units and valid range.

## Typical file families

Velocity, pressure/thermodynamic and actual energy fields; thermophysical/physical and momentum-transport dictionaries; optional gravity/motion/source dictionaries; system numerics and controls. Exact names must be confirmed from the selected local module/model.

## Compatibility checks

- energy field ↔ thermo energy selection ↔ BCs ↔ solver entries;
- pressure/temperature/density state is thermodynamically consistent;
- inlet/outlet total/static conditions match the intended regime;
- material properties and equation-of-state domain are valid;
- steady/transient algorithm and timestep/Courant controls agree;
- heat-transfer QoIs identify walls, reference quantities and sign convention.

## Frequent failures

Wrong thermo package, missing energy field/solver, incompatible pressure–temperature BCs, invalid material data, omitted density/thermo entries, algorithm mismatch, nonphysical temperature/density, and overly large transient timestep.

## Must not guess

Energy variable, gas/liquid model, heat capacity, molecular weight, conductivity, inlet thermodynamic state, reference pressure, wall thermal condition or buoyancy reference state.
