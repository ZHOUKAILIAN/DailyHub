# Morning Automation Requirements

## 1. 目标与背景

将每日晨间自动化任务沉淀为仓库内可迁移的标准化资产，确保在更换服务器或执行环境后可快速恢复，无需重复口头说明。

目标时段与任务：

1. `09:00` 小桔充电签到
2. `09:20` AI 日报主任务（`daily-news`）
3. `09:25` 前沿更新主任务（`frontier-changelog`）
4. `09:30` 合并发布主任务（`morning-publish`）

---

## 2. 范围

### In Scope

- 任务定义与执行策略文档化（含成功/失败处理）
- Skill 资产映射与创建：
  - 任务 1 复用现有小桔签到 skill
  - 任务 2/3/4 使用拆分后的三段式晨间 AI skill（日报、前沿追踪、合并发布）
  - `daily/skill` 作为外层编排入口，仅负责任务组合与失败策略
- 外部依赖资产记录：
  - 日报生成 skill（借用 OpenClaw asset）：`https://openclawmp.cc/asset/s-027065c89db7e63f`
  - 小红书发布 skill（借用 Agent-Reach OpenClaw skill，内含 MCP 能力）：`https://github.com/Panniantong/Agent-Reach`
- 迁移所需最小信息清单（时间点、输入、产出、失败策略）

### Out of Scope

- 本次不实现新的调度器代码（cron/系统服务配置）
- 本次不改造日报生产 skill 本身（沿用/借用既有 `daily-intelligence-news`：`https://openclawmp.cc/asset/s-027065c89db7e63f`）
- 本次不新增小红书发布实现（沿用/借用 Agent-Reach OpenClaw skill，内含 MCP 能力：`https://github.com/Panniantong/Agent-Reach`）

---

## 3. 功能需求

### FR-000: 职责边界（单一职责 + 外层组合）

- `daily/skill/SKILL.md` 仅负责编排（任务顺序、条件开关、失败策略、聚合输出）
- 顶层编排 skill 名称统一为 `morning-orchestrator`（避免过宽命名）
- 编排层权威任务清单文件统一为 `daily/skill/morning-task-schedule.md`
- `checkin/*` 与 `routine/*` 子 skill 仅负责自身任务执行，不承担跨时段编排
- `daily-news` 仅处理 `09:20` 日报内容生成
- `frontier-changelog` 仅处理 `09:25` IDE/CLI 与模型更新追踪
- `morning-publish` 仅处理 `09:30` 模板合并与分发

### FR-001: 09:00 小桔签到

- 自动执行：状态检查 + 签到 + 记录校验
- 成功：回执签到结果
- 失败：仅回执失败原因，等待人工决定后再排查

### FR-002: 09:20 AI 日报（daily-news）

- 调用既有 `daily-intelligence-news` skill 生成当日日报（借用资产：`https://openclawmp.cc/asset/s-027065c89db7e63f`）
- 仅输出 AI 日报主体内容，不合并 changelog 信息

### FR-003: 09:25 前沿更新（frontier-changelog）

- 独立追踪 IDE/CLI 与主流模型更新
- 仅保留“有实质内容”的条目
- 每个有效更新条目必须包含：总览 + 关键变更点与来源链接

### FR-004: 09:30 合并发布（morning-publish）

- 读取 `daily-news` 与 `frontier-changelog` 输出并按固定模板合并
- 写入 Blog 当日文件并发起 PR
- PR 仅包含日报单文件
- 同步向用户发送合并后的最终内容
- 同步发布到小红书（借用 Agent-Reach OpenClaw skill，内含 MCP 能力：`https://github.com/Panniantong/Agent-Reach`），仅要求接口调用发出，不做重试与回包校验

### FR-005: 分步汇报编排（Step-by-Step Reporting Orchestration）

- `daily/skill/SKILL.md` 禁止“等待全部子任务完成后统一回复”。
- 每个子任务执行周期必须固定为：启动子 Agent -> 等待完成 -> 立即向用户发送该步结果 -> 自动触发下一步。
- Step 1 结果消息末尾必须显式声明下一步：`接下来将开始执行 Step 2 (AI 日报)`。
- Step 2 完成后必须先发送 Step 2 结果消息，并声明将继续执行 Step 3 与 Step 4。
- Step 4 完成后必须先发送 Step 4 结果消息，再发送全局状态总结消息。
- 全局状态总结必须包含：整体成功/部分失败/失败状态、每步结果、异常建议动作。

## 4. 非功能需求

| NFR | 要求 |
|-----|------|
| NFR-001 可迁移性 | 更换服务器时，只需依赖仓库文档与 skill 即可恢复流程 |
| NFR-002 可观测性 | 每个时段任务均有结构化回执（成功/失败/摘要） |
| NFR-003 可维护性 | 外部依赖链接、用途、失败策略在仓库内有明确记录 |
| NFR-004 安全性 | 凭证/密钥不入库，仅记录命名规范与注入位置 |
| NFR-005 交互存活性 | 长任务执行期间必须在子任务粒度产生用户可见回执，避免超时无响应 |

---

## 5. 依赖资产

- 日报生成 skill（OpenClaw 资产）：
  `https://openclawmp.cc/asset/s-027065c89db7e63f`
- 小红书发布 skill（Agent-Reach OpenClaw skill，内含 MCP 能力）：
  `https://github.com/Panniantong/Agent-Reach`

---

## 6. 验收标准

1. 仓库内存在晨间任务总览文档，覆盖 09:00/09:20/09:25/09:30。
2. 任务 1 对应 skill 可追溯且已标注为现有资产。
3. 任务 2/3/4 skill 职责单一：`daily-news`、`frontier-changelog`、`morning-publish` 各自独立。
4. `daily` 编排 skill 已组合 09:00 -> 09:20 -> 09:25 -> 09:30，并定义失败不阻断策略。
5. 新/改 skill 通过 `skill-creator` 提供的基础校验。
6. Step 1 完成后存在独立汇报消息，且消息末尾包含“即将执行 Step 2”的声明。
7. Step 1 消息发送后无需人工确认，编排会自动推进到 Step 2。
8. Step 2 与 Step 4 完成后均存在独立汇报消息，且不与全局总结混为一条消息。
9. 全局总结消息紧随 Step 4 汇报之后，包含 overall 状态、分步结果、失败建议。

---

## 7. 验证步骤

1. 检查编排 skill 是否定义分步汇报与自动推进：
   - `rg -n "Sub-Agent Execution Model|After sub-agent completes|Step 1 Report|Step 2 Report|Final Global Summary" daily/skill/SKILL.md`
2. 检查需求与设计文档是否覆盖 FR-003：
   - `rg -n "FR-005|分步汇报|自动推进|三段式" docs/requirements/morning-automation-requirements.md docs/design/morning-automation-skill-design.md`
3. 运行现有 Python 测试回归：
   - `python3 -m unittest discover -s tests -q`

---

_Last updated: 2026-03-11_
