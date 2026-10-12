# Residual Analysis

Residual evidence must retain field, time/iteration, initial/final residual, linear iterations and the formal/diagnostic source attempt.

## Interpretation

- A decreasing initial residual may indicate iterative progress but does not by itself establish convergence.
- Final residual and linear iterations expose inner-solver behavior.
- Steady cases also require monitored integral/QoI stabilization and conservation.
- Transient cases require acceptable convergence within timesteps plus timestep/Courant and physical-time adequacy; residuals need not monotonically decrease over physical time.
- Spikes may correspond to startup, mesh motion, interface events or instability and require context.

## Reporting

Provide histories, first/last/trend/spikes and field-specific interpretation. Do not combine different attempts or fields into a single unlabeled curve. Acceptance belongs to Physics Validation, not the extractor.
