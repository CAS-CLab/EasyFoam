---
name: workflow-plan
description: Coordinate CaseSpec construction and bounded reference retrieval.
---

# Plan

Plan converts the user requirement into an auditable CFD contract. It does not write OpenFOAM case files or run OpenFOAM commands.

## 1. Preconditions

Use either the current natural-language user requirement or a user-provided requirement TXT path, plus user-provided artifacts, an optional existing `case_spec.json`, and only the bounded References needed for the current planning decision. Do not require a copied `user_requirement.txt` inside the run directory.

## 2. Specialist Routing

| Need | Specialist |
| --- | --- |
| Build, revise, reconstruct, or audit the CaseSpec | `workflow/plan/case-planning` |
| Retrieve a solver-family, tutorial, dictionary, or module pattern needed to resolve planning evidence | `workflow/plan/tutorial-retrieval` |

`case-planning` remains the Plan authority. `tutorial-retrieval` supplies bounded evidence and returns to `case-planning`; it never writes the final CaseSpec decision by itself.

## 3. Orchestration

1. Bind the exact user-scoped requirement and artifacts.
2. Invoke `case-planning`.
3. Invoke `tutorial-retrieval` only when a concrete planning decision needs additional evidence.
4. If `case-planning` returns open blocking review items, consolidate them into the minimum set of concrete user questions and keep Workflow blocked in Plan.
5. After the user replies, revise the same CaseSpec, resolve the corresponding review items, and rerun schema and semantic release checks. Ask again only if decisive ambiguity remains.
6. Accept the schema-valid and semantically releasable `case_spec.json`, or stop with an explicit blocker.
7. Record the Plan outcome and `case_spec.json` reference in `workflow.json`.

## 4. Stage Result

Plan creates or updates only `case_spec.json` and `workflow.json`. Parsing and audit scripts write to stdout unless the user explicitly requests a separate report.

Plan succeeds when `case_spec.json` passes schema and semantic release checks with no unresolved decisive requirement.

## 5. Failure and Return Routing

Missing or contradictory decisive input remains blocked in Plan. A later change to a decisive planning decision returns to Plan and invalidates only dependent downstream evidence.
