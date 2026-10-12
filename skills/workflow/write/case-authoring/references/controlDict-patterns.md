# `controlDict` and Runtime-Control Patterns

`controlDict`, CaseSpec, run command, and functionObjects must describe the same formal simulation.

## Solver execution

For module-based Foundation v13 workflows, record the selected `foamRun -solver <module>` command in the CaseSpec and ensure the case dictionaries are compatible with that module. Use a legacy application only when the local runtime and selected Reference support it.

## Formal controls

Include and reconcile as applicable:

- `startFrom`, `startTime`, `stopAt`, `endTime`;
- `deltaT`, `adjustTimeStep`, Courant limits, and maximum timestep;
- `writeControl`, `writeInterval`, write format/precision, time format/precision, purge policy;
- `runTimeModifiable`;
- libraries and functionObjects required for requested evidence.

## Semantics and experience

- Under `timeStep`, `writeInterval` is a step count; under runtime-based controls it is a time interval.
- Restart settings must point to available, compatible times and must not accidentally reuse diagnostic output.
- FunctionObjects must use actual fields/patches/regions and preserve sampling/sign/reference conventions.
- Formal controls are not shortened for convenience. Smoke/diagnostic changes belong to a separate attempt copy and must be labeled.
- A successful short run cannot support final-time, statistical, or convergence claims.

## Audit

Check the command/module, time behavior, output cadence, restart policy, parallel workflow, and all requested runtime evidence before freezing the formal case.
