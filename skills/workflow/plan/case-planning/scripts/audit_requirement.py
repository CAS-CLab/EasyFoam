"""Audit a user requirement before CaseSpec release.

The command accepts either natural-language text or a user-provided TXT file.
It prints missing decisive items, concrete clarification questions, and detected
conflicts. Exit code 0 means releasable by this conservative pre-audit, 1 means
conflicting/invalid input, and 2 means user clarification is required.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from parse_requirement import parse

QUESTIONS = {
    "phase_regime": "Is the problem single-phase or multiphase?",
    "compressibility": "Should the flow be treated as incompressible, low-Mach, or compressible?",
    "flow_time": "Is the target simulation steady or transient?",
    "solver_module_or_application": "Which OpenFOAM v13 solver module or legacy application is required?",
    "algorithm": "Which pressure-velocity algorithm is required: SIMPLE, PISO, or PIMPLE?",
    "turbulence_treatment": "Should the case be laminar, RAS, LES, or DNS, and which model is required if applicable?",
    "patch_inventory": "What are the mesh patch names and their physical roles?",
}


def audit(text: str, evidence_ref: str | None = None) -> dict[str, Any]:
    parsed = parse(text, evidence_ref)
    missing: list[str] = []
    if parsed["phase_regime"] is None:
        missing.append("phase_regime")
    if parsed["compressibility"] is None:
        missing.append("compressibility")
    if parsed["flow_time"] is None:
        missing.append("flow_time")
    if parsed["module"] is None and parsed["legacy_application"] is None:
        missing.append("solver_module_or_application")
    if parsed["algorithm"] is None and parsed["legacy_application"] is None:
        missing.append("algorithm")
    if parsed["turbulence_type"] is None:
        missing.append("turbulence_treatment")
    if not parsed["patches"]:
        missing.append("patch_inventory")

    conflicts: list[str] = []
    if parsed["flags"]["complex_geometry"] and parsed["mesh_method"] and parsed["mesh_method"]["value"] == "blockMesh":
        conflicts.append("complex geometry cannot be represented by a blockMesh-only route without an explicit toy/background-domain contract")

    questions = [QUESTIONS[item] for item in missing]
    return {
        "status": "failed" if conflicts else ("blocked" if missing else "passed"),
        "review_required": bool(missing),
        "missing_decisive": missing,
        "clarification_questions": questions,
        "conflicts": conflicts,
        "parsed": parsed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--requirement-text")
    source.add_argument("--requirement-file", type=Path)
    args = parser.parse_args()
    if args.requirement_text is not None:
        text, evidence_ref = args.requirement_text, None
    else:
        path = args.requirement_file.resolve(strict=True)
        text, evidence_ref = path.read_text(encoding="utf-8"), args.requirement_file.as_posix()
    result = audit(text, evidence_ref)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["conflicts"]:
        return 1
    return 2 if result["review_required"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
