# Evolution Artifact Contract

## Purpose

Keep Evolution auditable without creating a second workflow engine or a large collection of process files.

## Canonical artifacts

```text
<evolution_root>/
├── experiences/<experience_id>.json
├── candidates/<candidate_id>/candidate_patch.json
├── candidates/<candidate_id>/candidate.patch
└── decisions/<promotion_id>/promotion_record.json
```

Only actual apply or validation commands may additionally create stdout/stderr logs under the owning decision or isolated Workflow run.

## Authority and unique writers

| Artifact | Unique writer | Authority |
| --- | --- | --- |
| Experience record | `case-specific-fix` | One bounded Workflow observation and Candidate eligibility |
| Candidate record | `candidate-patch` | Scope, targets, hashes, risks, validation plan/results, evidence level |
| Candidate patch | `candidate-patch` | Exact frozen unified diff |
| Promotion record | `promoted-skill` | Human decision, application, post-apply validation, retention, rollback |

A Workflow replay used for Candidate validation writes ordinary `case_spec.json`, `workflow.json`, `run_record.json`, and `evidence_summary.json` in an isolated workspace. Candidate records reference those artifacts; they do not duplicate them.

## Path rules

- Store repository-relative or evolution-root-relative paths.
- Reject absolute paths, drive paths, and `..` traversal.
- Do not embed source-case directories, user home paths, temporary workspace paths, or machine-specific installation locations.
- Target paths are restricted to the explicitly reviewed library scope.

## Hash rules

- Experience may record before/after hashes when available, but hashes do not prove generality.
- Candidate records must store the SHA256 of the exact patch and the declared base/proposed hash of every target file.
- Application verifies current base hashes before modification and proposed hashes after modification.
- Rollback verifies restoration of declared base hashes.

## Immutability

- Workflow evidence referenced by Experience is not rewritten after capture.
- A frozen Candidate's patch, target list, scope, applicability, exclusions, and hashes are immutable.
- Any change to frozen Candidate content creates a new Candidate ID and preserves the old Candidate.
- Promotion records are append-by-state: decision, apply, validation, retention, and rollback update the same record without changing the original human decision.

## Artifact budget

Do not create by default:

```text
selection.json
cluster.json
normalized_signature.json
source_index.json
freeze_manifest.json
replay_result.json
replay_comparison.json
rollback.patch
merge_record.json
validation_report.json
retention_report.json
evolution.json
```

Compatibility inspection may print to stdout. User-requested reports may be created, but they are not canonical state.
