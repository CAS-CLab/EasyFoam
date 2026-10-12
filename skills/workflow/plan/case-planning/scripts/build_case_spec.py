"""Build a conservative, provenance-aware CaseSpec from user text or a user TXT file.

The result may be schema-valid but blocked for review. The case-planning specialist
must resolve blocking review items before Write.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))
from skills._shared.scripts.artifact_io import write_json_atomic
from skills._shared.scripts.schema_validate import validate
from parse_requirement import parse


def pv(
    value: Any,
    source: str,
    unit: str | None = None,
    evidence_ref: str | None = None,
    rationale: str = "",
    raw_text: str = "",
) -> dict[str, Any]:
    result: dict[str, Any] = {"value": value, "source": source, "unit": unit}
    result["evidence_ref"] = evidence_ref
    if rationale:
        result["rationale"] = rationale
    if raw_text:
        result["raw_text"] = raw_text
    return result


def from_parsed(item: dict[str, Any] | None, *, fallback_unit: str | None = None) -> dict[str, Any]:
    if item is None:
        return pv(None, "review_required", fallback_unit, None, "Not resolved from the user requirement.")
    return pv(
        item.get("value"),
        item.get("source", "derived"),
        item.get("unit", fallback_unit),
        item.get("evidence_ref"),
        raw_text=item.get("raw_text", ""),
    )


def _legacy_module(legacy: str | None) -> tuple[str | None, str | None]:
    if not legacy:
        return None, None
    key = legacy.lower()
    mapping = {
        "pimplefoam": ("incompressibleFluid", "PIMPLE"),
        "pisofoam": ("incompressibleFluid", "PISO"),
        "simplefoam": ("incompressibleFluid", "SIMPLE"),
        "rhosimplefoam": ("fluid", "SIMPLE"),
        "rhopimplefoam": ("fluid", "PIMPLE"),
        "interfoam": ("incompressibleVoF", "PIMPLE"),
    }
    return mapping.get(key, (None, None))


def _dictionary_family(module: str | None) -> str | None:
    return {
        "incompressibleFluid": "physicalProperties + momentumTransport",
        "incompressibleVoF": "physicalProperties + phaseProperties + momentumTransport",
        "fluid": "thermophysicalProperties/physicalProperties + momentumTransport",
        "shockFluid": "thermophysicalProperties/physicalProperties + momentumTransport",
        "multicomponentFluid": "thermophysicalProperties + species/reaction dictionaries + momentumTransport",
    }.get(module)


def _fields(module: str | None) -> list[dict[str, Any]]:
    """Return only field names that are unambiguous at module level.

    Energy variables (T/h/e), phase-fraction names, and species names depend on
    the selected model/dictionary contract and must be resolved explicitly.
    """
    if module in {"incompressibleFluid", "incompressibleVoF", "fluid", "shockFluid", "multicomponentFluid"}:
        return [
            {"name": "U", "class": None, "dimensions": None, "role": "solved", "required": True},
            {"name": "p", "class": None, "dimensions": None, "role": "solved", "required": True},
        ]
    return []


def _field_conditions(parsed: dict[str, Any], patch: dict[str, str], field_names: list[str], requirement_ref: str | None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    conditions: dict[str, Any] = {}
    reviews: list[dict[str, Any]] = []
    role = patch["physical_role"]
    mesh_type = patch["mesh_type"]
    explicit = {
        (item["patch"].lower(), item["field"]): item
        for item in parsed.get("boundary_conditions", [])
    }
    for field in field_names:
        matched = explicit.get((patch["name"].lower(), field))
        if matched is not None:
            conditions[field] = {
                "type": matched["type"],
                "source": "user_explicit",
                "evidence_ref": matched.get("evidence_ref", requirement_ref),
            }
            if "value" in matched:
                conditions[field]["value"] = matched["value"]
            continue
        if mesh_type == "empty":
            conditions[field] = {"type": "empty", "source": "derived", "evidence_ref": requirement_ref}
            continue
        if role == "inlet" and field == "U" and parsed["material"].get("inlet_velocity"):
            value = parsed["material"]["inlet_velocity"]
            conditions[field] = {
                "type": "fixedValue",
                "source": "user_explicit",
                "value": value["value"],
                "evidence_ref": requirement_ref,
            }
            continue
        if role == "outlet" and field == "p" and parsed["flags"]["zero_gradient_pressure_outlet"]:
            conditions[field] = {
                "type": "zeroGradient",
                "source": "user_explicit",
                "evidence_ref": requirement_ref,
            }
            continue
        if role == "wall" and field == "U" and parsed["flags"]["no_slip"]:
            conditions[field] = {
                "type": "noSlip",
                "source": "user_explicit",
                "evidence_ref": requirement_ref,
            }
            continue
        conditions[field] = {"type": "review_required", "source": "review_required", "evidence_ref": None}
        reviews.append(
            {
                "review_id": f"bc-{patch['name']}-{field}",
                "category": "boundary_condition",
                "question": f"Resolve boundary condition for field {field} on patch {patch['name']}.",
                "blocking": True,
                "status": "open",
            }
        )
    return conditions, reviews


def build(
    run_dir: Path,
    case_id: str,
    requirement_text: str,
    requirement_ref: str | None,
    requirement_kind: str,
    openfoam_version: str,
) -> Path:
    text = requirement_text
    parsed = parse(text, requirement_ref)
    legacy = parsed["legacy_application"]["value"] if parsed["legacy_application"] else None
    derived_module, derived_algorithm = _legacy_module(legacy)
    module = parsed["module"]["value"] if parsed["module"] else derived_module
    algorithm = parsed["algorithm"]["value"] if parsed["algorithm"] else derived_algorithm

    flow_time = parsed["flow_time"]["value"] if parsed["flow_time"] else None
    if flow_time is None and algorithm == "SIMPLE":
        flow_time = "steady"
    elif flow_time is None and algorithm in {"PIMPLE", "PISO"}:
        flow_time = "transient"

    phase_regime = parsed["phase_regime"]["value"] if parsed["phase_regime"] else None
    if phase_regime is None and module == "incompressibleVoF":
        phase_regime = "multiphase"

    compressibility = parsed["compressibility"]["value"] if parsed["compressibility"] else None
    energy = parsed["flags"]["energy"]
    species = parsed["flags"]["species"]
    turbulence_type = parsed["turbulence_type"]["value"] if parsed["turbulence_type"] else None
    turbulence_model = parsed["turbulence_model"]["value"] if parsed["turbulence_model"] else None

    reviews: list[dict[str, Any]] = []
    decisive: list[str] = []

    def need(key: str, question: str, category: str) -> None:
        decisive.append(key)
        reviews.append({"review_id": key, "category": category, "question": question, "blocking": True, "status": "open"})

    if phase_regime is None:
        need("physics-phase-regime", "Resolve single-phase or multiphase physics.", "physics")
    if compressibility is None:
        need("physics-compressibility", "Resolve incompressible, low-Mach, or compressible treatment.", "physics")
    if flow_time is None:
        need("physics-flow-time", "Resolve steady or transient flow model.", "physics")
    if turbulence_type is None:
        need("physics-turbulence", "Resolve laminar/RAS/LES/DNS treatment and model if applicable.", "physics")
    if module is None:
        need("solver-module", "Select a compatible OpenFOAM-13 solver module/application.", "solver")
    if algorithm is None:
        need("solver-algorithm", "Resolve SIMPLE, PISO, PIMPLE, or not-applicable algorithm contract.", "solver")

    geometry_source = parsed["geometry_source"]
    complexity = "complex" if parsed["flags"]["complex_geometry"] else ("simple" if geometry_source == "parametric" else "unknown")
    if complexity == "complex" and geometry_source == "unspecified":
        need("geometry-source", "Provide or identify the complex geometry/mesh source.", "geometry")

    parsed_mesh = parsed["mesh_method"]["value"] if parsed["mesh_method"] else None
    if geometry_source == "external_mesh":
        mesh_route, mesh_method = "import", parsed_mesh or "external"
    elif parsed_mesh in {"blockMesh", "snappyHexMesh"}:
        mesh_route, mesh_method = "generate", parsed_mesh
    elif geometry_source == "surface_file":
        mesh_route, mesh_method = "generate", "snappyHexMesh"
    elif geometry_source == "parametric" and complexity == "simple":
        mesh_route, mesh_method = "generate", "blockMesh"
    else:
        mesh_route, mesh_method = "unknown", "unknown"
        need("mesh-route", "Resolve mesh generation, import, or reuse route.", "mesh")

    dimensionality = "2D" if any(patch["mesh_type"] == "empty" for patch in parsed["patches"]) else "unknown"
    if dimensionality == "unknown":
        need("mesh-dimensionality", "Resolve 2D, 3D, wedge, or axisymmetric mesh dimensionality.", "mesh")

    fields = _fields(module)
    if not fields:
        need("field-set", "Resolve the required solved and auxiliary fields.", "fields")
    if module in {"fluid", "shockFluid", "multicomponentFluid"} or energy:
        need("energy-field-family", "Resolve the actual energy variable required by the selected module and thermophysical model (for example T, h, or e).", "fields")
    if module == "incompressibleVoF" or phase_regime == "multiphase":
        need("phase-field-names", "Resolve explicit phase names and resulting phase-fraction field names; do not assume alpha.water.", "fields")
    if species or module == "multicomponentFluid":
        need("species-field-names", "Provide the actual species list and field names; Yi is a family notation, not an assumed field file.", "fields")
    field_names = [item["name"] for item in fields]

    patch_contracts = [
        {"name": item["name"], "mesh_type": item["mesh_type"], "physical_role": item["physical_role"], "required": True}
        for item in parsed["patches"]
    ]
    boundaries = []
    for patch in parsed["patches"]:
        conditions, patch_reviews = _field_conditions(parsed, patch, field_names, requirement_ref)
        reviews.extend(patch_reviews)
        decisive.extend(item["review_id"] for item in patch_reviews)
        boundaries.append(
            {
                "name": patch["name"],
                "mesh_type": patch["mesh_type"],
                "physical_role": patch["physical_role"],
                "source": "derived",
                "field_conditions": conditions,
            }
        )
    if not patch_contracts:
        need("patch-inventory", "Define all mesh patches and physical roles.", "boundary_condition")

    material_entries = []
    for key, item in parsed["material"].items():
        if item is None or key in {"inlet_velocity", "rpm"}:
            continue
        material_entries.append(
            {
                "name": key,
                "value": item["value"],
                "unit": item.get("unit"),
                "dimensions": None,
                "source": item.get("source", "user_explicit"),
                "evidence_ref": item.get("evidence_ref"),
                "required": True,
            }
        )

    controls_parsed = parsed["controls"]
    controls = {
        "start_from": from_parsed(controls_parsed.get("start_from"), fallback_unit="category"),
        "start_time": from_parsed(controls_parsed.get("start_time"), fallback_unit="s_or_iteration"),
        "end_time": from_parsed(controls_parsed.get("end_time"), fallback_unit="s_or_iteration"),
        "delta_t": from_parsed(controls_parsed.get("delta_t"), fallback_unit="s_or_iteration"),
        "adjust_time_step": from_parsed(parsed.get("adjust_time_step"), fallback_unit="boolean"),
        "max_co": from_parsed(controls_parsed.get("max_co"), fallback_unit="1"),
        "write_control": from_parsed(parsed.get("write_control"), fallback_unit="category"),
        "write_interval": from_parsed(controls_parsed.get("write_interval"), fallback_unit="s_or_iteration"),
    }
    required_control_keys = ["start_from", "start_time", "end_time", "write_control", "write_interval"]
    if flow_time == "transient":
        required_control_keys.append("delta_t")
    for key in required_control_keys:
        if controls[key]["source"] == "review_required":
            need(f"run-{key}", f"Resolve formal run control: {key}.", "run_control")

    solver_command = f"foamRun -solver {module}" if module else None
    preprocessing = []
    if mesh_method == "blockMesh":
        preprocessing = ["blockMesh", "checkMesh"]
    elif mesh_method == "snappyHexMesh":
        preprocessing = ["blockMesh", "surfaceFeatures", "snappyHexMesh -overwrite", "checkMesh"]
    elif mesh_method == "external":
        preprocessing = []
        need(
            "mesh-converter-command",
            "Resolve the external mesh format, source reference, exact converter command, and required conversion options.",
            "mesh",
        )

    required_cell_zones: list[str] = []
    if parsed["flags"]["mrf"]:
        need("mrf-cell-zone", "Provide or verify the exact rotating cellZone name required by MRF; do not assume rotor.", "mesh")
    outputs_qoi: list[dict[str, Any]] = []
    if re.search(r"\bprobe(?:s)?\b|探针|监测点", text, re.I):
        outputs_qoi.append({"qoi_id": "probe_history", "kind": "probe", "field": "U", "location": None, "unit": None, "method": "probes functionObject", "required": True, "acceptance_criterion": None, "sampling_or_aggregation": None})
        need("probe-contract", "Resolve probe field(s), coordinates, and sampling/write control.", "output")
    if re.search(r"\bforceCoeffs?\b|\bC[dDlL]\b|drag coefficient|lift coefficient|阻力系数|升力系数", text, re.I):
        outputs_qoi.append({"qoi_id": "force_coefficients", "kind": "forceCoeffs", "field": None, "location": None, "unit": "1", "method": "forceCoeffs functionObject", "required": True, "acceptance_criterion": None, "sampling_or_aggregation": None})
        need("force-coefficients-contract", "Resolve forceCoeffs patches, density contract, reference area/length, lift/drag directions, and moment reference point.", "output")

    visual_requests = [
        {"visual_id": f"visual-{field}", "kind": "field_contour" if field != "U" else "flow_visual", "field": field, "purpose": f"Inspect {field} field evidence.", "required": True}
        for field in parsed["requested_visuals"]
    ]

    parameters: dict[str, Any] = {}
    for group in [controls_parsed, parsed["material"]]:
        for key, item in group.items():
            if item is not None:
                parameters[key] = from_parsed(item)
    for key in ["phase_regime", "compressibility", "flow_time", "algorithm", "module", "legacy_application", "turbulence_type", "turbulence_model", "mesh_method", "write_control", "adjust_time_step"]:
        item = parsed.get(key)
        if item is not None:
            parameters[key] = from_parsed(item)

    if parsed["module"] is None and module:
        parameters["module"] = pv(
            module,
            "derived",
            "category",
            f"skills/reference/solver_modules/{module}.md",
            rationale=f"Legacy application {legacy} maps to the OpenFOAM-13 module {module}.",
        )
    if parsed["algorithm"] is None and algorithm:
        parameters["algorithm"] = pv(
            algorithm,
            "derived",
            "category",
            "skills/workflow/plan/case-planning/references/solver-selection-v13.md",
            rationale=f"Algorithm {algorithm} was derived from legacy application {legacy}.",
        )
    if parsed["flow_time"] is None and flow_time:
        parameters["flow_time"] = pv(
            flow_time,
            "derived",
            "category",
            "skills/workflow/plan/case-planning/references/solver-selection-v13.md",
            rationale=f"{algorithm} was mapped to the {flow_time} execution contract.",
        )
    if parsed["phase_regime"] is None and phase_regime:
        parameters["phase_regime"] = pv(
            phase_regime,
            "derived",
            "category",
            f"skills/reference/solver_modules/{module}.md" if module else "skills/workflow/plan/case-planning/references/solver-selection-v13.md",
            rationale=f"Module {module} requires the {phase_regime} phase regime.",
        )
    parameters["mesh_route"] = pv(
        mesh_route,
        "derived" if mesh_route != "unknown" else "review_required",
        "category",
        requirement_ref if mesh_route != "unknown" else None,
        rationale="Mesh route was derived from geometry source and declared mesh method." if mesh_route != "unknown" else "Mesh route remains unresolved.",
    )
    parameters["mesh_method"] = pv(
        mesh_method,
        "derived" if parsed["mesh_method"] is None and mesh_method != "unknown" else parameters.get("mesh_method", {}).get("source", "review_required"),
        "category",
        requirement_ref if mesh_method != "unknown" else None,
        rationale="Mesh method was derived from geometry source and complexity." if parsed["mesh_method"] is None and mesh_method != "unknown" else "",
    )
    parameters["dimensionality"] = pv(
        dimensionality,
        "derived" if dimensionality != "unknown" else "review_required",
        "category",
        requirement_ref if dimensionality != "unknown" else None,
        rationale="An empty patch contract implies a 2D case." if dimensionality == "2D" else "Mesh dimensionality remains unresolved.",
    )

    requirement_items = []
    for key, item in parameters.items():
        requirement_items.append(
            {
                "requirement_id": key,
                "category": "parsed_parameter",
                "statement": item.get("raw_text") or f"Captured parameter {key}.",
                "status": "captured" if item["source"] == "user_explicit" else "derived",
                "decisive": key in {"phase_regime", "compressibility", "flow_time", "algorithm", "module", "mesh_route", "mesh_method", "dimensionality", "end_time", "write_interval"},
                "parameter": item,
                "mapped_targets": [key],
                "evidence_refs": [item["evidence_ref"]] if item.get("evidence_ref") else [],
                "notes": [],
            }
        )

    source_refs = [requirement_ref] if requirement_ref else []
    if module:
        source_refs.append(f"skills/reference/solver_modules/{module}.md")

    spec = {
        "schema_version": "1.2",
        "case_id": case_id,
        "case_name": case_id.replace("/", "_").replace("\\", "_"),
        "openfoam_version": openfoam_version,
        "description": "Conservative CaseSpec generated from the user requirement; unresolved decisive items remain blocking review items.",
        "user_requirement_ref": requirement_ref,
        "requirement_fidelity": {
            "status": "blocked" if reviews else "complete",
            "source_ref": requirement_ref,
            "parameters": parameters,
            "items": requirement_items,
            "unresolved_decisive": sorted(set(decisive)),
        },
        "physics": {
            "phase_regime": phase_regime or "unknown",
            "compressibility": compressibility or "unknown",
            "energy": "on" if energy else "unknown",
            "species": "on" if species else "unknown",
            "flow_time": flow_time or "unknown",
            "turbulence": {
                "simulation_type": turbulence_type or "unknown",
                "model": turbulence_model,
                "wall_treatment": None,
            },
            "rotating_or_moving_frame": "MRF" if parsed["flags"]["mrf"] else ("moving_mesh" if parsed["flags"]["moving_mesh"] else "none"),
            "gravity": True if parsed["flags"]["gravity"] else None,
            "notes": [],
        },
        "solver": {
            "execution": "foamRun" if module else "unknown",
            "module": module,
            "application": legacy if legacy and not module else None,
            "legacy_equivalent": legacy,
            "algorithm": algorithm or "unknown",
            "dictionary_family": _dictionary_family(module),
            "selection_basis": source_refs,
        },
        "geometry": {
            "source_type": geometry_source,
            "complexity": complexity,
            "source_refs": ([requirement_ref] if requirement_ref else []) if geometry_source != "unspecified" else [],
            "units": None,
            "body_kind": None,
            "review_required": any(item["category"] == "geometry" and item["status"] == "open" for item in reviews),
        },
        "mesh": {
            "route": mesh_route,
            "method": mesh_method,
            "dimensionality": dimensionality,
            "required_patches": patch_contracts,
            "required_cell_zones": required_cell_zones,
            "required_face_zones": [],
            "quality_policy": {
                "check_mesh_required": True,
                "blocking_failures": ["negative_volume", "invalid_topology", "missing_required_patch", "missing_required_zone"],
            },
            "source_refs": [requirement_ref] if requirement_ref else [],
        },
        "fields": fields,
        "boundary_patches": boundaries,
        "material_properties": {
            "entries": material_entries,
            "models": {
                "turbulence_model": turbulence_model,
                "rotating_speed_rpm": parsed["material"]["rpm"]["value"] if parsed["material"].get("rpm") else None,
            },
        },
        "numerics": {
            "algorithm": algorithm or "unknown",
            "schemes": {},
            "linear_solvers": {},
            "correctors": {},
            "relaxation": {},
            "time_step_policy": {},
            "source_refs": source_refs,
        },
        "run": {
            "preprocessing_commands": preprocessing,
            "solver_command": solver_command,
            "controls": controls,
            "parallel": {"enabled": False, "processes": None},
            "restart_policy": "fresh",
            "formal_controls_preserved": not any(controls[key]["source"] == "review_required" for key in required_control_keys),
        },
        "outputs": {
            "qois": outputs_qoi,
            "diagnostics": ["residuals", "mesh_quality", "runtime_summary"],
            "visuals": visual_requests,
        },
        "validation": {
            "checks": [
                {"check_id": "requirement-fidelity", "category": "requirement", "metric": "mapped explicit requirements", "criterion": "all decisive requirements resolved and mapped", "required": True, "evidence_plan": ["case_spec.json"]},
                {"check_id": "case-contract", "category": "file", "metric": "case structure and field/patch/model contracts", "criterion": "all required static checks pass", "required": True, "evidence_plan": ["workflow.json", "case/"]},
                {"check_id": "mesh-contract", "category": "mesh", "metric": "geometry, patches, zones and checkMesh", "criterion": "required mesh gates pass", "required": True, "evidence_plan": ["workflow.json", "case/constant/polyMesh/", "runs/*/*.stdout.log"]},
                {"check_id": "runtime-contract", "category": "runtime", "metric": "formal solver completion", "criterion": "declared terminal condition reached with decisive evidence", "required": True, "evidence_plan": ["runs/*/run_record.json"]},
                {"check_id": "numerical-credibility", "category": "numerical", "metric": "residual/time-step/conservation/boundedness behavior", "criterion": "problem-appropriate numerical gates pass", "required": True, "evidence_plan": ["runs/*/run_record.json", "evidence_summary.json"]},
                {"check_id": "physical-credibility", "category": "physical", "metric": "problem-specific physics and conservation", "criterion": "requested physical checks pass", "required": True, "evidence_plan": ["evidence_summary.json"]},
            ],
            "claim_boundaries": [
                "Schema validity does not release a blocked CaseSpec.",
                "Solver execution does not prove numerical or physical credibility.",
                "A single mesh does not prove mesh independence.",
            ],
        },
        "assumptions": [],
        "review_required": {"required": bool(reviews), "items": reviews},
        "evidence_sources": [
            {"source_id": "user-requirement", "kind": requirement_kind, "ref": requirement_ref, "role": "authoritative user target"}
        ] + ([{"source_id": "solver-module-card", "kind": "reference", "ref": f"skills/reference/solver_modules/{module}.md", "role": "module/dictionary-family evidence"}] if module else []),
    }

    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "case_spec.json"
    write_json_atomic(path, spec)
    errors = validate(path, ROOT / "schemas" / "case_spec.schema.json")
    if errors:
        raise RuntimeError("CaseSpec schema validation failed: " + "; ".join(errors))
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--requirement-text")
    source.add_argument("--requirement-file", type=Path)
    parser.add_argument("--openfoam-version", default="Foundation-v13")
    args = parser.parse_args()
    if args.requirement_text is not None:
        requirement_text = args.requirement_text
        requirement_ref = None
        requirement_kind = "runtime_prompt"
    else:
        source_path = args.requirement_file.resolve(strict=True)
        requirement_text = source_path.read_text(encoding="utf-8")
        try:
            requirement_ref = source_path.relative_to(ROOT.resolve(strict=True)).as_posix()
        except ValueError:
            requirement_ref = Path(os.path.relpath(source_path, args.run_dir.resolve(strict=False))).as_posix()
        requirement_kind = "user_requirement_file"
    path = build(args.run_dir, args.case_id, requirement_text, requirement_ref, requirement_kind, args.openfoam_version)
    print(json.dumps({"status": "passed", "case_spec": path.as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
