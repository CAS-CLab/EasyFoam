"""Validate a JSON artifact against a core schema addressed relative to the repository."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema


def validate(instance_path: Path, schema_path: Path) -> list[str]:
    instance = json.loads(instance_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    return [f"{'.'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path))]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("instance", type=Path)
    parser.add_argument("schema", type=Path)
    args = parser.parse_args()
    errors = validate(args.instance, args.schema)
    print(json.dumps({"status": "passed" if not errors else "failed", "errors": errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
