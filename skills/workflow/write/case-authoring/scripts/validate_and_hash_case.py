"""Run deterministic static case gates, hash the accepted formal case, and update Workflow."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "skills" / "workflow" / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "workflow" / "plan" / "case-planning" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent))

from skills._shared.scripts.artifact_io import read_json
from skills._shared.scripts.hashing import formal_input_digest, state_digest, tree_digest
from skills._shared.scripts.openfoam_text import find_placeholders, parse_boundary_file, parse_field_boundary_names, parse_zone_names
from skills._shared.scripts.schema_validate import validate
from workflow_ledger import add_evidence, advance, load, record_artifact, save
from validate_case_spec import semantic_errors
from check_case_structure import inspect as inspect_structure
from validate_algorithm_contract import inspect as inspect_algorithm


def verify(case_dir: Path, spec: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    structure = inspect_structure(case_dir, spec)
    errors.extend(structure["missing"])

    placeholders = find_placeholders(case_dir)
    if placeholders:
        errors.append("unresolved placeholders in: " + ", ".join(placeholders))

    poly = case_dir / "constant" / "polyMesh"
    patches = parse_boundary_file(poly / "boundary")
    actual = {item["name"]: item.get("type") for item in patches}
    expected = {
        item["name"]: item["mesh_type"]
        for item in spec.get("mesh", {}).get("required_patches", [])
        if item.get("required", False)
    }
    missing_patches = sorted(set(expected) - set(actual))
    type_mismatches = sorted(name for name, patch_type in expected.items() if name in actual and actual[name] and patch_type != actual[name])
    if missing_patches:
        errors.append("missing mesh patches: " + ", ".join(missing_patches))
    if type_mismatches:
        errors.append("mesh patch type mismatches: " + ", ".join(type_mismatches))

    actual_cell = set(parse_zone_names(poly / "cellZones"))
    actual_face = set(parse_zone_names(poly / "faceZones"))
    missing_cell = sorted(set(spec.get("mesh", {}).get("required_cell_zones", [])) - actual_cell)
    missing_face = sorted(set(spec.get("mesh", {}).get("required_face_zones", [])) - actual_face)
    if missing_cell:
        errors.append("missing cellZones: " + ", ".join(missing_cell))
    if missing_face:
        errors.append("missing faceZones: " + ", ".join(missing_face))

    field_gaps: dict[str, dict[str, list[str]]] = {}
    actual_patch_names = set(actual)
    for field in spec.get("fields", []):
        if not field.get("required", False):
            continue
        path = case_dir / "0" / field["name"]
        names = set(parse_field_boundary_names(path))
        missing = sorted(actual_patch_names - names)
        unexpected = sorted(names - actual_patch_names)
        if missing or unexpected:
            field_gaps[field["name"]] = {"missing": missing, "unexpected": unexpected}
    if field_gaps:
        errors.append("field boundary coverage differs from actual mesh")

    algorithm = spec.get("solver", {}).get("algorithm") or spec.get("numerics", {}).get("algorithm")
    algorithm_result = (
        inspect_algorithm(case_dir, algorithm)
        if algorithm in {"SIMPLE", "PISO", "PIMPLE", "not_applicable"}
        else {"passed": False, "expected": [algorithm], "found": [], "errors": ["unresolved or unsupported algorithm"]}
    )
    errors.extend(algorithm_result.get("errors", []))
    if not patches:
        errors.append("no actual mesh patches parsed")

    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "structure": structure,
        "patches": patches,
        "cell_zones": sorted(actual_cell),
        "face_zones": sorted(actual_face),
        "field_patch_gaps": field_gaps,
        "algorithm": algorithm_result,
        "placeholders": placeholders,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--case-dir", type=Path)
    parser.add_argument("--update-workflow", action="store_true")
    args = parser.parse_args()

    case_dir = args.case_dir or args.run_dir / "case"
    spec_path = args.run_dir / "case_spec.json"
    schema_errors = validate(spec_path, ROOT / "schemas" / "case_spec.schema.json")
    if schema_errors:
        print(json.dumps({"passed": False, "errors": schema_errors}, ensure_ascii=False, indent=2))
        return 1
    spec = read_json(spec_path)
    semantic, blockers = semantic_errors(spec, spec_path)
    if semantic or blockers:
        print(json.dumps({"passed": False, "errors": semantic, "blockers": blockers}, ensure_ascii=False, indent=2))
        return 1
    if not case_dir.is_dir():
        print(json.dumps({"passed": False, "errors": [f"case directory missing: {case_dir}"]}, ensure_ascii=False, indent=2))
        return 1

    result = verify(case_dir, spec)
    if result["passed"]:
        result["case_sha256"] = tree_digest(case_dir)["tree_sha256"]
        mesh = case_dir / "constant" / "polyMesh"
        result["mesh_sha256"] = tree_digest(mesh)["tree_sha256"] if mesh.is_dir() else None
        result["input_sha256"] = formal_input_digest(case_dir)["tree_sha256"]
        result["initial_state_sha256"] = state_digest(case_dir, "0")["tree_sha256"]
        if args.update_workflow:
            workflow = load(args.run_dir)
            if not case_dir.resolve().is_relative_to(args.run_dir.resolve()):
                raise ValueError("formal case must be inside the Workflow root")
            rel = case_dir.resolve().relative_to(args.run_dir.resolve()).as_posix()
            record_artifact(workflow, "case_spec", "case_spec.json")
            record_artifact(
                workflow,
                "formal_case",
                rel,
                result["case_sha256"],
                result["mesh_sha256"],
                result["input_sha256"],
                result["initial_state_sha256"],
            )
            add_evidence(
                workflow,
                "formal_case_structural_gate_passed",
                "write",
                "passed",
                "Structural inventory, patch/zone/field coverage, algorithm block, placeholder, and formal input hash gates passed.",
                rel,
            )
            remaining = [stage for stage in workflow["requested_scope"]["stages"] if stage not in workflow["completed_scope"] and stage != "write"]
            next_stage = next((stage for stage in ("run", "postprocess") if stage in remaining), None)
            advance(
                workflow,
                "write",
                next_stage,
                None,
                "Write completed; continue to the next requested stage." if next_stage else None,
            )
            save(args.run_dir, workflow)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
