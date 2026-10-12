# EasyFoam

[中文说明](README_zh.md) | [Paper draft (PDF)](docs/EasyFoam-draft.pdf) | [Project website](https://cas-clab.github.io/EasyFoam/)

EasyFoam is a Skill-based, contract-driven, evidence-oriented CFD workflow library for **OpenFOAM Foundation v13**. It guides a coding agent with file and command execution capabilities through case planning, authoring, execution, recovery, validation, and postprocessing. When explicitly requested by the user, verified workflow experience can also be distilled into reviewed and reversible Skill updates.

> EasyFoam is not a new CFD solver and is not a monolithic one-click CLI. OpenFOAM performs the numerical solve; EasyFoam organizes the user requirement, CaseSpec, case files, runtime attempts, validation evidence, and reusable repairs into an auditable engineering workflow.

> **Project status: engineering research release.** The formal contracts currently focus on single-region OpenFOAM Foundation v13 workflows. Production design, certification, safety-critical analysis, and high-cost engineering decisions still require review by a qualified CFD engineer.

## Paper

The accompanying paper, **EasyFoam: Skill-Oriented OpenFOAM Agents with Evidence-Driven Evolution**,
is available as a [draft PDF](docs/EasyFoam-draft.pdf).
This repository provides the usable EasyFoam library, including Workflow,
human-governed Evolution, References, deterministic scripts, and their Schemas.

## 1. Key Features

- **End-to-end Workflow loop**: `Plan → Write → Run → Postprocess`.
- **Human-governed Evolution loop**: `Experience → Candidate → Validation → Human Decision → Apply / Defer / Reject / Rollback`.
- **Requirement-grounded CaseSpec**: a CaseSpec is derived only from the current natural-language request or a user-provided TXT path.
- **No guessing of decisive CFD information**: missing or conflicting inputs remain blocking review items; the agent asks concrete questions and updates the same CaseSpec after the user replies.
- **OpenFOAM v13 contracts** for solver modules, fields, dictionaries, meshes, run controls, QoIs, and postprocessing.
- **Separated evidence claims** for file correctness, mesh contract, execution, numerical credibility, physical credibility, and QoI acceptance.
- **Recoverable Workflow state**: `advance` atomically completes and routes a stage; `reopen` invalidates the earliest affected completed stage and its downstream claims.
- **Minimal loading**: one active stage, one active specialist, and only the References needed for the current decision.
- **Reversible evolution** with frozen patches, validation levels, explicit authorization, retention review, and rollback.

## 2. Supported Scope

The current release formally targets:

- OpenFOAM Foundation v13;
- single-region CFD workflows;
- Windows hosts executing OpenFOAM through WSL;
- native OpenFOAM execution on Linux or inside WSL;
- generated, imported, or reused meshes with explicit patch, zone, interface, and quality contracts;
- agent-coordinated case creation, execution, diagnosis, validation, visualization, and recovery;
- evidence-linked and human-governed changes to Skills, References, scripts, and Schemas.

## 3. Architecture

```text
User request
├── Workflow
│   └── Plan → Write → Run → Postprocess
├── Evolution
│   └── Experience → Candidate → Review and Validation
│       → Human Decision → Apply / Defer / Reject / Rollback
└── Reference
    └── Read-only OpenFOAM, CFD, tutorial-pattern, and governance knowledge
```

| Layer | Responsibility | May modify formal Skills? |
| --- | --- | --- |
| Workflow | Complete, resume, repair, run, and validate the current CFD task; passively retain Experience | No |
| Evolution | Turn verified Experience into reviewed, reversible library changes | Only after explicit user authorization |
| Reference | Supply read-only technical and governance evidence | No |

The root router is `skills/SKILL.md`; detailed intent and state routing is defined in `skills/ROUTING.md`.

## 4. Loading Model

Start the agent from the repository root and load `skills/SKILL.md` first. Then use `skills/ROUTING.md` to bind the smallest user-scoped target, select Workflow/Evolution/Reference, load one active stage, one active specialist, and only the References needed for the current decision. Do not preload the complete Skill tree, all historical runs, or all Experience records.

## 5. Workflow Loop

### Plan

Plan creates `case_spec.json` from either the current natural-language request or a user-provided TXT path. It does not require a copied `user_requirement.txt` inside the run directory.

Plan resolves or blocks physics, phase regime, compressibility, time behavior, turbulence and other models, solver module and algorithm, geometry and mesh route, fields, boundaries, material properties, run controls, outputs, QoIs, and validation boundaries.

When decisive information is missing, the CaseSpec remains schema-valid but unreleased. Related blocking items are consolidated into concrete user questions. After the user replies, the same CaseSpec is revised, the corresponding review items are resolved, and schema plus semantic release checks are rerun. Write cannot start while a blocking item remains unresolved.

### Write

Write materializes a schema-valid and semantically released CaseSpec into one formal `case/` tree. Mesh generation, external mesh import/reuse, and case authoring remain separate specialist responsibilities. External mesh conversion requires a real source, format, and executable converter command; placeholders such as `<converter>` are not valid formal commands.

Before recording hashes and advancing Workflow, case authoring reruns the CaseSpec semantic release gate and validates the actual patch/zone/field and algorithm contracts.

### Run

Run supports `formal`, `resume`, `smoke`, and `diagnostic` attempts. Each actual attempt creates an immutable `runs/<attempt_id>/run_record.json` plus command stdout/stderr logs.

A failed formal attempt is classified by `debug-reviewer`. Requirement changes return to Plan; formal case or mesh changes reopen Write; invocation, environment, or restart-only changes remain in Run. Immutable prior run records remain available for audit, while superseded stage-scoped evidence no longer supports the current outcome.

### Postprocess

Postprocess extracts residual, runtime, mesh, probe, force, field, and QoI evidence; creates requested tables, exports, reports, and ParaView visuals; and assesses requirement, mesh, numerical, physical, conservation, boundedness, and QoI claims. Only `physics-validation` writes `evidence_summary.json`.

Execution success does not establish numerical or physical credibility, and visual evidence does not replace quantitative validation.

## 6. Evolution Loop

Evolution starts only on explicit user request:

```text
Verified Workflow evidence
→ Experience
→ Candidate
→ Validation
→ Human decision
→ Apply / Apply Limited / Reject / Defer / Revise
→ Retention or Rollback
```

A verified repair, reusable successful pattern, complete natural failure hypothesis, or unresolved failure may be retained as `experience_record.json`. Successful or verified reusable observations require explicit execution, numerical, physical, and QoI evidence; unresolved failures remain Candidate-ineligible. Compatible Experience records may be distilled into an atomic frozen `candidate_patch.json` plus patch. Candidate validation and application authorization remain separate. Application, limited application, retention, and rollback all require explicit human instruction.

`apply_candidate.py` records post-apply validation through `--validation-argv-json` or `--validation-command`; it does not automatically commit, merge, or push.

## 7. Reference Layer

| Area | Content |
| --- | --- |
| `skills/reference/openfoam13/` | version rules, clarification, solver/module mapping, consistency audit, geometry policy |
| `skills/reference/solver_modules/` | field families, algorithms, dictionary requirements, module compatibility |
| `skills/reference/tutorial_families/` | reusable structural patterns for major CFD families |
| `skills/reference/tutorial_patterns/` | local tutorial indexes and module-to-family mappings |
| `skills/reference/evolution/` | Experience, Candidate, validation, promotion, retention, and rollback policy |
| Specialist `references/` | mesh, boundary, dictionary, runtime, diagnostic, QoI, postprocessing, and visualization rules |

References are evidence sources, not automatic answers. Explicit user requirements and actual case evidence remain authoritative.

## 8. Canonical Artifacts

| Artifact | Schema | Owner | Purpose |
| --- | ---: | --- | --- |
| `case_spec.json` | 1.2 | Plan / case-planning | requirement source, simulation contract, provenance, review items |
| `workflow.json` | 2.2 | Workflow ledger | stages, artifacts, stage-scoped evidence, blockers, next action |
| `runs/<attempt_id>/run_record.json` | 1.1 | Run / runner | immutable environment, command, terminal, hash, restart evidence |
| `evidence_summary.json` | 2.1 | Postprocess / physics-validation | bounded final assessment and highest supported claim |
| `experience_record.json` | 2.1 | Evolution / case-specific-fix | verified reusable behavior or unresolved failure |
| `candidate_patch.json` | 2.1 | Evolution / candidate-patch | frozen proposed change and validation state |
| `promotion_record.json` | 2.1 | Evolution / promoted-skill | human decision, application, retention, limitation, rollback |

## 9. Repository Layout

```text
.
├── README.md
├── README_zh.md
├── LICENSE
├── requirements.txt
├── requirements-visual.txt
├── .env.example
├── .gitignore
├── docs/
│   ├── index.html
│   ├── index_zh.html
│   ├── static/
│   └── EasyFoam-draft.pdf
├── schemas/
└── skills/
    ├── SKILL.md
    ├── ROUTING.md
    ├── workflow/
    ├── evolution/
    ├── reference/
    └── _shared/scripts/
```

Skills define responsibility, boundaries, and decision procedures. Nearby `references/` contain reusable knowledge. `scripts/` implement deterministic parsing, validation, hashing, state updates, and execution.

## 10. Environment

### Python

Python 3.11 or 3.12 and `jsonschema` are required. Pillow is optional for visual artifact checks; install `requirements-visual.txt` when needed. Git is required for Candidate construction, validation, application, and rollback. A coding agent with file and command execution capabilities is required to orchestrate the Skills; configure the model and credentials in your agent runtime.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### OpenFOAM v13

Set the OpenFOAM environment script path as visible in the selected shell:

```bash
export EASYFOAM_OPENFOAM_BASHRC=/opt/openfoam13/etc/bashrc
export EASYFOAM_EXEC_BACKEND=auto
```

`auto` selects WSL on a Windows host and native execution on Linux or inside WSL. `wsl` and `native` may also be selected explicitly.

```bash
python skills/_shared/scripts/openfoam_env.py discover
```

A successful result reports backend, platform, OpenFOAM version `13`, and paths for `foamRun`, `blockMesh`, `checkMesh`, and `foamPostProcess` when available. Use the Foundation release; OpenCFD releases require a separate adapter. Parallel execution requires MPI. ParaView `pvpython` is optional for requested visual diagnostics. `.env.example` documents the OpenFOAM variables; set them in the shell used by your agent.

## 11. Quick Start

Start the agent from the repository root.

### Natural-language requirement

```text
Use EasyFoam Skills to complete the following OpenFOAM v13 task.

CFD task:
<user requirement>

Fixed run directory:
<run directory>
```

### Requirement TXT path

```text
Use EasyFoam Skills to complete the OpenFOAM v13 task described by the following TXT file.

CFD requirement file:
<TXT file path>

Fixed run directory:
<run directory>
```

The Skills already define stage order, evidence retention, formal-control preservation, clarification behavior, and the rule that Evolution does not start automatically. These instructions do not need to be repeated in the user prompt.

### Resume

```text
Use EasyFoam Skills to resume the following OpenFOAM v13 task.

Fixed run directory:
<existing run directory>
```

### Review reusable experience

```text
Use EasyFoam Skills to review reusable experience from this completed task.

Run directory:
<existing run directory>

Evolution directory:
<separate evolution directory>

Record supported experience and propose a scoped candidate if eligible.
Wait for my explicit decision before applying changes to the library.
```

Experience recording, candidate generation, validation, and application are separate actions. A complete natural `failure_pattern` can support a hypothesis candidate, but is not a verified repair; the candidate still requires matched validation.

## 12. Typical Run Directory

```text
<run-root>/
├── case_spec.json
├── workflow.json
├── case/
│   ├── 0/
│   ├── constant/
│   └── system/
├── runs/
│   └── <attempt_id>/
│       ├── run_record.json
│       └── *.stdout.log / *.stderr.log
├── evidence_summary.json
├── experiences/                 # only when Experience is retained
└── results/                     # requested tables, plots, exports, reports
```

Natural-language requirements do not need to be persisted as files. A user-provided TXT file is referenced in place and is not copied or modified.

## 13. Common Script Entrypoints

| Purpose | Command |
| --- | --- |
| Discover OpenFOAM | `python skills/_shared/scripts/openfoam_env.py discover` |
| Build CaseSpec from text | `python skills/workflow/plan/case-planning/scripts/build_case_spec.py --run-dir <dir> --case-id <id> --requirement-text "<text>"` |
| Build CaseSpec from TXT | `python skills/workflow/plan/case-planning/scripts/build_case_spec.py --run-dir <dir> --case-id <id> --requirement-file <file>` |
| Validate CaseSpec | `python skills/workflow/plan/case-planning/scripts/validate_case_spec.py <run-dir>/case_spec.json` |
| Manage Workflow | `python skills/workflow/scripts/workflow_ledger.py --help` |
| Execute an attempt | `python skills/workflow/run/runner/scripts/run_openfoam.py --help` |

CaseSpec validation exits with `0=passed`, `1=schema/semantic error`, and `2=user clarification required`.

## 14. Current Limitations

- Automated gates currently focus on single-region contracts; complex models still require specialist review.
- Complex geometry must not be replaced by a simple box; real CAD, surface, or mesh input is required.
- One mesh does not prove mesh independence.
- Solver completion does not prove convergence or physical credibility.
- QoI thresholds must not be invented when the user did not provide or approve them.
- Evolution validation and application do not replace human review.

## 15. License

Licensed under Apache License 2.0. OpenFOAM, ParaView, and other third-party software remain under their respective licenses. EasyFoam does not redistribute OpenFOAM itself.
