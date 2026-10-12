# Quantitative Postprocessing Patterns

Choose the smallest operation that directly answers the requested quantity.

| Need | Typical operation | Critical parameters |
| --- | --- | --- |
| Point history | probes | fields, coordinates, region, cadence |
| Line/profile | sampled set | endpoints/axis, resolution, time, interpolation |
| Surface distribution | sampled surface/patch fields | surface/patch, field, association, area convention |
| Integral/average | field value operations | region/patch, weighting, normalization, units |
| Force/coefficients | forces/forceCoeffs | patches, density, reference area/length/directions/center |
| Wall metrics | y+, wall shear, heat flux | wall patches, turbulence/thermal model, units |
| Phase/species conservation | field integrals/min/max | phase/species names, region, normalization |
| Statistics | mean/RMS/averages | start time, window, stationarity, sampling cadence |

## Traceability

Every product should identify source attempt, field/region, operation, parameters, time window, aggregation, unit and sign/reference convention. Plot files do not replace the underlying values/table.

## Failure handling

Missing method parameters → Plan. Missing fields/functionObject configuration → Write. Missing time history → Run. Utility/backend failure → Postprocess.
