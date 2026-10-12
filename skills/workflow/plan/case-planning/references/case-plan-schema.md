# CaseSpec Field Guide

`case_spec.json` is the authoritative Plan contract. Validate it with `schemas/case_spec.schema.json`; semantic release additionally requires no unresolved decisive review item.

## Major sections

- identity, OpenFOAM version, description, and requirement source (`runtime_prompt` with null ref or `user_requirement_file` with a path);
- requirement fidelity with provenance and unresolved decisive items;
- physics classification;
- solver/module/application/algorithm/dictionary family;
- geometry and mesh route, patches, zones, interfaces, quality policy;
- actual field inventory and boundary contracts;
- material/model properties;
- numerical and formal run controls;
- QoI, diagnostic, visual, and validation contracts;
- assumptions, review items, and evidence sources.

## Provenance rules

The CaseSpec does not require a copied requirement file. Runtime-prompt provenance may use a null file reference; a user TXT source retains its user-provided path without copying or modification.

Every decisive value should identify one of:

- `user_explicit` with raw text/evidence reference;
- `reference_default` with source and rationale;
- `derived` with deterministic derivation and evidence;
- `review_required` when unresolved.

Do not hide a missing value in a free-form note. Use the structured review mechanism and mark whether it blocks release.

## Naming rules

Actual patch, zone, phase, species, region, and field names must be explicit or unresolved. Generic family notation may appear in explanatory metadata but must not masquerade as a file that Write should create.

## Release rule

Schema validity checks structure and types. The semantic audit checks compatibility, completeness, feasibility, and unresolved decisive items. Both are required before Write.
