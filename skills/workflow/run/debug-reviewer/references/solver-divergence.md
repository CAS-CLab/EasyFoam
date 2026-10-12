# Solver Divergence Diagnosis

Divergence is an outcome, not a root cause.

## Required prior checks

Confirm static case structure, actual mesh/zone/patch contracts, field dimensions/BCs, model properties, algorithm agreement and scheme/solver coverage.

## Divergence patterns

- immediate startup blow-up: often initialization, BC, dimensions, properties, zone/source or severe mesh defect;
- pressure–velocity oscillation: coupling/reference/outlet/relaxation/timestep issues;
- one transported field diverges first: field-specific scheme, BC, source, property or boundedness issue;
- gradual growth after apparent convergence: physical instability, accumulation, poor outlet/domain, or long-time conservation problem;
- parallel-only failure: decomposition/interface/environment before assuming physics.

## Verification

Identify the first field/time/location, formulate one causal hypothesis, apply a bounded repair, reproduce the source failure under matched conditions, then verify correction without degrading required behavior. Residual reduction alone is insufficient if conservation, boundedness or QoIs remain invalid.
