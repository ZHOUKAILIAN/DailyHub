# Morning Automation Requirements

## 1. 目标与背景

将每日晨间自动化任务沉淀为仓库内可迁移的标准化资产，确保在更换服务器或执行环境后可快速恢复，无需重复口头说明。

目标时段与任务：

1. `09:00` 小桔充电签到
2. `09:20` AI 日报主任务（合并前沿更新：IDE/CLI + 模型）

---

## 2. 范围

### In Scope

- 任务定义与执行策略文档化（含成功/失败处理）
- Skill 资产映射与创建：
  - 任务 1 复用现有小桔签到 skill
  - 任务 2 使用独立的 AI 日报 skill（内含前沿更新合并）
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
- `ai-daily-news-and-changelog` 仅处理 `09:20` 日报链路

### FR-001: 09:00 小桔签到

- 自动执行：状态检查 + 签到 + 记录校验
- 成功：回执签到结果
- 失败：仅回执失败原因，等待人工决定后再排查

### FR-002: 09:20 AI 日报（合并前沿更新）

- 调用既有 `daily-intelligence-news` skill 生成当日日报（借用资产：`https://openclawmp.cc/asset/s-027065c89db7e63f`）
- 日报内容必须包含“前沿 IDE/CLI 更新”模块（重点关注 Claude Code / Codex / Cursor / OpenCode）
- 日报内容必须包含“模型更新”模块（关注主流模型发布与能力变化）
- 对更新模块仅保留“有实质内容”的条目
- 每个有效更新条目必须包含：总览 + 关键变更点
- 写入 Blog 当日文件并发起 PR
- PR 仅包含日报单文件
- 同步向用户发送日报内容
- 同步发布到小红书（借用 Agent-Reach OpenClaw skill，内含 MCP 能力：`https://github.com/Panniantong/Agent-Reach`），失败自动重试 1 次

## 4. 非功能需求

| NFR | 要求 |
|-----|------|
| NFR-001 可迁移性 | 更换服务器时，只需依赖仓库文档与 skill 即可恢复流程 |
| NFR-002 可观测性 | 每个时段任务均有结构化回执（成功/失败/摘要） |
| NFR-003 可维护性 | 外部依赖链接、用途、失败策略在仓库内有明确记录 |
| NFR-004 安全性 | 凭证/密钥不入库，仅记录命名规范与注入位置 |

---

## 5. 依赖资产

- 日报生成 skill（OpenClaw 资产）：
  `https://openclawmp.cc/asset/s-027065c89db7e63f`
- 小红书发布 skill（Agent-Reach OpenClaw skill，内含 MCP 能力）：
  `https://github.com/Panniantong/Agent-Reach`

---

## 6. 验收标准

1. 仓库内存在晨间任务总览文档，覆盖 09:00/09:20。
2. 任务 1 对应 skill 可追溯且已标注为现有资产。
3. 任务 2 skill 职责单一：`ai-daily-news-and-changelog` 仅负责 09:20 日报链路。
4. `daily` 编排 skill 已组合 09:00 -> 09:20，并定义失败不阻断策略。
5. 新/改 skill 通过 `skill-creator` 提供的基础校验。

---

_Last updated: 2026-03-09_
