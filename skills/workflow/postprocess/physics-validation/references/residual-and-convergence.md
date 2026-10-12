# Residual and Convergence Assessment

## Steady iterative cases

Assess field residual history, final residual/iterations, continuity/conservation, and stabilization of required monitored quantities/QoIs over a meaningful window. Reaching an iteration count is not convergence.

## Transient cases

Assess convergence within each timestep/outer loop, timestep/Courant control, boundedness, accumulated conservation and adequacy of physical time. Physical transients may have nonmonotonic residuals; judge solver performance and physical evolution separately.

## Statistics/periodic behavior

LES, unsteady forces, periodic flows and averaged QoIs require startup removal, sufficient sampling duration, stationarity/periodicity evidence and uncertainty/variability reporting.

## Status guidance

- passed: applicable residual/monitor/time evidence satisfies stated basis;
- limited: trends are acceptable but duration, monitor or tolerance evidence is incomplete;
- failed: divergence, persistent nonconvergence or unstable/invalid behavior blocks claim;
- not_assessed: required history is unavailable.
