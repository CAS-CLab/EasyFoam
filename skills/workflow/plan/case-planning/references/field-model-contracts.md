# Field, Boundary, Material, and Model Contracts

This card defines planning-time contracts. Case Authoring later verifies the actual files against them.

## Field inventory

Separate:

- solved fields required by the selected module;
- model fields required by turbulence, phases, species, reaction, motion, or sources;
- auxiliary/runtime fields created by models or functionObjects;
- requested derived fields used only for postprocessing.

Use actual field names when known. Do not use `T`, `alpha.water`, `Yi`, or `rotor` as universal placeholders.

## Patch inventory

For every expected patch record:

- exact or unresolved name;
- mesh patch type;
- physical role;
- region, orientation, and paired-interface information;
- field-condition contract for every required field.

Keep mesh type and field condition separate. For example, a `wall` mesh patch may carry different thermal/turbulence field conditions, while `cyclic`, `cyclicAMI`, `empty`, `wedge`, and `symmetryPlane` require consistent mesh and field semantics.

## Boundary compatibility checks

- pressure and velocity conditions must provide a well-posed inflow/outflow/reference contract;
- compressible/thermal conditions must match the solved thermodynamic variable and property model;
- species conditions require an explicit species inventory and consistent closure;
- phase fractions require actual phase names, bounded initial state, and interface-compatible boundaries;
- turbulence fields/wall functions must match the selected model and near-wall strategy;
- reference pressure, hydrostatic pressure, or density conventions must be explicit when applicable.

## Material/model contract

Record values, units, dimensions, provenance, model names, and subdictionary family for transport, thermo, turbulence, phases, species, reactions, gravity, MRF/motion, porous media, and sources. `simulationType` is not the turbulence model name.

## Blocking conditions

Block when a missing field, actual phase/species name, boundary value, material property, model choice, zone/interface, or pressure convention changes the formal equations or case files.
