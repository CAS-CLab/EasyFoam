# QoI Validation

A QoI value is not a validation result until its method and status basis are explicit.

## Required information

- physical definition and sign convention;
- field/patch/region and source attempt;
- reference quantities and nondimensionalization;
- time/window/averaging/integration;
- unit and uncertainty/variability where relevant;
- acceptance criterion, trusted comparison or evidence-supported engineering interpretation;
- evidence references.

## Status mapping

- `passed`/`failed`: explicit criterion or supported comparison evaluated.
- `limited`: valid method/value but incomplete criterion, duration, resolution or comparison.
- `not_assessed`: value/method/evidence unavailable.
- `blocked`: a decisive upstream contract prevents evaluation.

For benchmark evaluation, keep two dimensions separate:

- **coverage**: whether the required observable can be extracted from the
  candidate result;
- **agreement**: whether an extracted value satisfies its declared criterion.

An absent field or unavailable derived observable is an evidence/output
completeness issue. It must be reported as `not_assessed`/`limited` (and may
prevent end-to-end completion), but it is not evidence of a physically wrong
simulation. Only an observed value outside its criterion is an agreement
failure. Aggregate reports should therefore expose execution success, QoI
coverage, conditional agreement on available QoIs, and strict end-to-end
acceptance as separate numbers.

Task-specific measurement extractors, reference answers, and tolerance
comparators must remain outside the Agent-facing Skill context. Deterministic
measurement-only derivations (for example, vorticity computed from `U`) are
allowed only when declared by the task's measurement contract and must retain
their derived provenance; they must not synthesize solver/model state such as
`k`, `nut`, or `nuTilda`.

## Common errors

Wrong force patches/directions, wrong reference area/length/density, probe outside mesh, mixed time windows, diagnostic values presented as formal, uncorrected units, or comparison to a non-applicable source.
