# Formal Run-Control Contract

Formal controls preserve the user's intended simulation and output cadence.

## Required controls

Record as applicable:

- preprocessing command order;
- solver command/module;
- `startFrom`, `startTime`, restart source and overwrite policy;
- `stopAt`, `endTime` or steady iteration target;
- `deltaT`, adjustable stepping, `maxCo`, `maxAlphaCo`, and maximum timestep controls;
- `writeControl`, `writeInterval`, write format/precision and purge policy;
- runtime-modifiable behavior;
- serial/parallel intent, process count, decomposition and reconstruction;
- required functionObjects and runtime outputs.

## Semantics

- `writeInterval` has different meaning under `timeStep`, `runTime`, and `adjustableRunTime`.
- A transient physical model needs timestep and stability controls even if a short diagnostic run is later used.
- A steady SIMPLE case still needs clear iteration/time bookkeeping and write cadence.
- Restart behavior must identify which prior time is authoritative and whether formal controls remain unchanged.

## Hard requirements

User-explicit end time, timestep, Courant target, write cadence, solver command, and parallel intent are not shortened or replaced silently. Diagnostic/smoke overrides occur only in a separate run copy and never rewrite the formal CaseSpec.

## Default rule

A Reference default may fill only a non-decisive unspecified field. Record source and rationale. If the value affects physical fidelity, stability, requested output, computational scope, or claim strength, leave it for review.
