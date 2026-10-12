"""Extract field-wise residual histories from an OpenFOAM solver log."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import median

TIME_RE = re.compile(r"^Time\s*=\s*([^\s]+)", re.M)
SOLVE_RE = re.compile(
    r"Solving for\s+(?P<field>[^,\s]+),\s*Initial residual\s*=\s*(?P<initial>[0-9.eE+\-]+),\s*Final residual\s*=\s*(?P<final>[0-9.eE+\-]+),\s*No Iterations\s+(?P<iterations>\d+)",
    re.I,
)


def _trend(values: list[float]) -> str:
    if len(values) < 2:
        return "insufficient"
    first = median(values[: max(1, len(values)//4)])
    last = median(values[-max(1, len(values)//4):])
    if last < first * 0.5:
        return "decreasing"
    if last > first * 2.0:
        return "increasing"
    return "flat_or_oscillatory"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    args = parser.parse_args()
    text = args.log.read_text(encoding="utf-8", errors="replace")
    current_time = None
    rows = []
    for line in text.splitlines():
        time_match = re.match(r"^Time\s*=\s*([^\s]+)", line)
        if time_match:
            current_time = time_match.group(1)
            continue
        match = SOLVE_RE.search(line)
        if match:
            rows.append({
                "time_or_iteration": current_time,
                "field": match.group("field"),
                "initial_residual": float(match.group("initial")),
                "final_residual": float(match.group("final")),
                "iterations": int(match.group("iterations")),
            })
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["field"]].append(row)
    summary = {}
    for field, records in grouped.items():
        initials = [row["initial_residual"] for row in records]
        finals = [row["final_residual"] for row in records]
        spikes = sum(1 for prev, cur in zip(initials, initials[1:]) if prev > 0 and cur > prev * 10)
        summary[field] = {
            "count": len(records),
            "first_initial": initials[0],
            "last_initial": initials[-1],
            "minimum_initial": min(initials),
            "maximum_initial": max(initials),
            "last_final": finals[-1],
            "trend": _trend(initials),
            "spike_count": spikes,
        }
    print(json.dumps({"source": args.log.as_posix(), "record_count": len(rows), "history": rows, "fields": summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
