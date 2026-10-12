# Visual Diagnostic Parameter Contract

Resolve these parameters before rendering.

## Common fields

- source attempt and case/region;
- time or time range;
- field and point/cell association;
- visual kind;
- units/coordinate frame;
- range mode and values;
- camera/projection and image/animation format;
- purpose and comparison group.

## Kind-specific requirements

- **mesh:** region, representation, surface/edges and optional clip/slice.
- **contour:** field/component, association, region, range.
- **slice:** plane origin/normal and contour parameters.
- **streamline:** vector field, seed point/line, direction and integration limits.
- **vector:** vector field, association, scale and subsampling.
- **isosurface:** scalar field and isovalue(s).
- **animation:** source time range, frame rate, fixed camera/range policy.

Missing decisive plane, seed, isovalue, field or time is a planning/output-contract gap; do not fabricate it silently.
