# Parallel Run Patterns

Parallel execution must be explicit in CaseSpec and compatible with the mesh, decomposition method, environment and postprocessing plan.

## Preconditions

- requested process count and available MPI/runtime;
- valid `decomposeParDict` and decomposition method;
- no stale processor directories from an incompatible mesh/case state;
- file-system path accessible consistently to ranks;
- intended reconstruction or parallel postprocessing strategy.

## Execution pattern

1. Verify or clean/recreate processor directories only in the attempt copy.
2. Run decomposition and record its output.
3. Launch the solver with explicit process count and supported command form.
4. Stop on MPI or rank failure and preserve the first deterministic error.
5. Reconstruct fields/mesh only when requested or required for downstream tools.
6. Record whether postprocessing reads reconstructed or decomposed data.

## Experience rules

- More ranks do not guarantee faster or stable execution; very small partitions may degrade performance/solver behavior.
- Decomposition must preserve required coupled interfaces and region structure.
- A serial case hash and a decomposed attempt are related evidence, not separate formal case definitions.
- Do not reuse processor directories after mesh or field changes without re-decomposition.
- MPI startup, library and permission failures are environment/invocation defects, not CFD-model defects.
