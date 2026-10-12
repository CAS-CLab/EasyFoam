# VTK Export Guidance

Use VTK export only when requested or required by an approved downstream tool.

## Contract

Select the source attempt, region, time/time range, fields, cell/point representation and target directory. Confirm sufficient disk space and preserve field names/units/association.

## Experience rules

- Export does not create missing physics fields.
- Cell-to-point interpolation may alter extrema and should be labeled for quantitative interpretation.
- Large decomposed/transient exports can be expensive; select only requested times/fields.
- Do not mix formal and diagnostic times in one unlabeled dataset.
- Verify output readability before reporting completion.
