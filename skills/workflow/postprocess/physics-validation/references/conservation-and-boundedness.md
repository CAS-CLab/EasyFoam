# Conservation and Boundedness Assessment

Select checks from the active physics.

## Conservation examples

- mass/continuity and inlet–outlet imbalance;
- energy or enthalpy balance and wall/source contributions;
- phase volume and phase-fraction sum;
- species mass fractions and reaction/source balance;
- momentum/force balance where meaningful;
- source/constraint normalization and integrated effect.

## Boundedness examples

- phase fractions and mass fractions within physical limits;
- positive density, viscosity, temperature/energy and turbulence quantities when required;
- no NaN/Inf or nonphysical extrema;
- pressure/velocity limits consistent with model and BCs.

## Interpretation

Normalize imbalance by a stated reference and define time window/region. Instantaneous imbalance in a transient system may differ from accumulated conservation. Solver-reported continuity is useful but may not replace an engineering control-volume balance required by the target.

PASS requires method, criterion/status basis and evidence. Missing required quantities yields limited/not_assessed, not automatic PASS.
