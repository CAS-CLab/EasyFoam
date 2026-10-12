# OpenFOAM-13 Solver and Algorithm Selection

Use after the physics taxonomy is resolved sufficiently to identify a solver-module family.

## Evidence priority

1. Compatible user-explicit OpenFOAM-13 module/application.
2. Local OpenFOAM Foundation v13 runtime capability and selected solver-module card.
3. A version-compatible local tutorial family with matching physics and algorithm.
4. Legacy-name mapping supported by the local module/application contract.

Do not select a module solely because a similarly named historical solver is familiar.

## Selection record

Store separately:

- execution form (`foamRun` module or confirmed application);
- module/application name;
- legacy equivalent, if supplied;
- SIMPLE/PISO/PIMPLE or not-applicable algorithm;
- dictionary family;
- expected solved/auxiliary field families;
- evidence paths and applicability differences.

## Algorithm guidance

- **SIMPLE** normally supports steady iterative pressure–velocity coupling.
- **PISO** normally supports transient coupling with correctors inside each timestep and limited outer iteration.
- **PIMPLE** combines outer correctors with PISO-like inner correction and is common for transient or pseudo-transient problems requiring stronger coupling.
- The selected module and its dictionaries remain authoritative; do not create multiple active algorithm blocks “for safety”.
- A user-explicit algorithm is a hard requirement only when compatible. If incompatible, block and explain the conflict.

## Compatibility checks

Before release, confirm:

- phase/compressibility/energy/species/motion support;
- actual energy, phase, and species field families;
- required model dictionaries and boundary semantics;
- algorithm agreement among CaseSpec, `fvSolution`, run command, and selected module;
- steady/transient controls and output semantics;
- local availability of the requested module/application.

## Ambiguity rule

If two choices remain valid but change formal equations, fields, algorithm blocks, or validation claims, create a blocking review item. Defaults are acceptable only for non-decisive implementation details and must carry provenance.
