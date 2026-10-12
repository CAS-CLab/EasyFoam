"""Shared compatibility analysis for Candidate-eligible Experience records."""
from __future__ import annotations

import re
from typing import Any


def _norm(value: str | None) -> str | None:
    if value is None:
        return None
    return re.sub(r"\s+", " ", value.strip().lower()) or None


def inspect_rows(rows: list[dict[str, Any]], existing_errors: list[str] | None = None) -> dict[str, Any]:
    errors = list(existing_errors or [])
    review_reasons: list[str] = []
    if not rows:
        errors.append("no valid Experience record was supplied")

    responsible = sorted({row["responsible_skill"] for row in rows})
    kinds = sorted({row["kind"] for row in rows})
    if len(responsible) > 1:
        errors.append(f"selected Experiences identify multiple responsible Skills: {responsible}")

    applicability_sets = [set(row["scope"]["applicability"]) for row in rows]
    shared = sorted(set.intersection(*applicability_sets)) if applicability_sets else []
    if rows and not shared:
        review_reasons.append("selected Experiences have no shared applicability")

    exclusions = sorted({item for row in rows for item in row["scope"]["exclusions"]})
    conflicting_scope = sorted(set(shared) & set(exclusions))
    if conflicting_scope:
        errors.append(f"shared applicability is excluded by at least one Experience: {conflicting_scope}")

    root_causes = sorted({_norm(row["pattern"].get("root_cause")) for row in rows if _norm(row["pattern"].get("root_cause"))})
    actions = sorted({_norm(row["pattern"].get("action")) for row in rows if _norm(row["pattern"].get("action"))})
    triggers = sorted({_norm(row["pattern"].get("trigger")) for row in rows if _norm(row["pattern"].get("trigger"))})
    outcomes = sorted({_norm(row["pattern"].get("outcome")) for row in rows if _norm(row["pattern"].get("outcome"))})
    if len(root_causes) > 1:
        errors.append("selected Experiences describe different root causes")
    if len(actions) > 1:
        errors.append("selected Experiences describe different repair actions")
    failure_context = any(row.get("kind") == "failure_pattern" for row in rows)
    if len(triggers) > 1 and not failure_context:
        review_reasons.append("trigger descriptions differ and require causal review")
    if len(outcomes) > 1 and not failure_context:
        review_reasons.append("outcome descriptions differ and require causal review")

    if errors:
        status = "incompatible"
    elif review_reasons:
        status = "review_required"
    else:
        status = "compatible"
    return {
        "status": status,
        "experience_count": len(rows),
        "responsible_skills": responsible,
        "kinds": kinds,
        "shared_applicability": shared,
        "combined_exclusions": exclusions,
        "review_required": bool(review_reasons),
        "review_reasons": review_reasons,
        "errors": errors,
    }
