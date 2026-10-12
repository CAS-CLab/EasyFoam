"""Render one requested OpenFOAM visual with ParaView/pvpython.

The script writes only the requested image or animation. Rendering parameters
are supplied directly; no visual-contract or manifest JSON is created.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def triple(value: str) -> list[float]:
    parts = [float(item) for item in value.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("expected x,y,z")
    return parts


def pair(value: str) -> list[int]:
    parts = [int(item) for item in value.split(",")]
    if len(parts) != 2 or min(parts) <= 0:
        raise argparse.ArgumentTypeError("expected positive width,height")
    return parts


def _association(value: str) -> str:
    return "POINTS" if value == "point" else "CELLS"


def _set_camera(view: Any, args: argparse.Namespace) -> None:
    if args.camera_position:
        view.CameraPosition = args.camera_position
    if args.camera_focal_point:
        view.CameraFocalPoint = args.camera_focal_point
    if args.camera_view_up:
        view.CameraViewUp = args.camera_view_up
    if args.parallel_projection:
        view.CameraParallelProjection = 1


def _apply_range(lut: Any, source: Any, association: str, field: str, args: argparse.Namespace) -> None:
    if args.range_mode == "fixed":
        if args.range_min is None or args.range_max is None:
            raise ValueError("fixed range requires --range-min and --range-max")
        lut.RescaleTransferFunction(args.range_min, args.range_max)
    elif args.range_mode == "symmetric":
        if args.range_max is not None:
            bound = abs(args.range_max)
        elif args.range_min is not None:
            bound = abs(args.range_min)
        else:
            source.UpdatePipeline()
            info = source.GetPointDataInformation() if association == "POINTS" else source.GetCellDataInformation()
            array = info.GetArray(field)
            if array is None:
                raise ValueError(f"field not available for symmetric range: {field}")
            limits = array.GetComponentRange(-1)
            bound = max(abs(limits[0]), abs(limits[1]))
        lut.RescaleTransferFunction(-bound, bound)
    else:
        lut.RescaleTransferFunctionToDataRange(True, False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-file", type=Path, required=True, help="OpenFOAM .foam file")
    parser.add_argument("--kind", choices=["mesh", "contour", "slice", "streamline", "vector", "isosurface", "animation"], required=True)
    parser.add_argument("--field", default="U")
    parser.add_argument("--component", default="Magnitude")
    parser.add_argument("--association", choices=["point", "cell"], default="point")
    parser.add_argument("--mesh-region", action="append", default=[])
    parser.add_argument("--time", type=float)
    parser.add_argument("--time-start", type=float)
    parser.add_argument("--time-end", type=float)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=pair, default=[1600, 900])
    parser.add_argument("--slice-origin", type=triple, default=[0.0, 0.0, 0.0])
    parser.add_argument("--slice-normal", type=triple, default=[0.0, 0.0, 1.0])
    parser.add_argument("--seed-kind", choices=["point", "line"], default="point")
    parser.add_argument("--seed-center", type=triple, default=[0.0, 0.0, 0.0])
    parser.add_argument("--seed-radius", type=float, default=1.0)
    parser.add_argument("--seed-count", type=int, default=200)
    parser.add_argument("--seed-point1", type=triple)
    parser.add_argument("--seed-point2", type=triple)
    parser.add_argument("--integration-direction", choices=["FORWARD", "BACKWARD", "BOTH"], default="BOTH")
    parser.add_argument("--vector-scale", type=float, default=1.0)
    parser.add_argument("--vector-every-nth", type=int, default=1)
    parser.add_argument("--iso-value", type=float, action="append", default=[])
    parser.add_argument("--range-mode", choices=["data", "fixed", "symmetric"], default="data")
    parser.add_argument("--range-min", type=float)
    parser.add_argument("--range-max", type=float)
    parser.add_argument("--camera-position", type=triple)
    parser.add_argument("--camera-focal-point", type=triple)
    parser.add_argument("--camera-view-up", type=triple)
    parser.add_argument("--parallel-projection", action="store_true")
    parser.add_argument("--background", type=triple)
    parser.add_argument("--frame-rate", type=int, default=24)
    args = parser.parse_args()

    try:
        from paraview.simple import (
            OpenFOAMReader, GetAnimationScene, GetActiveViewOrCreate, Show,
            ColorBy, GetColorTransferFunction, Render, SaveScreenshot,
            SaveAnimation, Slice, StreamTracer, Glyph, Contour, Calculator,
            ResetCamera, Hide, GetTimeKeeper,
        )
    except Exception as exc:
        print(json.dumps({"status": "blocked", "reason": f"ParaView Python unavailable: {exc}"}, ensure_ascii=False))
        return 2

    if not args.case_file.is_file():
        print(json.dumps({"status": "failed", "reason": f"case file not found: {args.case_file}"}, ensure_ascii=False))
        return 1
    if args.kind == "animation" and args.output.suffix.lower() not in {".avi", ".mp4", ".png"}:
        print(json.dumps({"status": "failed", "reason": "animation output must be .avi, .mp4, or a numbered .png sequence"}, ensure_ascii=False))
        return 1

    association = _association(args.association)
    reader = OpenFOAMReader(FileName=str(args.case_file.resolve()))
    reader.MeshRegions = args.mesh_region or ["internalMesh"]
    scene = GetAnimationScene()
    scene.UpdateAnimationUsingDataTimeSteps()
    if args.time is not None:
        scene.AnimationTime = args.time

    source = reader
    color_source = source
    if args.kind == "slice":
        source = Slice(Input=reader)
        source.SliceType = "Plane"
        source.SliceType.Origin = args.slice_origin
        source.SliceType.Normal = args.slice_normal
        color_source = source
    elif args.kind == "streamline":
        seed_type = "Point Cloud" if args.seed_kind == "point" else "Line"
        source = StreamTracer(Input=reader, SeedType=seed_type)
        source.Vectors = [association, args.field]
        source.IntegrationDirection = args.integration_direction
        if args.seed_kind == "point":
            source.SeedType.Center = args.seed_center
            source.SeedType.Radius = args.seed_radius
            source.SeedType.NumberOfPoints = args.seed_count
        else:
            if args.seed_point1 is None or args.seed_point2 is None:
                raise ValueError("line seeds require --seed-point1 and --seed-point2")
            source.SeedType.Point1 = args.seed_point1
            source.SeedType.Point2 = args.seed_point2
            source.SeedType.Resolution = max(1, args.seed_count - 1)
        color_source = source
    elif args.kind == "vector":
        source = Glyph(Input=reader, GlyphType="Arrow")
        source.OrientationArray = [association, args.field]
        source.ScaleArray = [association, args.field]
        source.ScaleFactor = args.vector_scale
        source.GlyphMode = "Every Nth Point"
        source.Stride = max(1, args.vector_every_nth)
        color_source = source
    elif args.kind == "isosurface":
        if not args.iso_value:
            raise ValueError("isosurface requires at least one --iso-value")
        source = Contour(Input=reader)
        source.ContourBy = [association, args.field]
        source.Isosurfaces = args.iso_value
        color_source = source
    elif args.kind == "animation":
        # Animation uses the same field coloring as a contour view of the full domain.
        color_source = reader

    view = GetActiveViewOrCreate("RenderView")
    if args.background:
        view.Background = args.background
    display = Show(source, view)
    if args.kind == "mesh":
        display.Representation = "Surface With Edges"
    else:
        display.Representation = "Surface"
        ColorBy(display, (association, args.field, args.component))
        lut = GetColorTransferFunction(args.field)
        _apply_range(lut, color_source, association, args.field, args)
        display.SetScalarBarVisibility(view, True)

    ResetCamera(view)
    _set_camera(view, args)
    Render()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.kind == "animation":
        time_keeper = GetTimeKeeper()
        available = list(time_keeper.TimestepValues or [])
        if args.time_start is not None:
            available = [value for value in available if value >= args.time_start]
        if args.time_end is not None:
            available = [value for value in available if value <= args.time_end]
        if not available:
            raise ValueError("no timesteps satisfy the requested animation range")
        scene.StartTime = available[0]
        scene.EndTime = available[-1]
        SaveAnimation(str(args.output.resolve()), view, ImageResolution=args.size, FrameRate=args.frame_rate)
    else:
        SaveScreenshot(str(args.output.resolve()), view, ImageResolution=args.size)

    if args.kind == "animation" and args.output.suffix.lower() == ".png":
        rendered = sorted(path for path in args.output.parent.glob(f"{args.output.stem}*.png") if path.is_file() and path.stat().st_size > 0)
        ok = bool(rendered)
        output_value: Any = [path.as_posix() for path in rendered]
    else:
        ok = args.output.is_file() and args.output.stat().st_size > 0
        output_value = args.output.as_posix()
    print(json.dumps({
        "status": "available" if ok else "failed",
        "output": output_value,
        "kind": args.kind,
        "field": args.field,
        "association": args.association,
        "time": args.time,
        "range_mode": args.range_mode,
    }, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(json.dumps({"status": "failed", "reason": str(exc)}, ensure_ascii=False))
        raise SystemExit(1)
