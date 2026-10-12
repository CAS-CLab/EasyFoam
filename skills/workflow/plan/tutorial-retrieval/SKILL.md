---
name: workflow-tutorial-retrieval
description: Retrieve bounded read-only OpenFOAM-13 tutorial or Reference evidence for one planning decision.
---

# Tutorial Retrieval

## 1. Entry Conditions

Use only when `case-planning` has a concrete unresolved question about module mapping, dictionary family, required fields/models, boundary pattern, mesh sequence, or command sequence.

## 2. Required Inputs

- the exact planning question;
- relevant CaseSpec context;
- known physics/module/algorithm constraints;
- OpenFOAM version, module/application, physics family, algorithm, and special mesh/model features;
- local tutorial/reference roots.


## 3. Decision Procedure

1. Search the smallest relevant tutorial family or Reference index.
2. Filter by OpenFOAM version, physics, module, algorithm, geometry/mesh route, and required features.
3. Prefer official/local version-matched examples over approximate analogies.
4. Extract only the evidence needed for the planning question.
5. Record matching features, differences, and limitations.
6. Return the selected path, relevant pattern, applicability limits, and unresolved differences to `case-planning`.


## 4. Output Contract

Default output is stdout. Write a selection JSON only when explicitly requested. Do not create auxiliary selection manifests, copied tutorial workspaces, or unrelated provenance files by default. Never copy a complete tutorial into the production case from this Skill.

## 5. Completion Conditions

Pass when the selected pattern is version-compatible and its applicability differences are explicit, or when no-match is decisively reported.

## 6. Invariants

- Reference access is read-only.
- Retrieval does not make the final CaseSpec decision.
- A tutorial pattern is evidence, not ground truth for a different case.
- User scope, source provenance, and authoritative inputs are preserved.

## 7. Failure Routing

No suitable evidence returns an explicit unresolved result to `case-planning`. Version mismatch or conflicting examples remain visible; do not choose silently.

## 8. Scripts

```text
scripts/select_tutorial_reference.py  # stdout by default; optional --out
```

## 9. Conditional References

- `references/tutorial-selection-rules.md` for ranking and no-copy boundaries;
- `references/tutorial-index-format.md` for index fields;
- `skills/reference/tutorial_patterns/` for indexed patterns;
- the selected `skills/reference/tutorial_families/` and solver-module card.
