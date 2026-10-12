# Cross-Artifact Consistency Audit

Apply consistency checks at the owner stage; do not rely on a later solver crash.

## Planning consistency

- physics classification ↔ solver module;
- steady/transient ↔ SIMPLE/PISO/PIMPLE;
- module/model ↔ actual solved field family;
- motion/source requirements ↔ required zones and dictionaries;
- requested QoI ↔ fields, functionObjects, locations, and reference quantities;
- complex geometry claim ↔ real geometry/mesh source.

## Write consistency

- mesh boundary inventory ↔ every required field boundaryField;
- patch type ↔ field boundary semantics;
- zone names ↔ MRF, porous, actuator, cyclicAMI, and source dictionaries;
- model names ↔ installed OpenFOAM-13 support;
- active fields ↔ fvSchemes and fvSolution coverage;
- algorithm ↔ exactly one applicable control block and correctors/relaxation;
- controlDict ↔ formal run controls and requested outputs.

## Run consistency

- formal case hash ↔ selected case directory;
- declared command chain ↔ module and parallel mode;
- resume policy ↔ available times and fields;
- smoke/diagnostic case ↔ separate copy and declared modifications.

## Evidence consistency

- every PASS ↔ explicit criterion and evidence;
- QoI value ↔ method, unit, time/iteration, source attempt;
- physical claim ↔ mesh, execution, numerical, and conservation prerequisites;
- visuals ↔ field/time/range/camera provenance.
