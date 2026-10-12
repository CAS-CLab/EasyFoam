---
name: evolution-case-specific-fix
description: Record bounded, evidence-linked Workflow Experience without generalizing or modifying formal Skills.
---

# Case-Specific Fix and Experience Capture

## 1. Entry Conditions

Use after Workflow has produced decisive evidence for one of the following:

- a verified natural case repair;
- a reusable successful behavior;
- a natural failure pattern with complete gate/run evidence that should drive a validation-bound hypothesis;
- an unresolved failure worth preserving.

Experience capture may occur passively from Workflow. It must not create a Candidate or modify a formal Skill or Reference.

## 2. Required Inputs

- the source `workflow.json`;
- applicable `run_record.json` and `evidence_summary.json` references;
- the responsible specialist Skill;
- a concise trigger, outcome, applicability boundary, and exclusions;
- for a verified repair: root cause, repair action, before/after hashes when available, and verification evidence;
- for an unresolved failure: blocker, attempted actions, remaining risk, and next action.

Use relative evidence references. Preserve case identity in the Experience record, but do not treat it as a reusable rule.

## 3. Decision Procedure

1. Confirm that the source evidence exists and represents a natural Workflow result rather than an injected fault.
2. Separate the observed symptom, root cause, action, verification outcome, and unrelated warnings.
3. Classify the Experience as `verified_repair`, `successful_pattern`, `failure_pattern`, or `unresolved_failure`.
4. Define applicability and exclusions narrowly enough to prevent case-specific details from becoming generic behavior.
5. Set `candidate_eligible=true` for verified reusable observations or an evidence-complete `failure_pattern` hypothesis with an identifiable responsible Skill. The latter is proposal input, not proof of a repair.
6. Keep `unresolved_failure` and weakly supported observations ineligible instead of overstating confidence.
7. Write and validate the canonical Experience record.

## 4. Output Contract

Write exactly one default artifact:

```text
<evolution_root>/experiences/<experience_id>.json
```

It must validate against `schemas/experience_record.schema.json`.

Do not create a separate failure-signature, fix-trace, diff-summary, Experience report, or selection file. Existing Workflow artifacts remain the evidence source.

## 5. Completion Conditions

- the Experience schema passes;
- all stored references are portable relative paths;
- the kind matches the evidence;
- Candidate eligibility is explicit and justified;
- no Candidate, patch, or promotion record is created.

## 6. Invariants

- Never label an unverified repair as verified.
- Never record injected faults as natural Experience evidence.
- Preserve case-local values, paths, geometry names, and one-off constants only as source context, not reusable instructions.
- Do not modify Workflow evidence after capture.
- Experience quality and Candidate suitability are separate claims.

## 7. Failure Routing

If evidence is incomplete or contradictory, record `unresolved_failure` when useful or do not create an Experience. A complete natural failure with explicit failed gates may be recorded as `failure_pattern`, but any Candidate it triggers still requires matched validation. Return to the responsible Workflow stage when additional verification is required.

## 8. Scripts

```text
scripts/record_experience.py
```

Use `scripts/record_experience.py` to normalize, validate, and write the canonical Experience record. The script accepts a JSON descriptor from a file or standard input and does not create other process files.

## 9. Conditional References

- `skills/reference/evolution/experience-policy.md` for kinds and eligibility;
- `skills/reference/evolution/artifact-contract.md` for paths, ownership, and artifact budget;
- responsible Workflow specialist contract and referenced canonical evidence.
