# `foamPostProcess` Guidance

Use for supported functionObjects or derived operations on existing time directories without changing the formal solver history.

## Preconditions

- selected case/region/time exists and is readable;
- required source fields are present;
- the functionObject/library is supported in the active OpenFOAM-13 environment;
- operation parameters match the CaseSpec output contract.

## Rules

Run only the required operation and time range. Preserve command stdout/stderr, selected attempt and generated file paths. Distinguish postprocessed fields from fields produced during the formal run. Do not infer physical validity from utility success.

If a required quantity cannot be reconstructed from existing fields, route to Write/Run for future evidence generation rather than fabricating it.
