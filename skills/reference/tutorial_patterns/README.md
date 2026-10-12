# Tutorial Patterns

This directory stores generalized indexes derived from the official OpenFOAM-13 `tutorials/` tree. It does not turn individual tutorials into skills and it must not list concrete tutorial case names.

## Source

- Primary source: `https://github.com/OpenFOAM/OpenFOAM-13/tree/master/tutorials`
- Extraction method: recursive GitHub tree path aggregation under `tutorials/`, followed by local aggregation into module-level and file-category patterns.

## Files

- `official_tutorial_tree.md` records the official top-level tutorial modules and generic directory grammar.
- `solver_module_to_family_map.yaml` maps official module directories to existing solver/family reference cards.
- `family_to_reference_requirements.yaml` maps family cards to minimal reference cards and pattern categories.
- `tutorial_pattern_index.yaml` is a machine-readable generalized pattern index for Workflow Plan routing.

## Non-Goals

- Do not copy tutorial source files.
- Do not create one skill per tutorial.
- Do not include concrete tutorial case names or evaluation-specific case names.
- Do not update `tutorial_families/` from this index unless an Evolution promotion explicitly requests it.
