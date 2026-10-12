# Surface and Feature Preparation

Surface evidence precedes volume meshing.

## Checks

- file readability and supported format;
- unit scale and coordinate orientation;
- bounding box versus expected physical size;
- duplicate/degenerate facets, open edges, non-manifold edges, self-intersections, disconnected regions;
- normal consistency where it affects region interpretation;
- region names and intended patch mapping;
- sharp features requiring explicit extraction;
- whether the surface represents a closed solid, an open boundary, or multiple regions.

## Experience rules

Do not automatically “repair” or close a user surface without recording the geometric change. A visually plausible surface may still have topological defects that cause leakage, wrong cell retention, or patch fragmentation. Surface simplification can remove QoI-relevant features. Feature extraction angle and resolution should reflect geometry and mesh scale rather than a universal value.

## Output to mesh planning

Provide confirmed scale, bounds, region inventory, surface limitations, feature-edge reference, and any required user decision. No separate manifest is required; retain actual utility logs and update the canonical mesh/case evidence through Workflow.
