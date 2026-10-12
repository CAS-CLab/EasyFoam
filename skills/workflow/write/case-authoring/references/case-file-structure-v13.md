# OpenFOAM-13 Case File Structure

Use the selected solver-module card and released CaseSpec to determine the required files. Do not create every familiar dictionary by default.

## Core layout

```text
case/
├── 0/ or selected initial-time directory
├── constant/
└── system/
```

Typical responsibilities:

- initial-time directories: actual solved/model field files and complete patch entries;
- `constant/`: mesh, transport/thermophysical/model properties, phases/species, gravity, MRF/motion, source and constraint configuration;
- `system/`: `controlDict`, `fvSchemes`, `fvSolution`, mesh-generation/import dictionaries, decomposition, sampling, and explicitly required utilities.

## File inclusion rules

- Include a dictionary only when required by the active module/model/utility.
- File names, header classes, object names, and region placement must match what the local OpenFOAM-13 reader expects.
- Multi-region cases require region-aware field and dictionary placement; do not flatten region contracts into a single directory.
- Preserve user-provided files unless a verified contract change requires editing.
- Remove placeholders, template comments that imply unresolved choices, and unsupported legacy-only files before freezing Write.

## Cross-file consistency

Check at least:

- run command/module ↔ `controlDict`/solver selection;
- module ↔ physical/model dictionaries and actual fields;
- mesh boundary ↔ every field boundary block;
- cellZone/faceZone/interface names ↔ MRF/motion/source/constraint dictionaries;
- algorithm ↔ active `fvSolution` control block;
- active equations ↔ `fvSchemes` and linear solver entries;
- output contracts ↔ functionObjects and runtime fields.

A complete directory tree is not sufficient if these contracts disagree.
