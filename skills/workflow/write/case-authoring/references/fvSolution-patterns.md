# `fvSolution` Decision Patterns

`fvSolution` combines linear-solver contracts, algorithm controls, correctors, relaxation, and model-specific solution controls.

## Linear solver coverage

- Every solved field or explicit field family must match one solver entry.
- Final entries should inherit intentionally and tighten relative tolerance only when required by the algorithm.
- Solver/preconditioner/smoother choices must support the matrix characteristics produced by the equation.
- Regex groups must not omit generated species/phase/turbulence fields or accidentally capture incompatible fields.

## Algorithm contract

Write only the applicable SIMPLE, PISO, or PIMPLE control family. Confirm outer/inner correctors, pressure correction, non-orthogonal correction, momentum prediction, and convergence/residual controls against the selected module and formal time behavior.

## Relaxation and convergence

- Steady iterative cases may need equation/field relaxation; values require rationale or trusted structural evidence.
- Transient physical timesteps should not be converted into a pseudo-steady relaxation strategy silently.
- Residual controls are stopping aids, not proof of physical convergence.
- Excessive correctors or tiny tolerances may waste compute without improving model credibility.

## Common defects

Missing `Final` entries, wrong field regex, multiple conflicting algorithm blocks, legacy keyword families, absent species/energy solvers, and algorithm mismatch with run command are authoring failures.
