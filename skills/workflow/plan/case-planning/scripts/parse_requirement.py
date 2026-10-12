"""Extract explicit CFD requirements with provenance without inventing decisive values.

This parser is intentionally conservative. The case-planning specialist must review and
complete the semantic contract; regex extraction is not the planning authority.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

NUMBER = r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"


def _value(text: str, pattern: str, unit: str, parameter_id: str) -> dict[str, Any] | None:
    match = re.search(pattern, text, re.I)
    if not match:
        return None
    raw = match.group(1)
    try:
        value: Any = float(raw)
    except ValueError:
        value = raw
    return {
        "value": value,
        "unit": unit,
        "source": "user_explicit",
        "evidence_ref": "__requirement_source__",
        "raw_text": match.group(0),
        "parameter_id": parameter_id,
    }


def _category(text: str, patterns: list[str], value: str, parameter_id: str) -> dict[str, Any] | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return {
                "value": value,
                "unit": "category",
                "source": "user_explicit",
                "evidence_ref": "__requirement_source__",
                "raw_text": match.group(0),
                "parameter_id": parameter_id,
            }
    return None


def _first_category(text: str, candidates: list[tuple[list[str], str]], parameter_id: str) -> dict[str, Any] | None:
    for patterns, value in candidates:
        found = _category(text, patterns, value, parameter_id)
        if found:
            return found
    return None


def _captured_token(text: str, pattern: str, parameter_id: str, *, unit: str = "category") -> dict[str, Any] | None:
    match = re.search(pattern, text, re.I)
    if not match:
        return None
    return {
        "value": match.group(1),
        "unit": unit,
        "source": "user_explicit",
        "evidence_ref": "__requirement_source__",
        "raw_text": match.group(0),
        "parameter_id": parameter_id,
    }


def _parse_scalar_or_vector(raw: str) -> Any:
    value = raw.strip().strip("()")
    parts = value.split()
    try:
        numbers = [float(item) for item in parts]
    except ValueError:
        return raw.strip()
    return numbers[0] if len(numbers) == 1 else numbers


def _boundary_conditions(text: str) -> list[dict[str, Any]]:
    """Extract only explicit patch/field boundary statements.

    The patterns intentionally require a named field and patch. General engineering
    phrases remain for the case-planning specialist to resolve.
    """
    records: list[dict[str, Any]] = []

    def add(match: re.Match[str], bc_type: str, field: str, patch_names: list[str], value: Any = None) -> None:
        for patch in patch_names:
            record: dict[str, Any] = {
                "patch": patch,
                "field": field,
                "type": bc_type,
                "source": "user_explicit",
                "evidence_ref": "__requirement_source__",
                "raw_text": match.group(0),
            }
            if value is not None:
                record["value"] = value
            records.append(record)

    # OpenFOAM-style statements such as ``zeroGradient p at inlet and walls``.
    simple = re.compile(
        r"\b(zero[- ]?gradient|no[- ]?slip|fixedValue|empty|slip|symmetryPlane|inletOutlet)"
        r"\s+([A-Za-z][A-Za-z0-9_.]*)\s+(?:at|on)\s+(?:the\s+)?"
        r"([A-Za-z][A-Za-z0-9_.]*)(?:\s+and\s+(?:the\s+)?([A-Za-z][A-Za-z0-9_.]*))?",
        re.I,
    )
    type_map = {
        "zerogradient": "zeroGradient",
        "zero-gradient": "zeroGradient",
        "zero gradient": "zeroGradient",
        "noslip": "noSlip",
        "no-slip": "noSlip",
        "no slip": "noSlip",
        "fixedvalue": "fixedValue",
        "empty": "empty",
        "slip": "slip",
        "symmetryplane": "symmetryPlane",
        "inletoutlet": "inletOutlet",
    }
    for match in simple.finditer(text):
        normalized = re.sub(r"\s+", " ", match.group(1).lower())
        compact = normalized.replace(" ", "")
        bc_type = type_map.get(normalized, type_map.get(compact, match.group(1)))
        patches = [match.group(3)] + ([match.group(4)] if match.group(4) else [])
        add(match, bc_type, match.group(2), patches)

    # Explicit fixed values, e.g. ``fixedValue p=0 Pa at outlet``.
    fixed = re.compile(
        r"\bfixedValue\s+([A-Za-z][A-Za-z0-9_.]*)\s*=\s*"
        r"(\([^)]*\)|[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
        r"(?:\s*[A-Za-z0-9/^.*-]+)?\s+(?:at|on)\s+(?:the\s+)?([A-Za-z][A-Za-z0-9_.]*)",
        re.I,
    )
    for match in fixed.finditer(text):
        add(match, "fixedValue", match.group(1), [match.group(3)], _parse_scalar_or_vector(match.group(2)))

    # Natural-language velocity form, e.g. ``fixed velocity U=(1 0 0) m/s at inlet``.
    velocity = re.compile(
        r"\bfixed\s+velocity(?:\s+([A-Za-z][A-Za-z0-9_.]*))?\s*=\s*"
        r"(\([^)]*\)|[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
        r"(?:\s*m/s)?\s+(?:at|on)\s+(?:the\s+)?([A-Za-z][A-Za-z0-9_.]*)",
        re.I,
    )
    for match in velocity.finditer(text):
        add(match, "fixedValue", match.group(1) or "U", [match.group(3)], _parse_scalar_or_vector(match.group(2)))

    # Keep the last explicit statement for a patch/field pair.
    deduplicated: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        deduplicated[(record["patch"].lower(), record["field"])] = record
    return list(deduplicated.values())


def _bind_evidence_ref(value: Any, evidence_ref: str | None) -> Any:
    if isinstance(value, dict):
        return {key: (evidence_ref if key == "evidence_ref" and item == "__requirement_source__" else _bind_evidence_ref(item, evidence_ref)) for key, item in value.items()}
    if isinstance(value, list):
        return [_bind_evidence_ref(item, evidence_ref) for item in value]
    return value


def parse(text: str, evidence_ref: str | None = None) -> dict[str, Any]:
    lower = text.lower()
    phase = _first_category(
        text,
        [
            ([r"\b(vof|multiphase|free[- ]surface|dam break)\b"], "multiphase"),
            ([r"\b(single[- ]phase)\b"], "single_phase"),
        ],
        "phase_regime",
    )
    compressibility = _first_category(
        text,
        [
            ([r"\blow[- ]mach\b"], "low_mach"),
            ([r"\bincompressible\b"], "incompressible"),
            ([r"\bcompressible\b", r"\bshock\b", r"\bmach\b"], "compressible"),
        ],
        "compressibility",
    )
    flow_time = _first_category(
        text,
        [
            ([r"\bsteady(?:[- ]state)?\b"], "steady"),
            ([r"\btransient\b", r"\bunsteady\b"], "transient"),
        ],
        "flow_time",
    )
    algorithm = _first_category(
        text,
        [([r"\bPIMPLE\b"], "PIMPLE"), ([r"\bPISO\b"], "PISO"), ([r"\bSIMPLE\b"], "SIMPLE")],
        "algorithm",
    )
    module_match = re.search(r"foamRun\s+-solver\s+([A-Za-z0-9_]+)", text, re.I)
    module = None
    if module_match:
        module = {
            "value": module_match.group(1),
            "unit": "category",
            "source": "user_explicit",
            "evidence_ref": "__requirement_source__",
            "raw_text": module_match.group(0),
            "parameter_id": "solver_module",
        }
    legacy_match = re.search(r"\b(pimpleFoam|pisoFoam|simpleFoam|rhoSimpleFoam|rhoPimpleFoam|interFoam)\b", text, re.I)
    legacy = None
    if legacy_match:
        legacy = {
            "value": legacy_match.group(1),
            "unit": "category",
            "source": "user_explicit",
            "evidence_ref": "__requirement_source__",
            "raw_text": legacy_match.group(0),
            "parameter_id": "legacy_application",
        }

    controls = {
        "start_from": _captured_token(text, r"\bstartFrom\s*(?:=|is)?\s*(startTime|latestTime|firstTime)\b", "start_from"),
        "start_time": _value(text, rf"(?:startTime\s*(?:=|is)?\s*){NUMBER}", "s_or_iteration", "start_time"),
        "end_time": _value(text, rf"(?:endTime\s*(?:=|is)?\s*|(?:until|to)\s+(?:time\s*)?){NUMBER}", "s_or_iteration", "end_time"),
        "delta_t": _value(text, rf"(?:deltaT|time\s*step)\s*(?:=|is|of)?\s*{NUMBER}", "s_or_iteration", "delta_t"),
        "max_co": _value(text, rf"(?:maxCo|maximum\s+Courant(?:\s+number)?)\s*(?:=|is)?\s*{NUMBER}", "1", "max_co"),
        "write_interval": _value(text, rf"(?:writeInterval\s*(?:=|is)?\s*|(?:output|write|save)[^.\n]{{0,80}}?every\s+){NUMBER}", "s_or_iteration", "write_interval"),
    }
    write_control = _first_category(
        text,
        [
            ([r"writeControl\s+timeStep", r"every\s+\d+\s+time\s*steps?"], "timeStep"),
            ([r"writeControl\s+adjustableRunTime"], "adjustableRunTime"),
            ([r"writeControl\s+runTime", r"every\s+[0-9.eE+-]+\s*(?:s|seconds?)"], "runTime"),
        ],
        "write_control",
    )
    adjust_time_step = _first_category(
        text,
        [([r"adjustTimeStep\s+(?:true|yes|on)", r"adjustable\s+time\s*step"], True), ([r"adjustTimeStep\s+(?:false|no|off)", r"fixed\s+time\s*step"], False)],
        "adjust_time_step",
    )

    turbulence_type = _first_category(
        text,
        [
            ([r"\bLES\b", r"large\s+eddy"], "LES"),
            ([r"\bRAS\b", r"\bRANS\b", r"k[- ]?omega", r"k[- ]?epsilon"], "RAS"),
            ([r"\bDNS\b", r"direct\s+numerical"], "DNS"),
            ([r"\blaminar\b"], "laminar"),
        ],
        "turbulence_simulation_type",
    )
    turbulence_model = None
    for pattern, value in [
        (r"dynamic\s+kinetic\s+energy", "dynamicKEqn"),
        (r"k[- ]?omega\s*SST", "kOmegaSST"),
        (r"k[- ]?epsilon", "kEpsilon"),
        (r"Spalart[- ]Allmaras", "SpalartAllmaras"),
    ]:
        found = re.search(pattern, text, re.I)
        if found:
            turbulence_model = {
                "value": value,
                "unit": "category",
                "source": "user_explicit",
                "evidence_ref": "__requirement_source__",
                "raw_text": found.group(0),
                "parameter_id": "turbulence_model",
            }
            break

    material = {
        "nu": _value(text, rf"(?:kinematic\s+viscosity|\bnu\b)\s*(?:=|is|of)?\s*{NUMBER}", "m2/s", "nu"),
        "mu": _value(text, rf"(?:dynamic\s+viscosity|\bmu\b)\s*(?:=|is|of)?\s*{NUMBER}", "Pa.s", "mu"),
        "rho": _value(text, rf"(?:density|\brho\b)\s*(?:=|is|of)?\s*{NUMBER}", "kg/m3", "rho"),
        "temperature": _value(text, rf"(?:temperature|\bT\b)\s*(?:=|is|of)?\s*{NUMBER}\s*K", "K", "temperature"),
        "pressure": _value(text, rf"(?:pressure|\bp\b)\s*(?:=|is|of)?\s*{NUMBER}\s*Pa", "Pa", "pressure"),
        "inlet_velocity": _value(text, rf"inlet\s+velocity\s*(?:=|is|of)?\s*{NUMBER}\s*(?:m/s|m\s*s\^-1)", "m/s", "inlet_velocity"),
        "rpm": _value(text, rf"(?:speed|rotation|rotational\s+speed)\s*(?:=|is|of|at)?\s*{NUMBER}\s*rpm", "rpm", "rpm"),
    }

    geometry_source = "unspecified"
    if re.search(r"\b(stl|obj|surface\s+mesh)\b", lower):
        geometry_source = "surface_file"
    elif re.search(r"\b(cad|step|iges)\b", lower):
        geometry_source = "cad"
    elif re.search(r"\b(gmsh|\.msh|external\s+mesh|polyMesh)\b", text, re.I):
        geometry_source = "external_mesh"
    elif re.search(r"\b(cylinder|channel|cavity|box|pipe|bend|wedge)\b", lower):
        geometry_source = "parametric"

    mesh_method = _first_category(
        text,
        [
            ([r"\bsnappyHexMesh\b"], "snappyHexMesh"),
            ([r"\bblockMesh\b"], "blockMesh"),
            ([r"\bgmshToFoam\b", r"external\s+mesh"], "external"),
        ],
        "mesh_method",
    )

    patches: list[dict[str, Any]] = []
    for name, role, mesh_type, pattern in [
        ("inlet", "inlet", "patch", r"\binlet\b"),
        ("outlet", "outlet", "patch", r"\boutlet\b"),
        ("walls", "wall", "wall", r"\bwalls?\b"),
        ("frontAndBack", "empty", "empty", r"\bempty\b|\b2D\b"),
    ]:
        if re.search(pattern, text, re.I):
            patches.append({"name": name, "physical_role": role, "mesh_type": mesh_type})

    requested_visuals = []
    for token, field in [
        ("vorticity", "vorticity"),
        ("q-criterion", "Q"),
        ("lambda2", "lambda2"),
        ("streamline", "U"),
        ("velocity", "U"),
        ("pressure", "p"),
    ]:
        if token in lower:
            requested_visuals.append(field)

    result = {
        "raw_requirement": text,
        "phase_regime": phase,
        "compressibility": compressibility,
        "flow_time": flow_time,
        "algorithm": algorithm,
        "module": module,
        "legacy_application": legacy,
        "controls": controls,
        "write_control": write_control,
        "adjust_time_step": adjust_time_step,
        "turbulence_type": turbulence_type,
        "turbulence_model": turbulence_model,
        "material": material,
        "geometry_source": geometry_source,
        "mesh_method": mesh_method,
        "patches": patches,
        "boundary_conditions": _boundary_conditions(text),
        "requested_visuals": sorted(set(requested_visuals)),
        "flags": {
            "energy": bool(re.search(r"temperature|heat|thermal|enthalpy", lower)),
            "species": bool(re.search(r"species|combust|reaction|mixture", lower)),
            "mrf": bool(re.search(r"\bMRF\b|rotating\s+frame", text, re.I)),
            "moving_mesh": bool(re.search(r"moving\s+mesh|dynamic\s+mesh", lower)),
            "gravity": bool(re.search(r"gravity|buoyan", lower)),
            "complex_geometry": bool(re.search(r"vehicle|drivaer|airfoil|aerofoil|pump|turbine|rotor|propeller|cad|stl|obj", lower)),
            "no_slip": bool(re.search(r"no[- ]?slip", lower)),
            "zero_gradient_pressure_outlet": bool(re.search(r"zero[- ]?gradient\s+pressure\s+(?:at|on)\s+the\s+outlet", lower)),
        },
    }
    return _bind_evidence_ref(result, evidence_ref)


def _read_requirement(args: argparse.Namespace) -> tuple[str, str | None]:
    if args.requirement_text is not None:
        return args.requirement_text, None
    path = args.requirement_file.resolve(strict=True)
    return path.read_text(encoding="utf-8"), args.requirement_file.as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--requirement-text")
    source.add_argument("--requirement-file", type=Path)
    args = parser.parse_args()
    text, evidence_ref = _read_requirement(args)
    print(json.dumps(parse(text, evidence_ref), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
