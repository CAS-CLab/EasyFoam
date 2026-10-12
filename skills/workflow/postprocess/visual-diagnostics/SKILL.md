---
name: workflow-visual-diagnostics
description: Generate and verify requested spatial or temporal CFD visual evidence.
---

# Visual Diagnostics

## 1. Entry Conditions

Use when the CaseSpec or user requests mesh views, contours, slices, surfaces, vectors, streamlines, isosurfaces, or temporal visual diagnostics.

## 2. Required Inputs

- requested field, derived quantity, view, region, time, and output format;
- available mesh and fields from the selected attempt;
- coordinate/frame and seed information where required;
- ParaView/pvpython or another approved rendering backend.

## 3. Decision Procedure

1. Confirm that requested fields/times exist or can be derived legitimately.
2. Select the minimum visual operation that answers the requested question.
3. Preserve geometry, units, coordinate frame, color quantity, range policy, and time provenance.
4. For streamlines, define seed geometry and integration direction explicitly.
5. For comparison visuals, keep view/range conventions consistent unless the user requests otherwise.
6. Render directly to the requested output path.
7. Verify file existence, non-empty content, and expected format.

## 4. Output Contract

Write only requested images, animations, or approved ParaView state files under `results/visuals/` or a user-approved path. Do not create separate visual-contract or visual-manifest JSON files.

## 5. Completion Conditions

Pass when each required visual is available, readable, and traceable to the selected field/time/view. Mark unavailable visuals `blocked`/`unavailable` explicitly for final evidence synthesis.

## 6. Invariants

- Visuals support interpretation but do not replace quantitative validation.
- Formal and diagnostic data are never mixed silently.
- Color ranges and derived fields are not chosen to hide undesirable behavior.
- Missing fields are not fabricated.

## 7. Failure Routing

Missing data caused by case design returns to Write; missing run output returns to Run; unavailable renderer blocks only the requested visual unless it is required for the requested scope.

## 8. Scripts

```text
scripts/render_visuals.py
scripts/validate_visual_artifacts.py
```

`scripts/render_visuals.py` supports mesh, contour, slice, streamline, vector, isosurface, and animation; point/cell association; data/fixed/symmetric ranges; regions; seeds; camera; and time range. It writes only the requested visual.

## 9. Conditional References

- `references/visual-diagnostic-schema.md` for required parameters and provenance;
- `references/paraview-workflow.md` for filter-specific rendering;
- `references/rendering-comparison-rules.md` for range, camera, and comparison consistency;
