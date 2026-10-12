# EasyFoam

[English README](README.md) | [论文初稿（PDF）](docs/EasyFoam-draft.pdf) | [项目网站](https://cas-clab.github.io/EasyFoam/index_zh.html)

EasyFoam 是一个面向 **OpenFOAM Foundation v13** 的、基于 Skills、固定数据契约和证据链组织的 CFD 工作流库。它用于指导具备文件与命令执行能力的 Coding Agent 构建、恢复、运行、修复、验证和后处理 OpenFOAM case，并在用户明确要求时将经过验证的经验转化为可审核、可回滚的 Skill 更新。

> EasyFoam 不是新的 CFD 求解器，也不是单体的一键式 CLI。OpenFOAM 负责数值求解；EasyFoam 负责把用户需求、CaseSpec、case 文件、运行尝试、验证证据和可复用修复组织成可追踪的工程流程。

> **项目状态：工程研究版本。** 当前正式合同主要覆盖 OpenFOAM Foundation v13 单区域工作流。用于生产设计、认证、安全关键分析或高成本工程决策前，仍应由具备相应资质的 CFD 工程师审核网格、模型、数值方法和证据结论。

## 论文

配套论文 **EasyFoam: Skill-Oriented OpenFOAM Agents with Evidence-Driven Evolution**
可通过[论文初稿（PDF）](docs/EasyFoam-draft.pdf)阅读。
本仓库发布可使用的 EasyFoam 库，包括 Workflow、人工审核的 Evolution、Reference、
确定性脚本和对应 Schema。

## 1. 核心特点

- **完整 Workflow Loop**：`Plan → Write → Run → Postprocess`。
- **人工治理的 Evolution Loop**：`Experience → Candidate → Validation → Human Decision → Apply / Defer / Reject / Rollback`。
- **需求驱动的 CaseSpec**：CaseSpec 只能来源于当前自然语言需求或用户提供的 TXT 文件地址。
- **决定性信息不猜测**：缺失或矛盾的信息保持为 blocking review item，并由 Agent 向用户提出具体问题；用户补充后继续完善同一 CaseSpec。
- **OpenFOAM v13 明确契约**：覆盖 solver module、fields、dictionaries、mesh、run controls、QoIs 和 postprocessing。
- **分层证据声明**：文件正确、mesh 合同、执行成功、数值可信、物理可信和 QoI 验证分别判断。
- **可恢复状态**：`workflow.json` 记录最小权威状态；`advance` 原子完成并路由阶段，`reopen` 使最早受影响阶段及其下游结论失效。
- **最小加载原则**：一次只加载一个活动阶段、一个活动专家 Skill 和当前决策所需的最少 Reference。
- **可回滚进化**：冻结 patch、分级验证、人工授权、保留检查和 rollback 相互分离。

## 2. 支持范围

当前版本正式面向：

- OpenFOAM Foundation v13；
- 单区域 CFD 工作流；
- Windows 主机通过 WSL 执行 OpenFOAM；
- Linux 或 WSL 会话中原生执行 OpenFOAM；
- 生成、导入或复用 mesh，并显式维护 patch、zone、interface 和质量合同；
- Agent 协调的 case 构建、运行、诊断、验证、可视化和恢复；
- 对 Skill、Reference、脚本和 Schema 进行证据关联、人工治理和可回滚的修改。

## 3. 总体架构

```text
用户请求
├── Workflow
│   └── Plan → Write → Run → Postprocess
├── Evolution
│   └── Experience → Candidate → Review and Validation
│       → Human Decision → Apply / Defer / Reject / Rollback
└── Reference
    └── 只读 OpenFOAM、CFD、教程模式与治理知识
```

| 层级 | 主要职责 | 是否可以修改正式 Skill |
| --- | --- | --- |
| Workflow | 完成、恢复、修复、运行和验证当前 CFD 任务，并被动记录 Experience | 不可以 |
| Evolution | 将已验证 Experience 转化为经过审核、可回滚的库更新 | 仅在用户明确授权后可以 |
| Reference | 提供只读 OpenFOAM、CFD、教程模式和治理知识 | 不可以 |

根路由位于 `skills/SKILL.md`，详细意图与状态路由位于 `skills/ROUTING.md`。

## 4. Skill 加载原则

Agent 应从仓库根目录启动，并首先读取：

```text
skills/SKILL.md
```

随后根据 `skills/ROUTING.md`：

1. 绑定用户指定的最小目标；
2. 选择 Workflow、Evolution 或 Reference；
3. 加载一个活动阶段 Skill；
4. 加载一个活动专家 Skill；
5. 只读取当前决策需要的 Reference；
6. 仅在明确 handoff 时加载第二个专家。

不要预加载完整 Skill 树、全部 Reference、全部历史运行或全部 Experience。

## 5. Workflow Loop

### 5.1 Plan

Plan 将用户需求转换为可审计的 `case_spec.json`。需求可以来自：

- 当前对话中的自然语言 CFD 要求；
- 用户明确提供的 TXT 文件地址。

不要求在运行目录中复制或绑定 `user_requirement.txt`。

Plan 负责确认或阻塞：

- 物理问题、相态、可压缩性和稳态/瞬态形式；
- 湍流、能量、组分、反应、旋转和其他物理模型；
- solver module、legacy mapping 和 SIMPLE/PISO/PIMPLE 算法；
- 几何来源、mesh route、维度、patch、zone 和 interface；
- fields、边界条件、材料参数和运行控制；
- 用户要求的 QoI、可视化、输出和验收边界。

当决定性信息不明确时，Plan 保留 Schema 合法但未发布的 CaseSpec，并将相关项写为 open blocking review item。Agent 应合并相关问题，只向用户询问必须由用户权威决定或提供的信息。用户补充后，Agent 更新同一 CaseSpec、记录 resolution，并重新执行 Schema 与语义发布检查。只有全部 blocking items 关闭后才可进入 Write。

### 5.2 Write

Write 将通过 Schema 和语义发布门槛的 CaseSpec 落实为正式 `case/`：

- `mesh-generation`：适用于 `blockMesh`、`snappyHexMesh` 或组合路线；
- `mesh-import`：适用于外部 mesh、converter 或已有 `polyMesh`；
- `case-authoring`：编写和审核 fields、models、dictionaries、numerics 和 controls。

外部 mesh 必须提供实际源文件、格式和可执行转换命令；`<converter>` 一类占位符不能进入正式命令链。

Write 在更新 `workflow.json` 前重新执行 CaseSpec 语义发布检查，并记录正式 case、mesh、输入和初始状态哈希。

### 5.3 Run

Run 支持四种 attempt mode：

| 模式 | 用途 | 是否可以完成正式 Run |
| --- | --- | --- |
| `formal` | 执行正式生产命令链 | 可以 |
| `resume` | 从经过验证的 restart state 继续 | 可以 |
| `smoke` | 有限范围诊断 | 不可以 |
| `diagnostic` | 定位具体失败或环境问题 | 不可以 |

每次实际执行生成不可变目录：

```text
runs/<attempt_id>/
├── run_record.json
├── 01-<command>.stdout.log
├── 01-<command>.stderr.log
└── ...
```

失败后由 `debug-reviewer` 判断最早受影响阶段。正式 case 或 mesh 修复通过 ledger `reopen` 返回 Write；需求变化返回 Plan；仅调用、环境或 restart 修正保留在 Run。旧 run record 保留用于审计，但失效阶段的旧 decisive evidence 不再支持当前结论。

### 5.4 Postprocess

Postprocess 负责：

- residual、runtime、mesh、probe、force 和 field 数据提取；
- 派生量、表格、导出和 workflow report；
- ParaView contour、slice、vector、streamline、isosurface 和 animation；
- requirement、mesh、numerical、physical、conservation、boundedness 和 QoI 评估。

只有 `physics-validation` 可以写入 `evidence_summary.json`。求解器完成不等于数值或物理可信；可视化也不能替代守恒和定量验证。

## 6. Evolution Loop

Evolution 只在用户明确要求时启动：

```text
已验证的 Workflow 证据
→ Experience
→ Candidate
→ Validation
→ 人工决策
→ Apply / Apply Limited / Reject / Defer / Revise
→ Retention 或 Rollback
```

### Experience

经过验证且具有独立复用价值的修复、成功模式、证据完整的自然失败假设或未解决失败可以记录为 `experience_record.json`。成功或已验证经验需要显式的执行、数值、物理和 QoI 证据；未解决失败不能作为 Candidate 输入。Experience 保留来源 Workflow、证据、因果上下文、适用范围、排除条件和 Candidate 资格判断。

### Candidate

相互兼容的 Experience 可以被提炼成冻结的 `candidate_patch.json` 与 patch 文件。Candidate 必须保持原子范围，不能嵌入 case identity、私有机器路径、一次性数值或几何专用假设。

### Validation、Promotion 与 Rollback

Candidate replay、source-case、holdout、negative-control 和 cross-scope validation 与应用授权相互分离。应用、限制应用、保留和回滚都需要明确人工指令。`apply_candidate.py` 使用 `--validation-argv-json` 或 `--validation-command` 记录实际 post-apply validation；不会自动 commit、merge 或 push。

## 7. Reference 层

| 区域 | 内容 |
| --- | --- |
| `skills/reference/openfoam13/` | 版本规则、澄清策略、solver/module mapping、一致性审核和复杂几何策略 |
| `skills/reference/solver_modules/` | field family、algorithm、dictionary 要求和 module compatibility |
| `skills/reference/tutorial_families/` | 主要 CFD family 的可复用结构模式 |
| `skills/reference/tutorial_patterns/` | 本地教程索引与 module-to-family mapping |
| `skills/reference/evolution/` | Experience、Candidate、validation、promotion、retention 和 rollback policy |
| 各专家 `references/` | mesh、boundary、dictionary、runtime、diagnostic、QoI、postprocessing 和 visualization 规则 |

Reference 是证据来源，不是自动答案。用户明确需求和实际 case 证据始终具有更高优先级。

## 8. Canonical Artifacts

| Artifact | Schema 版本 | 所有者 | 作用 |
| --- | ---: | --- | --- |
| `case_spec.json` | 1.2 | Plan / case-planning | 需求来源、仿真合同、provenance 和 review items |
| `workflow.json` | 2.2 | Workflow ledger | 阶段、Artifact、stage-scoped evidence、阻塞项与下一步 |
| `runs/<attempt_id>/run_record.json` | 1.1 | Run / runner | 不可变环境、命令、终止、哈希和 restart 证据 |
| `evidence_summary.json` | 2.1 | Postprocess / physics-validation | 最终有边界的评估与最高可支持声明 |
| `experience_record.json` | 2.1 | Evolution / case-specific-fix | 已验证可复用行为或未解决失败 |
| `candidate_patch.json` | 2.1 | Evolution / candidate-patch | 冻结修改方案及验证状态 |
| `promotion_record.json` | 2.1 | Evolution / promoted-skill | 人工决策、应用、保留、限制和回滚 |

## 9. 仓库结构

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

Skill 保存职责、边界和 Decision Procedure；相邻 `references/` 保存可复用知识；`scripts/` 负责确定性解析、校验、哈希、状态更新和命令执行。

## 10. 环境要求

### Python

- Python 3.11 或 3.12；
- `jsonschema`；
- 可视化文件校验可选使用 Pillow，按需安装 `requirements-visual.txt`；
- Candidate 构建、验证、应用与回滚需要 Git；
- 需要具备文件和命令执行能力的 Coding Agent 来协调 Skills；模型和凭证在所选 Agent 运行环境中配置。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### OpenFOAM v13

设置 OpenFOAM 环境脚本在目标 shell 中的路径：

```bash
export EASYFOAM_OPENFOAM_BASHRC=/opt/openfoam13/etc/bashrc
```

可选执行后端：

```bash
export EASYFOAM_EXEC_BACKEND=auto     # 默认
# auto: Windows 主机使用 wsl；Linux/WSL 会话使用 native
# 也可显式设为 wsl 或 native
```

检查环境：

```bash
python skills/_shared/scripts/openfoam_env.py discover
```

成功结果应显示：

- `backend` 为 `wsl` 或 `native`；
- OpenFOAM 版本为 `13`；
- `foamRun`、`blockMesh` 和 `checkMesh` 可用；
- `foamPostProcess` 路径会同时报告，供后处理使用。

此处要求 Foundation 发行版；OpenCFD 发行版需要单独适配。并行执行需要 MPI；按需生成可视化时需要 ParaView `pvpython`。`.env.example` 提供 OpenFOAM 环境变量示例，请在 Agent 使用的 shell 中设置。

Windows 中应从 Windows Python/Agent 启动，并确保 WSL 内已安装 OpenFOAM v13。Linux 或 WSL 内部直接使用 native backend。

## 11. 快速开始

### 新建 Case

在仓库根目录启动 Agent，并发送：

```text
使用 EasyFoam Skills 完成以下 OpenFOAM v13 任务。

CFD 任务：
<用户需求>

运行目录固定为：
<运行目录>
```

或者使用 TXT 需求文件：

```text
使用 EasyFoam Skills 完成以下 TXT 文件描述的 OpenFOAM v13 任务。

CFD 需求文件：
<TXT 文件地址>

运行目录固定为：
<运行目录>
```

Skill 已经约定阶段顺序、证据保留、正式控制不缩短、决定性信息不猜测和 Evolution 不自动启动，因此无需把这些要求重复写入 Prompt。

### 恢复任务

```text
使用 EasyFoam Skills 恢复以下 OpenFOAM v13 任务。

运行目录固定为：
<已有运行目录>
```

Agent 应读取 `workflow.json` 和当前 Canonical Artifacts，从最早的不完整或失效阶段继续。

### Evolution

```text
使用 EasyFoam Skills 审阅以下已完成任务中的可复用经验。

运行目录：
<已有运行目录>

Evolution 目录：
<独立的进化目录>

记录证据支持的 Experience；符合资格时提出范围明确的 Candidate。
应用库修改前等待我的明确决策。
```

记录经验、构建候选、验证和应用是不同操作。证据完整的自然失败可以记录为
`failure_pattern`，用于提出待验证假设，但不代表修复已被验证；候选仍需成对验证。

## 12. 典型运行目录

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
├── experiences/                 # 仅在保留 Experience 时
└── results/                     # 用户请求的表格、图片、导出和报告
```

自然语言需求不需要保存为文件。用户提供 TXT 时，CaseSpec 仅引用原文件，不复制或修改它。Canonical Artifact 应尽可能使用相对路径或稳定逻辑标识。

## 13. 常用脚本入口

普通用户通常不需要手工串联全部脚本；Agent 应根据活动 Skill 调用相邻工具。

| 用途 | 命令 |
| --- | --- |
| 检查 OpenFOAM 环境 | `python skills/_shared/scripts/openfoam_env.py discover` |
| 构建自然语言 CaseSpec | `python skills/workflow/plan/case-planning/scripts/build_case_spec.py --run-dir <dir> --case-id <id> --requirement-text "<text>"` |
| 构建 TXT CaseSpec | `python skills/workflow/plan/case-planning/scripts/build_case_spec.py --run-dir <dir> --case-id <id> --requirement-file <file>` |
| 校验 CaseSpec | `python skills/workflow/plan/case-planning/scripts/validate_case_spec.py <run-dir>/case_spec.json` |
| 管理 Workflow | `python skills/workflow/scripts/workflow_ledger.py --help` |
| 执行 attempt | `python skills/workflow/run/runner/scripts/run_openfoam.py --help` |

`validate_case_spec.py` 返回：`0=passed`、`1=Schema/语义错误`、`2=需要用户补充的阻塞项`。

## 14. 当前限制

- 当前自动门槛以单区域合同为主；复杂模型仍需要专家审核。
- 复杂几何不应由 Agent 用简单盒体替代；必须提供真实 CAD、surface 或 mesh。
- 一个 mesh 不能证明 mesh independence。
- solver 运行完成不能证明数值收敛或物理可信。
- 没有明确验收标准时，不应虚构 QoI 阈值。
- Evolution 的验证和应用不能替代人工审阅。

## 15. License

本项目采用 Apache License 2.0。OpenFOAM、ParaView 及其他第三方软件遵循各自许可证；EasyFoam 不包含或重新分发 OpenFOAM 本体。
