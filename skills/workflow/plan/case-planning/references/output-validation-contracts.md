# Output and Validation Contracts

Translate natural-language output requests into executable, assessable contracts before case authoring.

## QoI contract

For each QoI record:

- name and physical meaning;
- source fields/patches/regions;
- method or functionObject;
- location, direction, reference quantities, sign convention;
- time window, sampling cadence, averaging/integration;
- unit and nondimensional convention;
- acceptance criterion or explicit `not_specified` status;
- required evidence and output format.

Examples of missing decisive parameters include probe coordinates, force patches, density convention, reference area/length, lift/drag direction, moment center, line/surface definitions, and averaging interval.

## Validation groups

Separate:

1. requirement fidelity;
2. case-file/model consistency;
3. mesh topology/quality/resolution;
4. formal execution;
5. numerical behavior;
6. conservation and boundedness;
7. physical credibility;
8. QoI assessment;
9. visual evidence availability/provenance.

## Acceptance criteria

Preserve user-defined thresholds. Use trusted published/reference comparisons only when applicability is established. Do not turn a value, residual decrease, successful command, or plausible image into PASS without a stated basis.

## Visual contract

Specify field, association, region, time/time range, filter type, plane/seed/isovalue/vector parameters, range policy, camera/comparison convention, and output format. Visuals support interpretation but do not replace numerical or physical evidence.

## Claim boundaries

- Smoke success: executable setup only.
- Residual decrease: not automatically converged or physically credible.
- One mesh: no mesh independence claim.
- A QoI value: no acceptance claim without criterion or supported interpretation.
