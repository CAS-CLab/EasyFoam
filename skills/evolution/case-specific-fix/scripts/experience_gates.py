"""Deterministic gates for manually recorded Workflow Experience.

This module belongs to the human-governed Experience workflow. It is not
imported by the automatic Minimal Evolution engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


_GATE_ALIASES = {
    "execution": ("execution_gate",),
    "numerical": ("numerical_gate",),
    "physical": ("physical_gate",),
    "physics_grounded_qoi": (
        "physics_grounded_qoi_gate",
        "physics_grounded_qoi_pass",
        "qoi_gate",
    ),
}


def _metadata(observation: dict[str, Any]) -> dict[str, Any]:
    value = observation.get("metadata", {})
    return value if isinstance(value, dict) else {}


def _gate_value(observation: dict[str, Any], name: str) -> Any:
    metadata = _metadata(observation)
    for key in _GATE_ALIASES[name]:
        if key in metadata:
            return metadata[key]
    return None


def _missing_acceptance_gates(observation: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for name in ("execution", "numerical", "physical", "physics_grounded_qoi"):
        if _gate_value(observation, name) is not True:
            missing.append(f"metadata.{name}_gate")
    return missing


def _verified_repair_evidence_missing(observation: dict[str, Any]) -> list[str]:
    pattern = observation.get("pattern", observation)
    before = pattern.get("before_sha256") or pattern.get("before")
    after = pattern.get("after_sha256") or pattern.get("after")
    missing: list[str] = []
    if not before:
        missing.append("pattern.before_sha256")
    if not after:
        missing.append("pattern.after_sha256")

    source_runs = observation.get("source_run_refs", [])
    metadata = _metadata(observation)
    before_gates = metadata.get("before_gates")
    if not isinstance(before_gates, dict) or not any(value is False for value in before_gates.values()):
        missing.append("metadata.before_gates_with_failure")
    rerun_refs = metadata.get("source_rerun_evidence_refs") or metadata.get("source_replay_refs")
    if not isinstance(rerun_refs, list) and not (isinstance(source_runs, list) and len(source_runs) >= 2):
        missing.append("source_rerun_evidence")
    elif isinstance(rerun_refs, list) and not rerun_refs and not (isinstance(source_runs, list) and len(source_runs) >= 2):
        missing.append("source_rerun_evidence")
    return missing


@dataclass(frozen=True)
class ExperienceDecision:
    status: str
    candidate_eligible: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "candidate_eligible": self.candidate_eligible,
            "reason": self.reason,
        }


def assess_observation(observation: dict[str, Any]) -> ExperienceDecision:
    """Assess a manually supplied observation against the Experience schema."""

    kind = observation.get("kind")
    if kind not in {"verified_repair", "successful_pattern", "failure_pattern", "unresolved_failure"}:
        return ExperienceDecision("invalid", False, "unsupported Experience kind")
    if kind == "unresolved_failure":
        return ExperienceDecision("unresolved", False, "unresolved failures are never Candidate-eligible")
    if observation.get("fault_injected") is True:
        return ExperienceDecision("ineligible", False, "fault-injected observations are not natural Experience")
    pattern = observation.get("pattern", observation)
    scope = observation.get("scope", observation)
    evidence_refs = observation.get("evidence_refs", [])
    missing = [key for key in ("outcome",) if not pattern.get(key)]
    if not evidence_refs:
        missing.append("evidence_refs")
    if not scope.get("applicability"):
        missing.append("applicability")
    if "exclusions" not in scope:
        missing.append("exclusions")
    if kind == "verified_repair":
        missing.extend(key for key in ("root_cause", "action") if not pattern.get(key))
        missing.extend(_verified_repair_evidence_missing(observation))
        missing.extend(_missing_acceptance_gates(observation))
    elif kind == "successful_pattern":
        missing.extend(_missing_acceptance_gates(observation))
    elif kind == "failure_pattern":
        unresolved = observation.get("unresolved", {})
        missing.extend(
            f"unresolved.{key}"
            for key in ("blocker", "attempted_actions", "remaining_risk", "next_action")
            if key not in unresolved or unresolved.get(key) in (None, "")
        )
    if missing:
        return ExperienceDecision("ineligible", False, "missing explicit fields: " + ", ".join(sorted(set(missing))))
    if observation.get("execution_only") is True:
        return ExperienceDecision("ineligible", False, "execution-only evidence cannot establish scientific reuse")
    if kind == "failure_pattern":
        return ExperienceDecision(
            "eligible_hypothesis",
            True,
            "natural failure evidence may trigger a hypothesis Candidate only; it is not a verified repair and requires matched validation",
        )
    return ExperienceDecision(
        "eligible",
        True,
        "execution, numerical, and physics-grounded acceptance plus reusable scope are explicitly evidenced",
    )


def compatible_observations(observations: Iterable[dict[str, Any]]) -> tuple[bool, str]:
    """Require one target and one shared applicability predicate."""

    rows = list(observations)
    if not rows:
        return False, "no observations"
    if not all(assess_observation(row).candidate_eligible for row in rows):
        return False, "one or more observations are not Candidate-eligible"
    targets = {row.get("responsible_skill") for row in rows}
    if len(targets) != 1:
        return False, "observations target different Skills"
    applicability = [set(row.get("scope", row).get("applicability", [])) for row in rows]
    if not set.intersection(*applicability):
        return False, "observations have no shared applicability predicate"
    return True, "observations are compatible for one atomic Candidate"
