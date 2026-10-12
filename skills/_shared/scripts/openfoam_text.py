"""Small deterministic readers for OpenFOAM text files and logs.

These helpers intentionally cover only inventories and diagnostics required by
EasyFoam static checks. They are not a general OpenFOAM dictionary parser.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def read_text(path: Path) -> str:
    return strip_comments(path.read_text(encoding="utf-8", errors="replace"))


def named_blocks(text: str) -> list[tuple[str, str]]:
    """Return balanced ``name { body }`` blocks at the current text level.

    OpenFOAM dictionaries often place opening braces on the same line as the
    name.  This scanner therefore does not depend on line layout.  Once a
    top-level block is found, nested blocks are kept in its body and are not
    returned separately.
    """
    text = strip_comments(text)
    blocks: list[tuple[str, str]] = []
    index = 0
    token = re.compile(r"[A-Za-z_][A-Za-z0-9_.:+-]*")
    while index < len(text):
        match = token.match(text, index)
        if not match:
            index += 1
            continue
        name = match.group(0)
        cursor = match.end()
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        if cursor >= len(text) or text[cursor] != "{":
            index = match.end()
            continue
        depth = 0
        end = None
        for pos in range(cursor, len(text)):
            char = text[pos]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    end = pos
                    break
        if end is None:
            break
        if name != "FoamFile":
            blocks.append((name, text[cursor + 1:end]))
        index = end + 1
    return blocks


def parse_boundary_file(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    result: list[dict[str, Any]] = []
    for name, body in named_blocks(read_text(path)):
        kind = re.search(r"\btype\s+([^;\s]+)\s*;", body)
        nfaces = re.search(r"\bnFaces\s+(\d+)\s*;", body)
        startface = re.search(r"\bstartFace\s+(\d+)\s*;", body)
        if kind or nfaces or startface:
            result.append({
                "name": name,
                "type": kind.group(1) if kind else None,
                "nFaces": int(nfaces.group(1)) if nfaces else None,
                "startFace": int(startface.group(1)) if startface else None,
            })
    return result


def parse_zone_names(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return sorted({name for name, _ in named_blocks(read_text(path))})


def parse_field_boundary_names(path: Path) -> list[str]:
    if not path.is_file():
        return []
    text = read_text(path)
    marker = re.search(r"\bboundaryField\s*\{", text)
    if not marker:
        return []
    start = text.find("{", marker.start())
    depth = 0
    end = None
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                end = index
                break
    if end is None:
        return []
    return [name for name, _ in named_blocks(text[start + 1:end])]


def find_placeholders(case_dir: Path) -> list[str]:
    patterns = [
        # Do not treat OpenFOAM type syntax such as ``List<scalar>`` as a
        # placeholder.  Explicit workflow markers below are the only
        # placeholders this static check owns.
        re.compile(r"\breview_required\b", re.I),
        re.compile(r"\bTODO\b", re.I),
        re.compile(r"\bTBD\b", re.I),
    ]
    hits: list[str] = []
    for path in sorted(case_dir.rglob("*")):
        if not path.is_file() or path.stat().st_size > 5_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if any(pattern.search(text) for pattern in patterns):
            hits.append(path.relative_to(case_dir).as_posix())
    return hits


def parse_checkmesh_log(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lower = text.lower()

    def number(pattern: str, cast=float):
        match = re.search(pattern, text, re.I)
        if not match:
            return None
        try:
            return cast(match.group(1))
        except ValueError:
            return None

    fatal_patterns = {
        "negative_volume": r"negative volume|negative-volume|cells with negative volume",
        "invalid_topology": r"failed topology checks|mesh has .* topology errors|\*\*\*error in mesh topology",
        "illegal_faces": r"illegal faces|faces with .* illegal",
        "multiple_regions": r"number of regions:\s*([2-9]\d*)",
    }
    fatal = [name for name, pattern in fatal_patterns.items() if re.search(pattern, text, re.I)]
    failed_count = number(r"failed\s+(\d+)\s+mesh checks", int)
    if failed_count:
        fatal.append(f"failed_checks:{failed_count}")

    warning_lines = [
        line.strip() for line in text.splitlines()
        if re.search(r"\bwarning\b|highly non-orthogonal|severe skew", line, re.I)
    ]
    passed_terminal = "mesh ok." in lower and not fatal
    return {
        "passed": passed_terminal,
        "terminal_found": "mesh ok." in lower or "failed" in lower or "fatal" in lower,
        "cells": number(r"\bcells:\s*(\d+)", int),
        "faces": number(r"\bfaces:\s*(\d+)", int),
        "points": number(r"\bpoints:\s*(\d+)", int),
        "regions": number(r"number of regions:\s*(\d+)", int),
        "max_aspect_ratio": number(r"max aspect ratio\s*=\s*([0-9.eE+\-]+)"),
        "max_non_orthogonality": number(
            r"(?:mesh\s+)?non-orthogonality\s+max:\s*([0-9.eE+\-]+)"
        ),
        "max_skewness": number(r"max skewness\s*=\s*([0-9.eE+\-]+)"),
        "min_volume": number(r"min volume\s*=\s*([0-9.eE+\-]+)"),
        "warnings": list(dict.fromkeys(warning_lines)),
        "fatal": sorted(set(fatal)),
        "source": path.as_posix(),
    }
