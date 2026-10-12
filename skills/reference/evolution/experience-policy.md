# Experience Eligibility Policy

## Purpose

An Experience preserves one bounded, evidence-linked Workflow result. It is evidence for later review, not a general rule and not permission to modify the library.

## Experience kinds

### `verified_repair`

Use only when:

- the failure occurred naturally in the user-scoped Workflow;
- the first decisive cause is identified;
- the repair is bounded and attributable to a responsible specialist;
- the original defect is reproduced or otherwise decisively evidenced;
- the repair passes the narrowest verification that addresses that defect;
- remaining warnings and limitations are recorded separately.

A verified repair may still be Candidate-ineligible when it is tied to a one-off patch name, geometry, path, user value, corrupt file, or local environment detail.

### `successful_pattern`

Use for a behavior that succeeded without a preceding repair when the behavior is reusable and supported by decisive evidence. Examples include a reliable ordering rule, static consistency check, or evidence-gathering procedure. A single successful case does not prove broad applicability.

### `unresolved_failure`

Use when the failure, attempts, and remaining risk are useful but the root cause or repair is unverified. This kind is always Candidate-ineligible.

### `failure_pattern`

Use when a natural failure has complete run/evidence references and explicit
failed execution, numerical, physical, timeout, or resource gates, but no repair
has yet been verified. This kind is Candidate-input eligible only as a clearly
labelled hypothesis. It may suggest a bounded defensive Skill change; it never
proves that change correct. Matched validation must establish execution,
numerical, physical, QoI, and operational behavior before acceptance.

## Candidate eligibility

Set `candidate_eligible=true` only when all are satisfied:

1. evidence references exist and are portable;
2. the behavior is verified, or the record is an evidence-complete `failure_pattern` whose unverified status is explicit;
3. a responsible Skill, Reference, script, or Schema target can be identified;
4. applicability predicates and explicit exclusions can be stated;
5. the change would improve reusable behavior rather than encode a case answer;
6. source evidence is natural, not fault-injected or fabricated;
7. known alternative causes have been ruled out sufficiently for the intended scope.

The record must include a plain-language `eligibility_reason`. `verified_repair`, `successful_pattern`, and `failure_pattern` are not automatically eligible.

## Case-specific information

Preserve source-case identifiers only as provenance. Do not turn these into generic instructions:

- patch, zone, region, phase, or species names;
- one-off dimensions, properties, controls, or thresholds;
- local paths or environment setup;
- user-specific geometry assumptions;
- a solver choice that was valid only because of unstated case context.

Such information may appear in applicability or exclusions only when it is a genuine predicate.

## Evidence quality examples

| Evidence | Suitable claim |
| --- | --- |
| Parser error plus corrected syntax | Static repair for that syntax family |
| Solver completes after an unrelated change | Does not verify the proposed root cause |
| Source run before/after under matched conditions | Source support, not generalization |
| Two independent natural cases with the same cause and fix | Repeated source support |
| An unresolved log with no verified correction | Unresolved Experience only |

## Exclusions

Do not record injected faults as natural Experience. Controlled negative cases may be used during Candidate validation, but not rewritten as historical Workflow failures.
