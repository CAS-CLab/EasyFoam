"""Shared integrity gates for canonical Evolution artifacts."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills._shared.scripts.artifact_io import read_json
from skills._shared.scripts.hashing import sha256_file
from skills._shared.scripts.schema_validate import validate

ALLOWED_TARGET_PREFIXES = ("skills/", "schemas/")
FORBIDDEN_TARGET_PARTS = {".git", "archive", "experiences", "candidates", "decisions"}


def resolve_inside(root: Path, value: str | Path, *, must_exist: bool = True) -> Path:
    resolved_root = root.resolve(strict=True)
    path = Path(value)
    candidate = path if path.is_absolute() else resolved_root / path
    resolved = candidate.resolve(strict=must_exist)
    if not resolved.is_relative_to(resolved_root):
        raise ValueError(f"path escapes declared root: {value}")
    return resolved


def relative_inside(root: Path, path: Path) -> str:
    return resolve_inside(root, path).relative_to(root.resolve(strict=True)).as_posix()


def validate_target_ref(value: str) -> str:
    normalized = value.replace("\\", "/")
    path = Path(normalized)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"invalid Candidate target path: {value}")
    if not normalized.startswith(ALLOWED_TARGET_PREFIXES):
        raise ValueError(f"Candidate target is outside the active EasyFoam library scope: {value}")
    if any(part in FORBIDDEN_TARGET_PARTS for part in path.parts):
        raise ValueError(f"forbidden Candidate target path: {value}")
    return path.as_posix()


def _load_valid(path: Path, schema_path: Path, label: str) -> dict[str, Any]:
    errors = validate(path, schema_path)
    if errors:
        raise ValueError(f"invalid {label} {path}: " + "; ".join(errors))
    return read_json(path)


def load_valid_candidate(evolution_root: Path, candidate_path: Path) -> tuple[dict[str, Any], Path, Path]:
    root = evolution_root.resolve(strict=True)
    path = resolve_inside(root, candidate_path)
    candidate = _load_valid(path, Path(__file__).resolve().parents[3] / "schemas" / "candidate_patch.schema.json", "Candidate")
    for change in candidate["target_changes"]:
        validate_target_ref(change["path"])
    if candidate["primary_target"] not in {item["path"] for item in candidate["target_changes"]}:
        raise ValueError("Candidate primary_target is not present in target_changes")
    patch_path = resolve_inside(root, candidate["patch_ref"])
    if sha256_file(patch_path) != candidate["patch_sha256"]:
        raise ValueError("Candidate patch hash mismatch")
    return candidate, path, patch_path


def validate_candidate_experience_refs(
    evolution_root: Path,
    candidate: dict[str, Any],
) -> list[dict[str, Any]]:
    """Load and validate the Experience records that produced a Candidate.

    Candidate eligibility is a persisted scientific gate, not a claim carried
    only in the Candidate manifest.  This helper is intentionally shared by
    adapter-backed campaigns and Promotion validation.
    """
    root = evolution_root.resolve(strict=True)
    schema = Path(__file__).resolve().parents[3] / "schemas" / "experience_record.schema.json"
    experiences: list[dict[str, Any]] = []
    for ref in candidate.get("source_experience_refs", []):
        path = resolve_inside(root, ref, must_exist=True)
        errors = validate(path, schema)
        if errors:
            raise ValueError(f"invalid source Experience {ref}: {'; '.join(errors)}")
        experience = read_json(path)
        if experience.get("candidate_eligible") is not True:
            raise ValueError(f"source Experience is not Candidate-eligible: {ref}")
        experiences.append(experience)
    if not experiences:
        raise ValueError(f"Candidate {candidate.get('candidate_id', '<unknown>')} has no source Experiences")
    return experiences


def load_valid_promotion(evolution_root: Path, promotion_path: Path) -> tuple[dict[str, Any], Path]:
    root = evolution_root.resolve(strict=True)
    path = resolve_inside(root, promotion_path)
    promotion = _load_valid(path, Path(__file__).resolve().parents[3] / "schemas" / "promotion_record.schema.json", "Promotion")
    return promotion, path


def validate_candidate_promotion_link(
    evolution_root: Path,
    promotion: dict[str, Any],
) -> tuple[dict[str, Any], Path, Path]:
    candidate_path = resolve_inside(evolution_root, promotion["candidate_ref"])
    candidate, candidate_path, patch_path = load_valid_candidate(evolution_root, candidate_path)
    if candidate["candidate_id"] != promotion["candidate_id"]:
        raise ValueError("Promotion candidate_id does not match referenced Candidate")
    expected_ref = candidate_path.relative_to(evolution_root.resolve(strict=True)).as_posix()
    if expected_ref != promotion["candidate_ref"]:
        raise ValueError("Promotion candidate_ref is not canonical")
    return candidate, candidate_path, patch_path
