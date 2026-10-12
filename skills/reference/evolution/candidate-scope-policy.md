# Candidate Scope Policy

## Atomicity

A Candidate is one causal, reviewable, reversible behavior change. Multiple files are allowed only when each edit is necessary for the same contract change, for example:

- a Skill instruction plus the script that implements it;
- a Schema change plus all scripts that read or write the changed field;
- a Reference rule plus the specialist declaration that routes to it;
- a routing change plus the corresponding specialist entry contract.

Unrelated cleanup, formatting, renaming, dead-code removal, and policy changes belong in separate Candidates unless they are required to make the same behavior coherent.

## Required scope description

The Candidate must state:

- recurring problem pattern;
- behavior before and after;
- primary target and every target file;
- applicability predicates;
- explicit exclusions and unsupported contexts;
- expected false-positive and compatibility risks;
- validation plan matching the intended claim;
- exact rollback method.

## Generalization rules

Generalize the causal rule, not the source case. Replace case-local names with typed predicates such as:

- “the CaseSpec requires an MRF cellZone whose explicit name is unresolved” rather than “zone `rotor` is missing”;
- “a required species field family lacks an actual species inventory” rather than “add `Yi`”;
- “the selected module requires a model-specific energy variable” rather than “always add `T`”.

Do not generalize when multiple causes remain plausible or when the correction only compensates for a bad case input.

## Target boundaries

Allowed targets are explicitly reviewed paths under `skills/` or `schemas/`. Validation or repository metadata may be included only when part of the same reviewed change. Evolution records, user cases, historical runs, generated results, private paths, and active decision directories are not Candidate targets.

## Applicability and exclusions

Applicability should be testable from canonical artifacts or deterministic repository state. Exclusions should name nearby contexts where the change must not trigger. Avoid vague terms such as “similar cases” or “usually”.

## Freeze and revision

Before freezing, review the complete diff, target hashes, scope, risks, and validation plan. Once frozen, any patch or scope edit creates a new Candidate ID. Mark the previous Candidate `superseded` only with an explicit reference in the new review context.
