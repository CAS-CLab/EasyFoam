"""Rank local tutorial/reference files for one bounded planning question."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def tokens(text: str) -> set[str]:
    return {item.lower() for item in re.findall(r"[A-Za-z0-9_+.-]{2,}", text)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, action="append", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    query = tokens(args.query)
    matches = []
    for root in args.root:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".json", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            hay = tokens(path.as_posix()) | tokens(text[:20000])
            score = len(query & hay)
            if score:
                matches.append({"path": path.as_posix(), "score": score, "matched_terms": sorted(query & hay)})
    result = {"query": args.query, "matches": sorted(matches, key=lambda x: (-x["score"], x["path"]))[: max(1, args.limit)]}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["matches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
