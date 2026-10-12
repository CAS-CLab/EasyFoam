# Promotion, Retention, and Rollback Policy

## Separate decisions

Keep these actions distinct:

1. human review of Candidate evidence;
2. decision to apply, apply with limitations, revise, reject, or defer;
3. exact patch application;
4. post-apply validation;
5. retention or limited retention;
6. rollback.

Review or validation does not imply authorization. Application does not imply effectiveness or retention.

## Human decisions

| Action | Meaning |
| --- | --- |
| `apply` | Authorize exact frozen Candidate application to the declared target |
| `apply_limited` | Authorize exact application under stated scope/evidence limitations |
| `revise` | Require a new Candidate; do not modify the target |
| `reject` | Close the Candidate for the reviewed purpose |
| `defer` | Preserve the Candidate pending evidence, timing, or ownership |

The reviewer and reason are required. `apply_limited` requires explicit limitations.

## Application gate

Before modification:

- verify the decision authorizes apply;
- validate Candidate Schema and status;
- verify patch hash and target paths;
- verify current target base hashes;
- run forward patch check;
- ensure the target repository is the explicitly requested one.

Apply the exact frozen patch. Record pre/post hashes and actual command logs. Do not silently edit around a patch conflict. Do not automatically commit, merge, push, or publish.

## Post-apply validation

Run the declared applicable repository and Workflow checks. Store only actual logs and canonical evidence references. If no validation command is run, status remains `not_run`. A failed or blocked validation prevents normal retention.

## Retention

- `retained`: application succeeded and required post-apply validation passed.
- `retained_limited`: application succeeded; validation passed or is explicitly limited; limitations and reviewer rationale are recorded. The original decision may have been `apply` or `apply_limited` if post-apply evidence narrowed the supported scope.
- `blocked`: evidence or target state cannot support a retention decision.
- `not_applicable`: revise, reject, or defer did not apply the Candidate.
- `rolled_back`: exact Candidate reversal succeeded and base hashes were restored.

## Rollback

Rollback requires explicit instruction. Verify the same frozen patch hash, run reverse check, reverse that exact patch, and verify declared base hashes. Do not create a separate rollback patch. If reverse application is unsafe because the target changed independently, block and require manual review rather than overwriting unrelated edits.

## Failure handling

Application or rollback failure is recorded in the same Promotion record. Preserve the patch, human decision, logs, pre/post hashes, and failure reason. Do not rewrite the decision to make the record appear successful.
