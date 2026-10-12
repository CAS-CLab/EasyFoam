---
name: evolution-candidate-patch
description: Distill compatible verified Experience into an atomic, scoped, validated, reversible Candidate patch.
---

# Candidate Patch

## 1. Entry Conditions

Use only after the user explicitly requests Candidate creation, revision, inspection, or validation.

At least one Candidate-eligible Experience is required. Multiple Experiences may be combined only when their responsible target, causal pattern, repair logic, applicability, and exclusions are compatible.

## 2. Required Inputs

- selected `experience_record.json` references;
- an explicit Candidate target and user-requested scope;
- an isolated base tree and edited tree, or an equivalent reviewed proposed change;
- problem pattern, behavior before/after, applicability, exclusions, and risks;
- a validation plan covering the evidence needed for the intended claim.

Declare `candidate_type` in the builder metadata: `behavioral`,
`documentation_only`, or `diagnostic`. For `behavioral` candidates (the default),
declare a non-empty `touched_runtime_surface` list containing only declared
target paths. A `documentation_only` candidate may target only Skill/Reference
text and must not declare a runtime surface. The validation plan must contain
exactly `structural`, `source_replay`, `holdout`, `negative_controls`,
`compatibility`, and `cross_scope`; `structural` must be enabled.

The target may include Skill, Reference, script, or Schema files under `skills/` or `schemas/` when they form one atomic change. Validation commands and their evidence artifacts are validation evidence, not formal Candidate targets.

## 3. Decision Procedure

1. Validate selected Experiences and reject ineligible, unresolved, incompatible, or unrelated records.
2. Identify the smallest causal change that addresses the repeated behavior without embedding case identities, case-specific answers, private paths, or one-off values.
3. Declare all target files before generating the patch. Separate unrelated cleanup into another Candidate.
4. Generate one real unified diff from the isolated base and edited trees.
5. Record base and proposed hashes for every target file.
6. Define applicability, exclusions, false-positive risk, backward-compatibility risk, and the rollback method.
7. Validate schema, patch hash, base hashes, `git apply --check`, exact proposed hashes, and reverse application in an isolated tree.
8. Freeze the Candidate patch and substantive scope after structural validation. Validation metadata may advance without changing the frozen patch.
9. Run matched baseline/evolved validation through the ordinary Workflow where required.
10. Record source, holdout, negative-control, compatibility, or cross-scope results in `candidate_patch.json` using relative references to the actual Workflow evidence.
11. Set the evidence level from performed validation only. Missing validation remains visible and does not block human review unless required by the intended action.

## 4. Output Contract

Write only:

```text
<evolution_root>/candidates/<candidate_id>/candidate_patch.json
<evolution_root>/candidates/<candidate_id>/candidate.patch
```

The Candidate record must validate against `schemas/candidate_patch.schema.json`.

Do not create separate selection, cluster, normalized-signature, source-index, freeze-manifest, replay-result, comparison, rollback-patch, or review-report artifacts by default.

The same `candidate.patch` is reversed for rollback.

## 5. Completion Conditions

A Candidate is structurally frozen when:

- all source Experiences are eligible and compatible;
- every target path and base hash is declared;
- the patch hash matches;
- forward and reverse checks pass in isolation;
- applying the patch yields the declared proposed hashes;
- scope, exclusions, risks, and validation plan are explicit.

A Candidate is `validated` only when every enabled validation-plan item is recorded as `passed` and the resulting evidence level is supported. A failed enabled validation item marks the Candidate `invalid`; `limited`, `blocked`, or `not_run` evidence keeps it `frozen`. Any `passed`, `failed`, or `limited` validation result must reference the actual evidence artifact. Validation does not authorize application.

## 6. Invariants

- No automatic Candidate creation from a single Workflow result.
- No automatic application, merge, commit, or push.
- No case identity, case path, geometry-specific assumption, or private machine path in generic Candidate behavior.
- Frozen patch content, target set, base/proposed hashes, scope, risks, and rollback method are immutable. Validation results, evidence level, status, and updated_at may advance without changing the frozen patch. Any substantive revision requires a new Candidate ID.
- No unrelated file edits in one Candidate.
- Patch correctness, behavioral effectiveness, and generalization remain separate claims.

## 7. Failure Routing

- incompatible Experience → return to Experience selection or defer;
- unclear reusable rule → keep Experience without creating a Candidate;
- invalid patch or hash mismatch → mark Candidate `invalid` and revise in a new Candidate;
- failed source replay → revise or reject;
- failed holdout or negative control → narrow applicability, apply only with explicit limitations, revise, or reject;
- missing evidence → preserve the current evidence level and defer the unsupported claim.

## 8. Scripts

- `scripts/inspect_experiences.py`: validate eligibility and compatibility; output findings to stdout only;
- `scripts/build_candidate.py`: generate `candidate.patch` and `candidate_patch.json` from isolated base/edited trees;
- `scripts/validate_candidate.py`: perform forward/reverse structural validation and freeze the Candidate in place;
- `scripts/record_validation.py`: append evidence-linked Workflow validation results, reject evidence claims without references, and update Candidate status and evidence level according to the enabled validation plan.

## 9. Conditional References

- `skills/reference/evolution/candidate-scope-policy.md` for atomicity/generalization;
- `skills/reference/evolution/validation-policy.md` for cumulative evidence levels;
- `skills/reference/evolution/artifact-contract.md` for targets, hashes, immutability, and artifact budget;
- source Experiences and responsible specialist/Reference contracts.
