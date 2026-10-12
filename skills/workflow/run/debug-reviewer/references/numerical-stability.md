# Numerical Stability Diagnosis

Use only after environment, dictionaries, mesh topology, fields, boundaries and physical models pass their static contracts.

## Evidence to inspect

- timestep/Courant and local maxima;
- residual and linear iteration histories by field;
- continuity/conservation errors;
- min/max boundedness of phase/species/temperature/pressure-related fields;
- location/time of first non-finite value;
- mesh-quality location near the instability;
- outer/inner corrector behavior and monitored QoIs.

## Causal categories

- timestep too large for transient/interface/acoustic/motion physics;
- unsuitable/insufficiently bounded scheme for a transported field;
- linear solver/preconditioner/tolerance mismatch;
- inadequate steady relaxation or coupling controls;
- inconsistent initial/boundary state;
- under-resolved shock/interface/wall/source region;
- physically invalid property/source value.

## Repair discipline

Change the smallest causal control, preserve formal requirements, and distinguish diagnostic stabilization from the final numerical method. First-order/bounded fallbacks may diagnose a cause but do not automatically become the retained formal scheme. Reassess accuracy and claim limits after any stabilization.
