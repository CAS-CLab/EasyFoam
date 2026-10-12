# Audit and Experience Gates

This reference preserves governance without restoring a detailed event ledger or automatic Skill evolution.

## Intake Gate

Use `case_spec.json` as the planning contract. Preserve the exact user requirement through a stable input reference. Do not require a second case-plan artifact.

## Write Gate

Use the formal `case/` tree as the materialized case. Record its validated content hash and optional mesh hash directly in `workflow.json`; do not create default first-generation, hash, mesh, or import manifests.

## Runtime Gate

Use `workflow.json` as the only Workflow state file. Each actual attempt creates one `runs/<attempt_id>/run_record.json` plus stdout/stderr logs for commands that were executed.

Required run evidence:

- command argv, cwd, timestamps, and return code;
- stdout/stderr references;
- terminal status and first deterministic error when available;
- blocked status when the required runtime is unavailable.

## Postprocess Gate

Use `evidence_summary.json` for requirement, case, mesh, execution, numerical, physical, QoI, output, and visual claims. Metric extractors return stdout by default. Persist only user-requested tables, plots, exports, images, or reports.

## Experience Gate

Experience records are optional passive facts. They never create a Candidate or modify a Skill by themselves.
