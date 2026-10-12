# Tutorial Reference Selection Rules

Tutorial retrieval supplies structural evidence to Case Planning; it does not copy a tutorial as the final case.

## Selection priority

1. Same OpenFOAM Foundation version and locally available tutorial tree.
2. Same solver module/application and algorithm family.
3. Same phase/compressibility/energy/species/motion model.
4. Same dictionary family and required field families.
5. Similar mesh/interface/zone requirements.
6. Similar QoI or runtime utility pattern.

Geometry resemblance alone is weak evidence when physics or module differs.

## Minimum comparison

Record:

- tutorial path and version;
- matching module/application and algorithm;
- matching physical/model features;
- reusable files/dictionary sections;
- applicability differences;
- fields, patches, zones, properties, controls, and values that must not be copied;
- verification needed in the active case.

## No-copy boundary

Do not copy case-specific dimensions, patch/zone names, material values, initial/boundary values, timestep/end time, relaxation, mesh settings, or acceptance criteria unless independently supported by the user requirement or an applicable Reference.

## Failure handling

If no sufficiently compatible local tutorial exists, return no-match evidence. Do not broaden the search until an unrelated tutorial appears acceptable, and do not invent an official path.
