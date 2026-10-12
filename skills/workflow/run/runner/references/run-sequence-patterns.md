# Run Sequence Patterns

Runner executes the formal CaseSpec command sequence as one immutable attempt and records one `run_record.json`.

## Attempt modes

- **formal:** unchanged released case and controls; evidence may support requested Workflow claims.
- **smoke:** separate case copy and explicit reductions; demonstrates setup/executable viability only.
- **diagnostic:** separate copy and one bounded change intended to isolate a failure.
- **resume:** starts from an explicitly verified prior formal time using compatible case/control state.

## Sequence rules

1. Verify formal-case hash and requested attempt mode.
2. Discover active OpenFOAM environment and executable/module availability.
3. Create an isolated attempt directory/case copy when required.
4. Execute preprocessing in declared order.
5. Stop at the first nonzero command unless the command contract explicitly permits continuation.
6. Execute the solver only after prerequisite commands pass.
7. Record argv, cwd, start/end time, return code, stdout/stderr refs, terminal status and first deterministic error.
8. Do not rewrite the formal case from Runner.

## Common sequences

- generated simple mesh: mesh utility → `checkMesh` → solver;
- surface mesh: surface checks/features/background mesh/surface meshing → `checkMesh` → solver;
- imported mesh: converter → mapping/type adjustment when declared → `checkMesh` → solver;
- parallel: decomposition → parallel solver → reconstruction only when requested/needed.

## Evidence boundary

Command success proves only that the declared command completed. Formal solver completion does not prove numerical convergence, conservation, mesh independence, physical validity, or QoI acceptance.
