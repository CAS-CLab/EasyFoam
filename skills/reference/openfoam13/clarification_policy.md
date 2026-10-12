# Clarification Policy

## Decisive information

Do not guess information that changes the physical problem, geometry, mesh topology, model equations, solver family, boundary-value problem, formal execution, or requested acceptance claim. Typical decisive items include:

- phase regime, compressibility, energy/species/reaction coupling;
- steady/transient intent and pressure-velocity algorithm when it changes numerics;
- real named geometry, mesh source, scale, patch roles, zones, interfaces;
- material properties, phase/species data, rotation speed, gravity, sources;
- boundary values and reference pressure/temperature/composition;
- formal end time/iterations, timestep policy, output interval, restart intent;
- required QoI method, location, reference quantities, or acceptance criterion.

Missing decisive information produces an open blocking review item. Preserve the exact question and affected CaseSpec target.

## Inferable information

A specialist may derive information when the derivation is deterministic and evidenced, for example unit conversion, a solver-module mapping confirmed by a selected module card, or a patch field type forced by an `empty` mesh patch. Record source and rationale.

## Non-decisive defaults

A default is allowed only when the responsible specialist determines that it does not change the user target or core claim, the Reference explicitly supports it, and provenance is recorded as `reference_default`. Defaults must remain visible and reviewable.

## Existing cases

Do not reconstruct intent solely from files when user requirements or a reusable CaseSpec exist. Existing files may provide evidence for actual names, dimensions, and configured values; contradictions with the user target require review.

## Interaction Procedure

- Group related blocking items into concise, concrete questions.
- Ask only for information that the user must authoritatively decide or provide.
- Do not ask for deterministic mappings, file syntax, or non-decisive defaults that the responsible specialist can resolve with evidence.
- Apply the user reply to the affected targets in the same CaseSpec and record the resolution in the existing review item.
- Re-run Schema and semantic release checks after each supplement.
- If the user explicitly defers a decisive choice, retain the item as `deferred` and keep the applicable scope blocked.

## Interaction Outcome

When clarification is unavailable, do not silently continue. Use `review_required`, `blocked`, or a stage-scoped limited result according to whether the unresolved item prevents the requested scope.
