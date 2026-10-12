# Runner Safety Rules

Runner may execute only the user-scoped case and declared commands.

## Filesystem safety

- Work inside the bound run/case/attempt roots.
- Use portable relative references in canonical records.
- Never delete or overwrite unrelated directories, source geometry, prior formal evidence, or the active Skill library.
- Smoke/diagnostic changes use a separate copy.
- Reject path traversal, ambiguous repository roots, and unexpected symbolic-link escapes.

## Command safety

- Prefer argv execution without an interactive shell.
- Execute only declared OpenFOAM utilities, solver commands, MPI/reconstruction commands, or explicitly approved postprocessing commands.
- Preserve actual cwd and environment discovery.
- Do not automatically install software, change system configuration, or run arbitrary fetched code.
- Stop at first decisive failure and preserve logs.

## State safety

Runner writes one attempt record and command logs. It updates Workflow only with the run-record reference and decisive outcome. It does not edit CaseSpec, formal case, Skills, References, or Evolution records.
