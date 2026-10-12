"""Deterministic file-tree hashing utilities without machine-specific paths."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Callable, Iterable

PathPredicate = Callable[[Path], bool]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_text_bytes(value: bytes) -> bytes:
    """Normalize text line endings for cross-platform Candidate target hashes.

    Candidate targets are text artifacts (Skills, references, Python scripts,
    and JSON Schemas). Git may materialize the same text with LF or CRLF in
    different working trees, so target-state hashes use LF-normalized bytes.
    Patch artifacts themselves must continue to use :func:`sha256_file`.
    """
    return value.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256_canonical_text_bytes(value: bytes) -> str:
    return hashlib.sha256(canonical_text_bytes(value)).hexdigest()


def sha256_canonical_text_file(path: Path) -> str:
    return sha256_canonical_text_bytes(path.read_bytes())


def tree_digest(
    root: Path,
    *,
    include_prefixes: Iterable[str] | None = None,
    exclude: PathPredicate | None = None,
) -> dict[str, object]:
    root = root.resolve(strict=True)
    prefixes = tuple(prefix.strip("/") for prefix in (include_prefixes or ()))
    entries: list[dict[str, str]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root)
        relative_text = relative.as_posix()
        if prefixes and not any(relative_text == prefix or relative_text.startswith(prefix + "/") for prefix in prefixes):
            continue
        if exclude and exclude(relative):
            continue
        entries.append({"path": relative_text, "sha256": sha256_file(path)})
    combined = hashlib.sha256(
        "\n".join(f"{entry['path']}:{entry['sha256']}" for entry in entries).encode("utf-8")
    ).hexdigest()
    return {"file_count": len(entries), "tree_sha256": combined, "files": entries}


def formal_input_digest(case_dir: Path) -> dict[str, object]:
    """Hash immutable formal inputs while excluding generated runtime outputs."""
    return tree_digest(case_dir, include_prefixes=("0", "constant", "system"))


def state_digest(case_dir: Path, time_name: str) -> dict[str, object]:
    state_dir = case_dir / time_name
    if not state_dir.is_dir():
        raise FileNotFoundError(f"state directory is missing: {state_dir}")
    return tree_digest(state_dir)
