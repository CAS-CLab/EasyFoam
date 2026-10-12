"""Render an optional HTML report from canonical EasyFoam Workflow artifacts.

The report is a user-requested presentation artifact, not a state authority.
It reads ``case_spec.json``, ``workflow.json`` and, when available,
``evidence_summary.json``.  No classification or report manifest is written.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))

from skills._shared.scripts.artifact_io import read_json
from skills._shared.scripts.schema_validate import validate


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def table(headers: list[str], rows: list[list[object]]) -> str:
    head = "".join(f"<th>{esc(item)}</th>" for item in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{esc(item)}</td>" for item in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def _load_valid(path: Path, schema_name: str, *, required: bool) -> dict[str, Any] | None:
    if not path.is_file():
        if required:
            raise FileNotFoundError(f"required canonical artifact is missing: {path}")
        return None
    errors = validate(path, ROOT / "schemas" / schema_name)
    if errors:
        raise ValueError(f"invalid {path.name}: {'; '.join(errors)}")
    return read_json(path)


def render(run_dir: Path, output: Path) -> None:
    workflow = _load_valid(run_dir / "workflow.json", "workflow.schema.json", required=True)
    spec = _load_valid(run_dir / "case_spec.json", "case_spec.schema.json", required=False)
    evidence = _load_valid(run_dir / "evidence_summary.json", "evidence_summary.schema.json", required=False)
    assert workflow is not None

    title = (spec or {}).get("case_name") or workflow.get("case_id") or run_dir.name
    scope = workflow.get("requested_scope", {})

    artifact_rows: list[list[object]] = []
    for kind, value in workflow.get("artifacts", {}).items():
        if isinstance(value, list):
            artifact_rows.extend([[kind, item] for item in value])
        elif isinstance(value, dict):
            artifact_rows.append([kind, value.get("path", "")])
        elif value:
            artifact_rows.append([kind, value])

    assessment_rows: list[list[object]] = []
    if evidence:
        for category, item in evidence.get("assessments", {}).items():
            assessment_rows.append([
                category,
                item.get("status"),
                item.get("summary"),
                item.get("status_basis"),
                "; ".join(item.get("limitations", [])),
            ])

    qoi_rows: list[list[object]] = []
    if evidence:
        for item in evidence.get("qoi_results", []):
            qoi_rows.append([
                item.get("name"),
                item.get("status"),
                item.get("value"),
                item.get("unit"),
                item.get("method"),
                item.get("acceptance_criterion"),
                item.get("status_basis"),
            ])

    next_action = workflow.get("next_action")
    sections = [
        f"<h1>EasyFoam Workflow 报告：{esc(title)}</h1>",
        "<div class='summary'>"
        f"Workflow 状态：<b>{esc(workflow.get('status'))}</b>；"
        f"请求范围：{esc(', '.join(scope.get('stages', [])))}；"
        f"最后阶段：{esc(workflow.get('active_or_last_stage'))}"
        "</div>",
        "<h2>Workflow 合同</h2>" + table(
            ["字段", "值"],
            [
                ["目标", scope.get("goal")],
                ["已完成范围", ", ".join(workflow.get("completed_scope", []))],
                ["下一动作", json.dumps(next_action, ensure_ascii=False) if next_action else "无"],
                ["OpenFOAM", workflow.get("openfoam_version")],
            ],
        ),
    ]

    if evidence:
        overall = evidence.get("overall", {})
        sections.append(
            "<h2>最终证据结论</h2>" + table(
                ["状态", "最高支持声明", "摘要"],
                [[overall.get("status"), overall.get("highest_supported_claim"), overall.get("summary")]],
            )
        )
        sections.append(
            "<h2>分层评估</h2>" + table(
                ["类别", "状态", "摘要", "判断依据", "限制"], assessment_rows
            )
        )
        if qoi_rows:
            sections.append(
                "<h2>QoI</h2>" + table(
                    ["名称", "状态", "值", "单位", "方法", "准则", "判断依据"], qoi_rows
                )
            )
        limitations = evidence.get("limitations", [])
        sections.append(
            "<h2>限制与审阅项</h2><ul>"
            + ("".join(f"<li>{esc(item)}</li>" for item in limitations) or "<li>无已记录限制。</li>")
            + "</ul>"
        )
    else:
        sections.append("<div class='notice'>当前未提供 evidence_summary.json；本报告不作数值或物理可信度结论。</div>")

    sections.append("<h2>Canonical Artifact 引用</h2>" + table(["类型", "路径"], artifact_rows))

    css = """
    body{font-family:Segoe UI,Microsoft YaHei,sans-serif;max-width:1400px;margin:32px auto;padding:0 24px;color:#172033;line-height:1.55}
    h1,h2{color:#123b5d}h2{margin-top:30px}table{border-collapse:collapse;width:100%;margin:12px 0 24px}
    th,td{border:1px solid #cbd5e1;padding:8px;text-align:left;vertical-align:top}th{background:#eaf3f9}
    .summary,.notice{padding:14px;background:#f8fafc;border-left:5px solid #276a91;margin:16px 0}.notice{border-left-color:#b7791f}
    """
    document = (
        "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
        f"<title>{esc(title)}</title><style>{css}</style></head><body>"
        + "".join(sections)
        + "</body></html>"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render(args.run_dir, args.output)
    print(json.dumps({"status": "passed", "output": args.output.as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(json.dumps({"status": "failed", "reason": str(exc)}, ensure_ascii=False))
        raise SystemExit(1)
