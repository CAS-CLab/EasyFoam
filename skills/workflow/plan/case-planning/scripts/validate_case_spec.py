"""Validate CaseSpec schema and semantic release gates."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from skills._shared.scripts.artifact_io import read_json
from skills._shared.scripts.schema_validate import validate


def _resolve_ref(case_spec_path: Path, ref: str) -> Path | None:
    candidates = []
    if ref.startswith(("skills/", "schemas/")):
        candidates.append(ROOT / ref)
    else:
        candidates.extend((case_spec_path.parent / ref, ROOT / ref))
    for candidate in candidates:
        try:
            return candidate.resolve(strict=True)
        except FileNotFoundError:
            continue
    return None


def _ref_exists(case_spec_path: Path, ref: str, *, user_file: bool = False) -> bool:
    resolved = _resolve_ref(case_spec_path, ref)
    if resolved is None:
        return False
    if user_file:
        return resolved.is_file()
    allowed_roots = (ROOT.resolve(strict=True), case_spec_path.parent.resolve(strict=True))
    return any(resolved.is_relative_to(root) for root in allowed_roots)


def semantic_errors(spec: dict[str, Any], case_spec_path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    blockers: list[str] = []

    review = spec["review_required"]
    unresolved_items = [item for item in review["items"] if item["status"] != "resolved"]
    open_blocking = [item["review_id"] for item in unresolved_items if item["blocking"]]
    if open_blocking:
        blockers.append("open or deferred blocking review items: " + ", ".join(open_blocking))
    if review["required"] != bool(unresolved_items):
        errors.append("review_required.required must equal whether unresolved review items remain")
    for item in review["items"]:
        if item["status"] == "resolved" and not item.get("resolution", "").strip():
            errors.append(f"resolved review item requires a resolution: {item['review_id']}")

    unresolved_decisive = set(spec["requirement_fidelity"]["unresolved_decisive"])
    expected_unresolved = {item["review_id"] for item in unresolved_items if item["blocking"]}
    if unresolved_decisive != expected_unresolved:
        errors.append(
            f"requirement_fidelity.unresolved_decisive {sorted(unresolved_decisive)} "
            f"does not match unresolved blocking reviews {sorted(expected_unresolved)}"
        )
    expected_fidelity = "blocked" if expected_unresolved else "review_required" if unresolved_items else "complete"
    if spec["requirement_fidelity"]["status"] != expected_fidelity:
        errors.append(
            f"requirement_fidelity.status must be {expected_fidelity} for the current review state"
        )

    evidence_refs = {item["ref"] for item in spec.get("evidence_sources", []) if item.get("ref")}
    user_file_refs = {item["ref"] for item in spec.get("evidence_sources", []) if item.get("kind") in {"user_requirement", "user_requirement_file"} and item.get("ref")}
    for source in spec.get("evidence_sources", []):
        ref = source.get("ref")
        if not ref:
            continue
        kind = source.get("kind")
        if not _ref_exists(case_spec_path, ref, user_file=kind in {"user_requirement", "user_requirement_file"}):
            errors.append(f"evidence source does not exist or is outside allowed scope: {ref}")
    for ref in spec["solver"].get("selection_basis", []):
        if ref not in evidence_refs:
            errors.append(f"solver.selection_basis is not declared in evidence_sources: {ref}")
    for name, parameter in spec["requirement_fidelity"].get("parameters", {}).items():
        ref = parameter.get("evidence_ref")
        if ref and not _ref_exists(case_spec_path, ref, user_file=ref in user_file_refs):
            errors.append(f"parameter {name} evidence_ref does not exist: {ref}")

    if spec["solver"]["execution"] == "foamRun" and not spec["solver"]["module"]:
        errors.append("foamRun execution requires solver.module")
    if spec["solver"]["execution"] == "legacy" and not spec["solver"]["application"]:
        errors.append("legacy execution requires solver.application")
    if spec["solver"]["algorithm"] != spec["numerics"]["algorithm"]:
        errors.append("solver.algorithm and numerics.algorithm must agree")
    if spec["solver"]["algorithm"] == "unknown":
        blockers.append("solver algorithm is unresolved")
    if spec["mesh"]["route"] == "unknown" or spec["mesh"]["method"] == "unknown":
        blockers.append("mesh route or method is unresolved")
    if spec["mesh"]["dimensionality"] == "unknown":
        blockers.append("mesh dimensionality is unresolved")
    if spec["geometry"]["complexity"] == "complex" and spec["mesh"]["method"] == "blockMesh":
        errors.append("complex geometry cannot use blockMesh-only without an explicit approved toy/background-domain contract")
    if not spec["fields"]:
        blockers.append("required field set is empty")
    if not spec["mesh"]["required_patches"]:
        blockers.append("patch inventory is empty")

    field_names = {field["name"] for field in spec["fields"] if field["required"]}
    patch_names = {patch["name"] for patch in spec["boundary_patches"]}
    required_patch_names = {patch["name"] for patch in spec["mesh"]["required_patches"] if patch["required"]}
    if patch_names != required_patch_names:
        errors.append(f"boundary patch set {sorted(patch_names)} does not match required mesh patches {sorted(required_patch_names)}")
    for patch in spec["boundary_patches"]:
        missing = sorted(field_names - set(patch["field_conditions"]))
        if missing:
            errors.append(f"patch {patch['name']} is missing conditions for fields: {', '.join(missing)}")
        unresolved = [name for name, bc in patch["field_conditions"].items() if bc.get("source") == "review_required" or bc.get("type") == "review_required"]
        if unresolved:
            blockers.append(f"patch {patch['name']} has unresolved boundary conditions: {', '.join(unresolved)}")

    controls = spec["run"]["controls"]
    required_controls = ["start_from", "start_time", "end_time", "write_control", "write_interval"]
    if spec["physics"]["flow_time"] == "transient":
        required_controls.append("delta_t")
    for key in required_controls:
        value = controls[key]
        if value["source"] == "review_required" or value.get("value") is None:
            blockers.append(f"formal run control unresolved: {key}")
    if not spec["run"]["solver_command"]:
        blockers.append("solver command is unresolved")
    if spec["physics"]["phase_regime"] == "unknown":
        blockers.append("phase regime is unresolved")
    if spec["physics"]["compressibility"] == "unknown":
        blockers.append("compressibility is unresolved")
    if spec["physics"]["flow_time"] == "unknown":
        blockers.append("steady/transient model is unresolved")
    if spec["physics"]["turbulence"]["simulation_type"] == "unknown":
        blockers.append("laminar/turbulence treatment is unresolved")

    return errors, sorted(set(blockers))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_spec", type=Path)
    parser.add_argument("--schema-only", action="store_true")
    args = parser.parse_args()
    schema_errors = validate(args.case_spec, ROOT / "schemas" / "case_spec.schema.json")
    semantic, blockers = ([], []) if schema_errors or args.schema_only else semantic_errors(read_json(args.case_spec), args.case_spec)
    status = "failed" if schema_errors or semantic else ("blocked" if blockers else "passed")
    print(json.dumps({"status": status, "schema_errors": schema_errors, "semantic_errors": semantic, "blockers": blockers}, ensure_ascii=False, indent=2))
    if schema_errors or semantic:
        return 1
    if blockers:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
