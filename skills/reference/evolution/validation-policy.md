# Evolution Validation Policy

## Principle

Validation must match the Candidate claim. Patch correctness, source effectiveness, generalization, compatibility, and retention are separate claims.

## Validation categories

### Structural

Required for every Candidate before behavioral validation:

- Candidate and Experience Schemas pass;
- patch SHA256 matches the frozen patch;
- current base hashes match declared hashes;
- `git apply --check` or equivalent forward check passes;
- applied files match proposed hashes;
- reverse check passes;
- reversal restores base hashes;
- all referenced Skill, script, Schema, and Reference paths exist after application.

Structural PASS proves only that the Candidate is well-formed and reversible.

### Source replay

Compare baseline and evolved behavior under matched source-compatible conditions. Preserve the same requirement, case inputs, formal controls, environment class, and evaluation procedure. The evolved result must correct the target defect without invalidating unrelated required behavior.

### Holdout

Use independently selected cases that satisfy the declared applicability predicates but were not used to formulate the Candidate. Holdout evidence should exercise meaningful variation in geometry, physics subtype, names, or controls while retaining the causal condition.

### Negative controls

Use clean cases outside or near the applicability boundary. Confirm that the new rule does not trigger falsely, reject valid inputs, broaden required clarification, or degrade prior successful behavior. Negative controls are not injected-fault Experience.

### Compatibility

Check all contracts touched by the patch, including:

- Skill front matter and links;
- referenced scripts and References;
- Python import paths and CLI compatibility;
- JSON Schema validation and version fields;
- artifact-budget rules;
- root/ROUTING boundaries;
- existing supported modules and stage handoffs.

### Cross-scope

Use only when claiming broader support than the initial family. Explicitly name the additional module, physics family, operating environment, or artifact subtype. Cross-scope PASS is not inferred from holdout diversity.

## Evidence levels

Evidence levels are cumulative:

| Level | Minimum support |
| --- | --- |
| `E0_OBSERVATION` | Pre-Candidate observation only; it is not stored as a Candidate evidence level |
| `E1_VERIFIED_SOURCE` | At least one eligible verified Experience |
| `E2_REPEATED_SOURCE` | At least two compatible independent eligible Experiences |
| `E3_SOURCE_REPLAY` | E2 + structural PASS + source replay PASS |
| `E4_HOLDOUT_SUPPORT` | E3 + holdout PASS + negative PASS + compatibility PASS |
| `E5_CROSS_SCOPE_SUPPORT` | E4 + explicit cross-scope PASS |

Canonical Candidate records begin at E1. A missing, blocked, limited, or failed prerequisite prevents the higher level. A higher evidence level never authorizes application by itself.

## Outcome handling

- Missing execution is `not_run`, not PASS.
- Incomplete evidence is `limited` or `blocked`.
- A patch that applies cleanly but has no source replay remains structural only.
- A source replay that fixes the source case but fails negative controls must not claim holdout support.
- Validation records reference ordinary Workflow artifacts instead of creating parallel replay records.
