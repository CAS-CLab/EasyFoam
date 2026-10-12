# `fvSchemes` Decision Patterns

Discretization is selected per active equation and field family. Do not copy an entire schemes dictionary from an unrelated tutorial.

## Required coverage

Provide the categories read by the selected module, commonly including time derivatives, gradients, divergence/convection, diffusion/laplacian, interpolation, surface-normal gradients, wall-distance or flux requirements. Exact entries depend on the module and models.

## Selection principles

- Match steady/transient time discretization to the formal physical/time contract.
- Choose convection treatment appropriate to transported variable, expected discontinuities, boundedness, and accuracy.
- Phase-fraction, species, turbulence, energy, and momentum fields may require different bounded/limited treatment.
- Non-orthogonal/skewed meshes may require robust gradient/laplacian handling, but numerical schemes must not be used to excuse an invalid mesh.
- Higher order is not automatically more credible; assess stability, boundedness, and mesh resolution.
- Keep explicit field-family patterns narrow enough to cover intended fields without accidentally matching unrelated ones.

## Audit

Check that every active equation has a matching scheme, no obsolete entries are relied upon, defaults do not hide missing contracts, and selected schemes are consistent with the intended numerical validation.

## Failure experience

Missing scheme errors are static authoring defects. Divergence after all static contracts pass is a separate numerical diagnosis; do not respond by blindly switching every scheme to first order.
