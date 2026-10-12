# Mesh Quality and Credibility Rules

Separate fatal topology defects, numerical quality concerns, and resolution adequacy.

## Fatal/blocking examples

- negative or zero cell volume;
- invalid topology, disconnected required region, duplicate/illegal faces;
- missing required patch, region, cellZone, or faceZone;
- wrong dimensionality or interface pairing;
- cells retained on the wrong side of geometry.

## Quality concerns

Non-orthogonality, skewness, aspect ratio, concavity, interpolation weights, determinant/volume ratios, abrupt size transitions, and poor layer quality can impair stability/accuracy. Interpret values with solver, schemes, local location, and intended physics; do not use one universal threshold as proof.

## Resolution credibility

A topologically valid mesh may still be under-resolved. Assess wall treatment/y+, boundary layers, wakes/jets/shocks/interfaces, curvature, gaps, rotating interfaces, source regions, and QoI sensitivity.

## Experience rules

- Numerical tuning cannot convert fatal topology into a credible mesh.
- Global maximum metrics should be localized; a few problematic cells near critical physics may matter more than a larger value in an inactive area.
- Cell count alone is not resolution evidence.
- One mesh can support a bounded engineering result but not mesh independence.

## Recording

Preserve checkMesh output, actual patch/zone inventory, key quality observations, limitations, and any resolution plan. Do not create a separate mesh manifest by default.
