# Rendering and Comparison Rules

Comparative visuals require controlled presentation so apparent differences represent data rather than rendering choices.

## Fixed conventions

For a comparison group preserve:

- field/component and association;
- mesh region and filter geometry;
- time or normalized phase;
- camera position, focal point, view-up and projection;
- image dimensions and background;
- color map and range policy;
- vector scale/subsampling, streamline seeds or isovalues.

## Range policies

- **data:** useful for single exploratory view; not directly comparable across cases/times.
- **fixed:** required when absolute values are compared.
- **symmetric:** useful for signed quantities around zero with explicit magnitude.

Do not clip extrema or choose ranges solely to exaggerate/suppress differences. Label units and range. If a fixed range saturates data, report that limitation.

## Temporal outputs

Use one camera and range across frames, confirm time ordering, avoid diagnostic/formal mixing and choose a frame rate that does not imply a physical timescale unless explicitly mapped.
