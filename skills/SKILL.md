---
name: EasyFoam
description: Root router for EasyFoam's OpenFOAM-13 Workflow loop, human-governed Evolution loop, and read-only Reference layer.
---

# EasyFoam

EasyFoam is currently a single-region-focused Skill system for creating, resuming, repairing, running, validating, and evolving OpenFOAM workflows.

This root Skill only:

* binds the user's target;
* selects Workflow, Evolution, or Reference;
* establishes system-level boundaries;
* loads the smallest required downstream Skill set.

Do not perform CFD planning, case authoring, execution, postprocessing, or Skill modification at this level.


## System Architecture

```text
User request
├── Workflow
│   └── Plan → Write → Run → Postprocess
├── Evolution
│   └── Experience → Candidate → Review and Validation
│       → Human Decision → Apply / Defer / Reject / Rollback
└── Reference
    └── Read-only OpenFOAM and CFD knowledge
```


The loops have different responsibilities:

* **Workflow** completes or audits the current CFD task and passively records reusable Experience.
* **Evolution** is entered only when the user explicitly requests reuse, distillation, review, application, or rollback of verified Experience.
* **Reference** supplies read-only knowledge to Workflow or Evolution; it does not execute cases or write runtime state.



### Workflow

Use Workflow to:

* create a new case;
* resume an existing case;
* inspect or repair a failed case;
* execute an OpenFOAM case;
* validate numerical and physical results;
* generate postprocessing or visualization artifacts;
* record reusable Experience.

Workflow may modify the user-scoped case, but it must not directly modify formal Skills or References.

### Evolution

Use Evolution only when the user explicitly requests:

* Experience review;
* Candidate distillation;
* Candidate validation;
* Skill or Reference update;
* limitation, rejection, deferment, or rollback.

Evolution is human-governed, evidence-linked, and reversible.

### Reference

Use Reference to retrieve read-only knowledge about:

* OpenFOAM modules and dictionaries;
* physical models;
* boundary conditions;
* mesh strategies;
* numerical settings;
* runtime diagnostics;
* QoIs;
* postprocessing and visualization.
* Evolution evidence, validation, promotion, and rollback governance.

Reference does not execute cases or change Workflow state.

## Root Routing

| Request or current state | Enter |
| --- | --- |
| Create, resume, inspect, repair, run, validate, postprocess, visualize, or summarize an OpenFOAM case | `skills/workflow/SKILL.md` |
| Review Experience, create or validate a Candidate, update Skill or Reference, or roll back a change | `skills/evolution/SKILL.md` |
| Retrieve OpenFOAM or CFD knowledge without executing or modifying a case | `skills/reference/SKILL.md` |

After selecting the layer, use `skills/ROUTING.md` to locate the active stage and specialist Skill.

## Canonical Artifacts

The system uses the following canonical data contracts:

```text
case_spec.json
workflow.json
run_record.json
evidence_summary.json
experience_record.json
candidate_patch.json
promotion_record.json
```

These artifacts are not additional Workflow stages.

A Workflow run has one canonical `workflow.json`. Logs, command records, hashes, patches, fields, plots, and reports are evidence referenced by the canonical artifacts.


## Global Boundaries

1. The executable target is OpenFOAM Foundation v13. On Windows, execute through WSL; on Linux or inside WSL, execute through the native shell. Other versions or execution backends require a separately validated compatibility adapter and must not be treated as supported by default.
2. A new CaseSpec must be grounded in either the current natural-language user requirement or a user-provided requirement TXT path. The user-defined target and scope are authoritative. Do not autonomously inspect or modify unrelated cases, directories, repositories, artifacts, or historical runs.
3. Decisive CFD information must not be invented. This includes physics, geometry, boundary conditions, material properties, solver compatibility, and user-specified numerical controls.
4. Workflow may repair the active case and record Experience, but formal Skills and References may change only through explicit Evolution.
5. Evolution must not start automatically, inject faults as evidence, auto-promote, auto-merge, auto-push, or silently broaden a Candidate's scope.
6. Reference is read-only during Workflow.
7. Persist portable relative paths or stable logical identifiers whenever possible. Do not store machine-specific absolute paths as canonical references.
8. Missing or contradictory decisive information must remain visible as `review_required`, `blocked`, or `deferred`; consolidate it into concrete user questions, apply the user supplement to the same CaseSpec, and do not advance to Write until semantic release passes.
9. File correctness, solver execution, numerical credibility, physical credibility, and requirement satisfaction are different claims and require different evidence.

## Target Binding and Loading

Before loading a specialist Skill, bind the request to the smallest user-specified target, such as:

* a new requirement;
* an existing case or run;
* a Workflow stage;
* a failed command or log;
* a mesh, field, or result artifact;
* an Experience or Candidate;
* a named Skill or Reference.

Then apply the following loading rules:

1. If the user explicitly names a stage, Skill, case, run, artifact, or Evolution action, use that target directly when safe.
2. For a new OpenFOAM simulation request with no existing case or reusable Workflow state, enter Workflow at Plan.
3. For an existing case or run, inspect its canonical artifacts and decisive evidence, then resume from the earliest incomplete or invalid stage.
4. Do not repeat a valid earlier stage only because a later stage failed or is missing.
5. Load one active stage Skill, one active specialist Skill, and only the References needed for the current decision.
6. Load a second specialist only for an explicit handoff.
7. Do not preload the complete Skill tree, all References, all historical runs, or all Experience records.
8. If the target cannot be resolved without expanding beyond the user's scope, request the missing target or record `review_required`.

Detailed stage routing and specialist selection are defined in `skills/ROUTING.md`. Stage responsibilities, References, procedures, outputs, completion criteria, and failure handling are defined by the corresponding stage-level and specialist `SKILL.md` files.
