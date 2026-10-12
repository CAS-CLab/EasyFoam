# Mesh Resolution and Independence

Mesh validity, resolution credibility and mesh independence are distinct.

## Resolution credibility

On one mesh assess whether critical walls, boundary layers, wakes/jets/shocks/interfaces, gaps, curvature, rotating interfaces and source regions are resolved sufficiently for the intended outputs. Use y+, cells across features, local refinement and field-gradient evidence where applicable.

## Independence study

Use at least a defensible sequence of systematically refined meshes with unchanged physics, geometry, BCs, numerics, formal controls and QoI method. Record cell counts/resolution parameters, refinement ratios, QoIs, conservation and convergence quality.

## Interpretation

- Monotonic QoI change supports extrapolation more strongly than irregular change.
- Similar global cell count is not systematic refinement.
- A finer mesh that is less converged cannot be compared naively.
- Local/adaptive refinement needs a clear comparable resolution measure.
- Claim only the sensitivity demonstrated for the assessed QoIs; one QoI's stability does not prove every field is independent.

Without a study, state mesh credibility/limitations, not mesh independence.
