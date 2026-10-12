"""Validate requested visual outputs for containment, readability, and format."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}
VIDEO_SUFFIXES = {".avi", ".mp4"}
STATE_SUFFIXES = {".pvsm"}
ALLOWED = IMAGE_SUFFIXES | VIDEO_SUFFIXES | STATE_SUFFIXES


def _inside(path: Path, root: Path) -> Path:
    resolved_root = root.resolve(strict=True)
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(resolved_root):
        raise ValueError(f"visual artifact escapes approved root: {path}")
    return resolved


def _image_metadata(path: Path) -> dict[str, Any]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required to validate image readability") from exc
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        return {"width": image.width, "height": image.height, "format": image.format}


def _video_metadata(path: Path) -> dict[str, Any]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("ffprobe is required to validate video readability")
    completed = subprocess.run(
        [
            ffprobe,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height,nb_frames,duration",
            "-of", "json",
            str(path),
        ],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "ffprobe could not decode the video")
    payload = json.loads(completed.stdout)
    streams = payload.get("streams", [])
    if not streams:
        raise RuntimeError("video contains no readable video stream")
    return streams[0]


def _state_metadata(path: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    return {"root_tag": root.tag, "xml_readable": True}


def validate_one(path: Path, approved_root: Path) -> dict[str, Any]:
    item: dict[str, Any] = {
        "path": path.as_posix(),
        "available": False,
        "bytes": 0,
        "format_supported": path.suffix.lower() in ALLOWED,
        "readable": False,
        "metadata": {},
        "reason": "",
    }
    try:
        resolved = _inside(path, approved_root)
        item["path"] = resolved.relative_to(approved_root.resolve(strict=True)).as_posix()
        item["bytes"] = resolved.stat().st_size
        if item["bytes"] <= 0:
            raise ValueError("visual file is empty")
        suffix = resolved.suffix.lower()
        if suffix not in ALLOWED:
            raise ValueError(f"unsupported visual suffix: {suffix}")
        if suffix in IMAGE_SUFFIXES:
            item["metadata"] = _image_metadata(resolved)
        elif suffix in VIDEO_SUFFIXES:
            item["metadata"] = _video_metadata(resolved)
        else:
            item["metadata"] = _state_metadata(resolved)
        item["readable"] = True
        item["available"] = True
    except (OSError, ValueError, RuntimeError, ET.ParseError, json.JSONDecodeError) as exc:
        item["reason"] = str(exc)
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-root", type=Path, required=True)
    parser.add_argument("--path", type=Path, action="append", required=True)
    args = parser.parse_args()
    items = [validate_one(path, args.approved_root) for path in args.path]
    passed = all(item["available"] for item in items)
    print(json.dumps({"passed": passed, "artifacts": items}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
