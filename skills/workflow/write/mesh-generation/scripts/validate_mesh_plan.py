"""Validate CaseSpec mesh-route and geometry compatibility."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from skills._shared.scripts.artifact_io import read_json


def validate(spec: dict) -> dict:
    geometry = spec["geometry"]
    mesh = spec["mesh"]
    errors: list[str] = []
    warnings: list[str] = []
    if mesh["route"] != "generate":
        errors.append("mesh-generation requires mesh.route=generate")
    if mesh["method"] not in {"blockMesh", "snappyHexMesh", "combined"}:
        errors.append(f"unsupported generation method: {mesh['method']}")
    if geometry["complexity"] == "complex" and mesh["method"] == "blockMesh":
        errors.append("complex geometry cannot use blockMesh-only")
    if geometry["complexity"] == "complex" and not geometry["source_refs"]:
        errors.append("complex geometry requires a source reference")
    if not mesh["required_patches"]:
        errors.append("required patch contract is empty")
    if mesh["dimensionality"] == "unknown":
        errors.append("mesh dimensionality must be resolved before mesh generation")
    return {"passed": not errors, "errors": errors, "warnings": warnings, "method": mesh["method"], "route": mesh["route"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args()
    result = validate(read_json(args.spec))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
