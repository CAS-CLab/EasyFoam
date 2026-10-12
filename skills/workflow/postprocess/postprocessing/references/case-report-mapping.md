# Workflow Report Mapping

Generate a report only when explicitly requested. The report summarizes canonical artifacts and requested results; it is not a second state store.

## Suggested sections

1. user target and requested scope;
2. released CaseSpec decisions and unresolved limitations;
3. formal case/mesh identity and hashes;
4. run attempts and decisive terminal evidence;
5. numerical, conservation, physical and QoI assessments;
6. requested tables/plots/visuals with provenance;
7. highest supported claim, limitations and next action.

## Mapping rules

Derive content from explicit CaseSpec fields, available fields, requested QoIs and `evidence_summary.json`. Do not create a case-type classification/confidence artifact. For unfamiliar physics, report only supported evidence and leave missing interpretation explicit.

## Evidence groups

- **Numerical:** residuals, timestep/Courant, continuity/conservation, boundedness, monitored stability.
- **Engineering/QoI:** forces, coefficients, profiles, integral quantities, heat/mass transfer, pressure loss, interface position, etc.
- **Flow physics:** requested field/mesh/streamline/vector/temporal visuals.

A report must not upgrade claim status, hide unavailable outputs, or substitute a plausible image for quantitative evidence.
