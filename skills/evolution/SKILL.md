---
name: evolution
description: Human-governed conversion of verified Workflow Experience into scoped, validated, reversible EasyFoam changes.
---

# Evolution

```text
Experience → Candidate → Review and Validation
→ Human Decision → Apply / Limit / Reject / Defer / Rollback
```

Evolution coordinates reusable system change. It does not repair the active CFD case, execute ordinary Workflow stages, or modify formal Skills or References without an explicit human decision.

## 1. Scope and Entry

Use Evolution only when the user explicitly requests review, reuse, distillation, validation, application, limitation, rejection, deferment, retention, or rollback of recorded Experience or a Candidate.

Passive Experience capture may be invoked by Workflow after verified evidence is available. That capture alone does not enter Candidate creation or authorize any system change.

Enter at:

| Situation | Entry |
| --- | --- |
| Record or inspect a verified repair, successful behavior, failure pattern, or unresolved failure | Experience |
| Create, revise, inspect, or validate a reusable change | Candidate |
| Record a human decision, apply an authorized Candidate, retain it, or roll it back | Decision and Application |

Do not infer permission to apply, retain, merge, commit, push, or roll back from an ambiguous request.

## 2. Canonical Contracts

Evolution uses three canonical records and one executable patch:

| Artifact | Authority |
| --- | --- |
| `experience_record.json` | One evidence-linked Workflow observation, verified repair, successful pattern, or unresolved failure |
| `candidate_patch.json` | Candidate scope, target files, patch hash, risks, validation plan, observed validation, and readiness |
| `candidate.patch` | Exact atomic unified diff proposed by the Candidate |
| `promotion_record.json` | Human decision, application result, post-apply validation, retention, limitation, and rollback state |

Default layout:

```text
<evolution_root>/
├── experiences/<experience_id>.json
├── candidates/<candidate_id>/
│   ├── candidate_patch.json
│   └── candidate.patch
└── decisions/<promotion_id>/
    ├── promotion_record.json
    └── logs/                         # only actual apply/validation command logs
```

Do not create separate selection, cluster, normalization, freeze, replay-comparison, rollback-patch, review-report, or Evolution-state JSON files by default.

Candidate validation reuses ordinary Workflow artifacts produced in isolated baseline and evolved workspaces. `candidate_patch.json` stores only their relative references and the supported conclusion.

## 3. Evolution Stage Contracts

| Stage | Owner | Successful when |
| --- | --- | --- |
| Experience | `skills/evolution/case-specific-fix/SKILL.md` | A schema-valid Experience accurately represents existing evidence and states Candidate eligibility |
| Candidate | `skills/evolution/candidate-patch/SKILL.md` | A scoped atomic patch is frozen, reversible, and supported by the validation actually performed |
| Decision and Application | `skills/evolution/promoted-skill/SKILL.md` | The human decision and any authorized apply, validation, retention, limitation, or rollback action are accurately recorded |

The stages are sequential but not automatic. An Experience does not create a Candidate; a Candidate does not authorize application; application does not imply retention or effectiveness.

## 4. Coordination and Governance

1. Bind the user request to specific Experience, Candidate, target files, and action.
2. Load only the active Evolution specialist and the narrowest governance References required.
3. Preserve source evidence and immutable Candidate patch content after freezing.
4. Require explicit human action before application, limited application, retention, or rollback.
5. Record actual results without converting missing evidence into PASS.
6. Stop at `deferred`, `rejected`, `blocked`, `invalid`, or `rolled_back` when the applicable contract is not satisfied.

Candidate changes may span multiple files only when they form one causal, reviewable, reversible change. Unrelated cleanup must be separated.

## 5. Validation and Claim Boundaries

Keep the following claims distinct:

- Experience quality;
- Candidate structural correctness;
- source replay support;
- compatible holdout support;
- negative-control behavior;
- post-apply compatibility;
- final retention status.

A patch that applies cleanly is not proven effective. Source replay does not prove generalization. A retained limited change must state its evidence limitation and scope restriction.

No injected fault may be recorded as natural Experience evidence. Validation may use clean negative controls and isolated baseline/evolved comparisons, but it must not fabricate Workflow history.

## 6. Evolution Outcome

For the user-requested scope, report the applicable terminal result:

- Experience: recorded, ineligible, or unresolved;
- Candidate: draft, frozen, validated, invalid, or superseded;
- Decision: apply, apply with limitations, revise, reject, or defer;
- Application: authorized, applied, failed, or rolled back;
- Retention: retained, retained with limitations, blocked, not applicable, or rolled back.

The final authoritative result is stored in the canonical artifact owned by the last requested stage. Evolution does not create a separate global state file.
