# Field File Patterns

Field files are generated from the released field inventory and actual mesh, not from a universal template.

## Required components

Every field file must have:

- OpenFOAM header with correct class, location, and object name;
- physically correct dimensions;
- explicit internal field or model-supported initialization;
- boundary entries for every actual patch in the relevant region;
- condition types and values compatible with patch mesh types and the selected model.

## Naming and class rules

- Use actual field names required by the module/model.
- Do not create literal `Yi` as a species file unless it is truly the configured species name.
- Do not assume `T` when the model solves `h` or `e`.
- Do not assume `alpha.water`; use configured phase names.
- Scalar/vector/tensor class and dimensions must match the equation and boundary condition.

## Initialization experience

- Uniform initialization is acceptable only when physically defensible and compatible with startup stability.
- Interface fields need bounded phase initialization consistent with geometry.
- Turbulence fields should be derived from stated intensity/length-scale or wall strategy when those inputs are available; do not use arbitrary positive constants without provenance.
- Compressible/thermal fields must form a thermodynamically consistent initial state.
- Reference-pressure fields and hydrostatic variants must follow the chosen pressure convention.

## Static audit

Compare the field inventory with actual files, check all patch names, reject duplicate/missing blocks, and identify values still represented by placeholders or unresolved review markers.
