---
name: workflow
description:  Execute OpenFOAM-13 tasks through Plan, Write, Run, and Postprocess.
---

# Workflow

```text
Plan → Write → Run → Postprocess
```

This Skill is the top-level coordinator for the EasyFoam Workflow Loop. It manages stage selection, progression, recovery, completion, and passive Experience capture. It does not perform specialist CFD work. Instead, it selects the active stage, enforces cross-stage contracts, coordinates stage transitions and recovery routing, and maintains a single canonical `workflow.json` as the authoritative Workflow state.

## 1. Scope and Entry

Use Workflow for a user-scoped OpenFOAM case or run that must be created, resumed, repaired, executed, validated, postprocessed, visualized, or summarized. A new requirement may come directly from the current user message or from a user-provided TXT path; a copied requirement file inside the run directory is not required.

| Situation | Entry |
| --- | --- |
| New simulation with no reusable CaseSpec or case | Plan |
| Existing CaseSpec but no complete case | Write |
| Complete case and mesh with no decisive run result | Run |
| Completed or inspectable run with missing evidence | Postprocess |
| Explicit stage request | Requested stage after prerequisite verification |
| Failure or repair | Earliest affected stage, not automatically Plan |

Preserve earlier stages whose artifacts and decisive checks remain valid.

## 2. Artifact and Schema Contract

A Workflow uses the following fixed records:

| Record | Required when | Schema / rule |
| --- | --- | --- |
| `case_spec.json` | Plan is in scope | `schemas/case_spec.schema.json` |
| `workflow.json` | Always | `schemas/workflow.schema.json` |
| `runs/<attempt_id>/run_record.json` | A preprocessing or solver attempt is executed | `schemas/run_record.schema.json` |
| `evidence_summary.json` | Postprocess or final evidence assessment is in scope | `schemas/evidence_summary.schema.json` |
| `experiences/<experience_id>.json` | Passive Experience is explicitly retained | `schemas/experience_record.schema.json` |

The formal OpenFOAM case remains under `case/`. Requested tables, plots, exports, and images are written under `results/` or another user-approved relative path.

Do not create separate parsed-requirement, handoff, invalidation, check, runtime-metrics, visual-contract, visual-manifest, or generic report JSON files by default. Intermediate calculations stay in memory or stdout unless they are required command logs, user-requested outputs, or decisive evidence that cannot be reconstructed.

Each executed command may create only its stdout/stderr logs referenced by the corresponding `run_record.json`. `workflow.json` stores final coordination state and evidence references, not detailed specialist histories.

## 3. Workflow Stage Contracts

Each stage-level Skill selects and coordinates its specialists. Specialist Skills perform the concrete CFD work.

| Stage | Purpose / Owner  | Successful when |
| --- | --- | --- |
| Plan | Convert requirements into a CaseSpec → `skills/workflow/plan/SKILL.md` | `case_spec.json` is schema-valid, internally consistent, and contains no unresolved decisive requirement |
| Write | Materialize the OpenFOAM case and mesh → `skills/workflow/write/SKILL.md` | Required files and mesh are consistent with the released `case_spec.json` |
| Run | Execute the requested case → `skills/workflow/run/SKILL.md` | The requested execution has a decisive terminal result and required runtime evidence |
| Postprocess | Validate, derive, report, and visualize evidence → `skills/workflow/postprocess/SKILL.md` | Requested evidence and a schema-valid `evidence_summary.json` are available |

A stage that cannot meet its success condition terminates as `failed` or `blocked`. A stage may be skipped only when it is outside the requested scope or demonstrably not applicable.

`skills/ROUTING.md` maps the user intent or current state to the active stage and specialist Skill.

## 4. Workflow State

`workflow.json` records only the minimum state required to coordinate, resume, and conclude the Workflow:

- the user-scoped target;
- the active or last stage and active specialist;
- the overall status and completed scope;
- references to the formal case, run records, evidence summary, requested outputs, and decisive evidence;
- unresolved limitations or blockers;
- the next action when further work is required.

Use the following overall statuses:

- `in_progress`: further Workflow action is required and a valid next step exists;
- `succeeded`: the requested scope completed successfully;
- `failed`: a required action was attempted but its contract was not satisfied;
- `blocked`: progress requires missing information, input, permission, capability, or required artifacts.

Detailed checks, warnings, repairs, and command results belong to the responsible specialist output, `run_record.json`, raw logs, or `evidence_summary.json`.

## 5. Stage Coordination and Recovery

1. Select the earliest required stage.
2. Load the stage Skill and applicable specialist.
3. Accept the stage result and referenced evidence.
4. Use the ledger `advance` operation to atomically complete and route a stage, or `reopen` to invalidate the earliest affected completed stage and its downstream claims before returning to it.
5. Advance, return to an affected stage, or terminate the Workflow.

Each receiving stage verifies its own prerequisites. Immutable run records remain available for audit after reopening, but superseded stage-scoped evidence must not support the current outcome.

Problems found during `Plan` or `Write` remain with the stage that detects them. Use `skills/workflow/run/debug-reviewer/SKILL.md` for failed preprocessing commands, solver commands, or invalid runtime states.

A verified repair or credibility finding returns to the earliest affected stage. Rerun only that stage and dependent downstream work. Superseded evidence may be retained for audit but must not support the final outcome.

## 6. Workflow Outcome

The Workflow outcome is assessed against the user-requested scope, not against stages that were not requested or applicable.

* `succeeded`: all applicable stage contracts within the requested scope are satisfied, with required artifacts and decisive evidence available;
* `failed`: a required action was attempted but its contract could not be satisfied;
* `blocked`: progress cannot continue due to missing information, input, permission, capability, or required artifacts;
* `in_progress`: further action is required and a valid next step exists.

A stage-scoped request may be marked `succeeded` when that stage satisfies its contract. This does not imply completion of an unrequested end-to-end Workflow.

Limited, unavailable, or skipped results do not automatically fail the Workflow. They only affect the outcome if they prevent satisfying the requested scope.

At termination, record the final status, completed scope, decisive evidence, unresolved limitations or blockers, and next action (if any).

Workflow may record evidence-linked Experience after termination, but must not automatically start Evolution or modify formal Skills or References.

## 7. Scripts

Use `skills/workflow/scripts/workflow_ledger.py` to initialize, route, atomically `advance`, `reopen` an affected stage, update artifact references, record stage-scoped decisive evidence or blockers, and finalize `workflow.json`. The script validates every write against `schemas/workflow.schema.json` version `2.2`.
