"""Validate selected Experience records and report Candidate compatibility to stdout."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from skills._shared.scripts.artifact_io import read_json
from skills._shared.scripts.schema_validate import validate
from experience_compatibility import inspect_rows


def inspect(paths: list[Path]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in paths:
        schema_errors = validate(path, ROOT / "schemas" / "experience_record.schema.json")
        if schema_errors:
            errors.extend(f"{path}: {item}" for item in schema_errors)
            continue
        exp = read_json(path)
        rows.append(exp)
        if not exp["candidate_eligible"]:
            errors.append(f"{path}: Experience is not Candidate-eligible")
    return inspect_rows(rows, errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experience", type=Path, action="append", required=True)
    args = parser.parse_args()
    result = inspect(args.experience)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "compatible" else 1


if __name__ == "__main__":
    raise SystemExit(main())
