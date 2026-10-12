"""Repository-relative path policy and archive exclusion helpers."""
from __future__ import annotations

from pathlib import Path


def repository_root(anchor: Path) -> Path:
    for parent in (anchor.resolve(), *anchor.resolve().parents):
        if (parent / "skills").is_dir() and (parent / "schemas").is_dir():
            return parent
    raise RuntimeError("EasyFoam repository root not found")


def relative_to_root(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def is_relative_reference(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return bool(normalized) and not normalized.startswith("/") and not (len(normalized) > 2 and normalized[1] == ":")


def is_excluded(path: Path) -> bool:
    return any(part == "archive" or part.startswith("legacy_snapshot_") for part in path.parts)
