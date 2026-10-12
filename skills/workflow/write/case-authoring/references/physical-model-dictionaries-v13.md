# Physical and Model Dictionaries for OpenFOAM-13

Use the selected module card to identify exact dictionary names and model substructure. This card defines consistency principles, not a universal file list.

## Model families

Resolve as applicable:

- transport/viscosity and density treatment;
- thermophysical package, equation of state, energy form, mixture and transport models;
- momentum transport and laminar/RAS/LES selection;
- phase properties, interfacial forces, surface tension, phase change;
- species inventory, reaction/chemistry, combustion and thermo coupling;
- gravity and buoyancy reference state;
- radiation or additional energy models;
- region-specific properties in multi-region cases.

## Consistency rules

- Model names must be supported by the active Foundation v13 installation.
- `simulationType` is separate from the RAS/LES model.
- The thermo energy choice must agree with actual field files and boundary conditions.
- Species listed in mixtures/reactions must agree with field files and closure rules.
- Phase names must agree across phase dictionaries, fields, boundary conditions, and functionObjects.
- Material values require units/dimensions and provenance.
- Do not retain inactive model subdictionaries as alternative configurations.

## Failure patterns

Common failures include wrong dictionary family for the selected module, legacy keys, missing model coefficients, unsupported model names, inconsistent phase/species names, and model-required fields missing from `0/`.

## Review gate

If the module supports multiple formal model families and the choice changes equations or fields, return to Plan rather than choosing from a tutorial by convenience.
