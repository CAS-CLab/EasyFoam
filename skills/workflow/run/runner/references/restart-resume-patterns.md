# Restart and Resume Patterns

A resume is valid only when the restart state belongs to the intended formal case lineage and remains compatible with current dictionaries and fields.

## Verify before resume

- selected time exists and is complete/readable;
- formal case/mesh/model changes since that time are compatible;
- all required fields are present for the current supported case region;
- `startFrom`/`startTime` select the intended state;
- timestep and write controls preserve the user contract;
- processor/reconstructed state matches the intended execution mode;
- diagnostic/smoke output is not mistaken for formal restart data.

## Restart categories

- **continuation:** same formal case and controls, later end target;
- **recovery restart:** same physical case with a verified runtime-only correction;
- **changed formal case:** normally a new formal generation/attempt, not a transparent resume;
- **mapped initialization:** a separate Write/Run contract requiring mapping evidence.

## Failure experience

Missing fields, inconsistent mesh, changed model families, unsupported time directories, stale decomposition and altered boundary dictionaries can invalidate a restart even when the solver starts. Record restart provenance and limitations in `run_record.json`.
