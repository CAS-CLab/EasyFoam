# CaseSpec Contract

`case_spec.json` is the released planning contract for one case. Its authoritative requirement source is either the current natural-language user request (`runtime_prompt`) or a user-provided TXT path (`user_requirement_file`). It separates user-explicit requirements, derived decisions, approved values, Reference defaults, and unresolved review items; no copied `user_requirement.txt` is required.

## Required semantic groups

- requirement fidelity and provenance;
- physical classification;
- OpenFOAM-13 module/application, algorithm, and dictionary family;
- geometry and mesh route;
- actual field, patch, zone, material, and model contracts;
- numerical and formal run controls;
- requested QoIs, diagnostics, visuals, and validation checks;
- assumptions and review items.

## Release rule

Schema validity proves structure only. Plan releases the CaseSpec only when:

- no decisive review item is open;
- solver/module and physics are compatible;
- algorithm declarations agree;
- actual field, phase, species, patch, and zone names are resolved where required;
- complex geometry has a real source;
- formal controls and requested output methods are feasible;
- accepted defaults have provenance.

A blocked CaseSpec may still be written for audit. The Agent consolidates open decisive items into concrete user questions, updates the same CaseSpec after the user replies, and reruns semantic release. Write must not materialize it as a complete formal case while any blocking item remains unresolved.
