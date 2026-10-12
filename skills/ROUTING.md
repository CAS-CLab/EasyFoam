# EasyFoam Routing

Use the smallest applicable Skill set. Paths below are relative to `skills/` and omit the trailing `/SKILL.md`.

This file routes an explicit user request or current system state to an EasyFoam Workflow or Evolution stage and specialist Skill.

Detailed stage responsibilities, internal routing, handoffs, inputs, procedures, References, scripts, outputs, completion criteria, and failure handling are defined by the corresponding stage-level and specialist `SKILL.md` files.

Knowledge-only requests are routed directly by the root Skill to `reference/SKILL.md` and are not repeated here.

Routing follows this sequence:

```text
User target or intent
→ Workflow / Evolution
→ Stage or function
→ Specialist Skill
```

## Routing Principles

1. Explicit user targets take precedence.
2. New simulation starts at Plan.
3. Existing work resumes from the earliest affected stage.
4. Do not repeat valid earlier stages.
5. Evolution requires explicit user intent.
6. Load only the active stage and specialist required by the current route.

# Workflow Loop

```text
Plan → Write → Run → Postprocess
```

## Plan Routes

| User intent or current state | Specialist Skill |
| --- | --- |
| Construct a new simulation from user requirements; complete, revise, or audit a CaseSpec; or reconstruct a CaseSpec only when an existing case has no reusable CaseSpec | `workflow/plan/case-planning` |
| Retrieve a local OpenFOAM tutorial, solver-family example, module pattern, or dictionary pattern needed during planning | `workflow/plan/tutorial-retrieval` |

## Write Routes

| User intent or current state | Specialist Skill |
| --- | --- |
| Generate, update, audit, or repair fields, dictionaries, physical models, numerical settings, solver algorithms, or run controls | `workflow/write/case-authoring` |
| Generate or repair a mesh constructed from geometry and mesh requirements | `workflow/write/mesh-generation` |
| Import, convert, inspect, map, or repair a user-provided mesh or existing `constant/polyMesh` | `workflow/write/mesh-import` |

## Run Routes

| User intent or current state | Specialist Skill |
| --- | --- |
| Run, resume, or re-run an OpenFOAM case | `workflow/run/runner` |
| Diagnose or repair a failed command, dictionary error, field error, mesh failure, solver failure, physical-model inconsistency, or invalid runtime state | `workflow/run/debug-reviewer` |

A verified repair returns to the earliest affected Workflow stage.

## Postprocess Routes

| User intent or current state | Specialist Skill |
| --- | --- |
| Assess requirement fidelity, mesh credibility, numerical behavior, physical credibility, conservation, or requested QoIs | `workflow/postprocess/physics-validation` |
| Extract residuals, probes, forces, sampled fields, derived quantities, tables, exports, or reports  | `workflow/postprocess/postprocessing` |
| Generate mesh views, contours, slices, surfaces, vectors, streamlines, or temporal visual diagnostics | `workflow/postprocess/visual-diagnostics` |
| Summarize an existing Workflow from canonical artifacts | `workflow/postprocess` |

# Evolution Loop

```text
Experience
→ Candidate
→ Review and Validation
→ Human Decision
→ Apply / Limit / Reject / Defer / Rollback
```

| User intent or current state | Evolution stage | Specialist Skill |
| --- | --- | --- |
| Record, inspect, or summarize a verified case repair, reusable successful behavior, or unresolved failure | Experience | `evolution/case-specific-fix` |
| Select, compare, distill, inspect, revise, or validate Experience and Candidate changes | Candidate | `evolution/candidate-patch` |
| Apply, limit, revise, reject, defer, validate, retain, or roll back a Candidate | Decision and Application | `evolution/promoted-skill` |

The Evolution stages are sequential but not automatic:

```text
record Experience
→ create and validate Candidate
→ record human decision
→ apply Candidate when explicitly requested
→ retain, limit, or roll back
```

* Recording Experience does not automatically create a Candidate.
* Creating or validating a Candidate does not automatically apply it.
* Decision, application, post-application validation, and retention are separate actions.


