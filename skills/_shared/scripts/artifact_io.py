"""UTF-8, transactional JSON artifact helpers shared by EasyFoam skills."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_temp_json(path: Path, value: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        return Path(handle.name)


def write_json_atomic(path: Path, value: Any) -> None:
    temporary = _write_temp_json(path, value)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)



def validate_json_value(value: Any, schema_path: Path, *, directory: Path | None = None) -> list[str]:
    """Validate an in-memory JSON value without touching a canonical artifact."""
    from skills._shared.scripts.schema_validate import validate

    base = directory or schema_path.parent
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=base,
        prefix=".easyfoam-validate.",
        suffix=".json",
        delete=False,
    ) as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        temporary = Path(handle.name)
    try:
        return validate(temporary, schema_path)
    finally:
        temporary.unlink(missing_ok=True)

def write_validated_json_atomic(path: Path, value: Any, schema_path: Path) -> None:
    """Validate a temporary JSON file before replacing the canonical artifact."""
    from skills._shared.scripts.schema_validate import validate

    temporary = _write_temp_json(path, value)
    try:
        errors = validate(temporary, schema_path)
        if errors:
            raise RuntimeError(f"{path.name} validation failed: " + "; ".join(errors))
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
