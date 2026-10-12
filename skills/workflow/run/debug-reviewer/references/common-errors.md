# OpenFOAM Failure Triage Order

Diagnose from the first deterministic error and the earliest contract layer. Later warnings often cascade from the initial defect.

## Triage order

1. environment/executable/permissions/path;
2. command invocation and case location;
3. dictionary parsing, missing file/keyword and version family;
4. mesh topology, patch/zone/region and decomposition;
5. field inventory, dimensions and boundary coverage;
6. physical/model dictionary compatibility;
7. algorithm, schemes and linear-solver coverage;
8. runtime numerical instability/divergence;
9. missing derived/postprocessing evidence.

## Evidence discipline

- Quote or reference the exact first deterministic error.
- Distinguish symptom from root cause and unrelated warnings.
- Change one bounded cause at a time in a repair copy.
- Verify the repair with the narrowest command that previously failed before rerunning downstream work.
- Route the verified repair to the earliest affected stage.

## Do not

Do not tune numerics before static mesh/field/model contracts pass, add missing files blindly, copy an unrelated tutorial dictionary, or label solver completion as a verified root-cause repair without matched evidence.
