# ParaView/pvpython Rendering Workflow

## Reader and source

Open the intended `.foam` case/region, select the required mesh region and time, and verify field availability/association before applying filters. Update the pipeline after changing time or arrays.

## Operations

- mesh: surface/surface-with-edges and optional region extraction;
- contour/slice: scalar/vector component coloring with explicit plane when used;
- streamline: vector field plus valid seeds inside the domain;
- vector: glyph/vector representation with controlled scale/subsampling;
- isosurface: scalar contour at explicit physical value(s);
- animation: fixed pipeline, camera and range across selected times.

## Reliability rules

- Do not silently switch point/cell association.
- Confirm seeds and slices intersect the intended fluid region.
- Use actual derived fields or generate them through supported postprocessing first.
- Record range and camera for reproducible comparisons.
- Verify output readability and nonzero size.
- Renderer success does not establish physical credibility.
