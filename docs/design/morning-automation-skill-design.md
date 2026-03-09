# Morning Automation Skill Design

## 1. 设计目标

以“文档可迁移 + skill 可执行”为核心，沉淀晨间自动化任务。

设计原则：

1. `09:00` 小桔签到复用现有实现，不重复建设。
2. `09:20` 日报主任务内合并“前沿 IDE/CLI + 模型更新”内容，降低迁移复杂度。
3. `daily/skill` 仅负责外层编排，不承载具体任务执行逻辑；编排 skill 名称为 `morning-orchestrator`。
4. 所有外部依赖（OpenClaw asset、Agent-Reach OpenClaw skill）在执行 skill 中显式声明用途与失败处理。

---

## 2. 技术边界

### 已有能力（复用）

- `daily/skill/SKILL.md`：晨间任务总编排入口（orchestration only, skill name=`morning-orchestrator`）
- `checkin/xiaojuchongdian/skill/overall`：小桔签到总入口
- `checkin/xiaojuchongdian/skill/checkin`：签到执行细节
- `checkin/xiaojuchongdian/skill/get-params`：凭证获取流程
- `routine/ai-morning/skill/ai-daily-news-and-changelog`：09:20 日报链路

### 职责边界（规范）

```
daily/skill/
├── SKILL.md                       # 仅编排：顺序、开关、失败策略、聚合输出
└── morning-task-schedule.md       # 权威任务表

checkin/xiaojuchongdian/skill/overall/
└── SKILL.md                       # 仅签到能力

routine/ai-morning/skill/ai-daily-news-and-changelog/
└── SKILL.md                       # 仅 09:20 日报能力
```

---

## 3. 编排流程

### 3.1 Daily 外层编排（09:00 -> 09:20）

1. `09:00` 调用 `xiaoju-overall`，拿到 `checkin_result`。
2. `09:20` 调用 `ai-daily-news-and-changelog`。
3. 返回聚合结果：`checkin`、`daily_report`。

### 3.2 09:20 日报主任务（ai-daily 子 skill 内部流程）

1. 调用外部日报 skill：`daily-intelligence-news`（借用 OpenClaw asset：`https://openclawmp.cc/asset/s-027065c89db7e63f`）。
2. 拉取前沿 IDE/CLI 更新（Claude Code / Codex / Cursor / OpenCode）。
3. 拉取模型更新（主流模型发布、能力与价格/上下文变化等）。
4. 将“日报主体 + IDE/CLI 更新 + 模型更新”合并为当日单篇内容，仅保留有实质信息的更新项。
5. 写入 Blog 当日文件，发起 PR（仅日报单文件）。
6. 同步发送日报内容给用户。
7. 通过 Agent-Reach OpenClaw skill 发布到小红书（该 skill 内含 MCP 能力，借用链路：`https://github.com/Panniantong/Agent-Reach`）。
8. 发布失败时自动重试 1 次；二次失败则返回失败原因。

## 4. 失败处理策略

| 层级 | 场景 | 策略 |
|------|------|------|
| daily 编排层 | `09:00` 签到失败 | 记录失败并继续后续步骤 |
| ai-daily 执行层 | 日报生成失败 | 直接返回失败原因，不进入后续分发 |
| ai-daily 执行层 | Blog 提交/PR 失败 | 返回失败原因，保留已生成内容以便人工处理 |
| ai-daily 执行层 | 小红书发布失败 | 自动重试 1 次；仍失败则报告原因 |
| ai-daily 执行层 | IDE/CLI 或模型更新拉取失败 | 返回来源维度失败信息，不伪造“无更新” |
| ai-daily 执行层 | 无有效前沿更新 | 返回“本轮无实质更新”，但保留日报主体输出 |

---

## 5. 输出约定

### 5.1 daily 编排 skill 输出

- `success`
- `status`（`completed` / `partial_failed` / `failed`）
- `message`
- `data.checkin`
- `data.daily_report`

### 5.2 ai-daily 子 skill 输出

- `success`
- `status`（`completed` / `partial_failed` / `failed` / `no_updates`）
- `message`
- `data.news_report`（日报摘要与文件信息）
- `data.blog_pr`（PR 链接或失败原因）
- `data.xiaohongshu_publish`（发布状态与重试结果）
- `data.frontier_updates.ide_cli`（按产品聚合的总览与关键变更）
- `data.frontier_updates.models`（按模型聚合的总览与关键变更）

---

## 6. 迁移策略

在新服务器迁移时，按以下最小集合恢复：

1. 仓库文档（requirements/design/summary）
2. `daily/skill` 编排目录
3. `checkin/xiaojuchongdian/skill/overall` 目录
4. `routine/ai-morning/skill/ai-daily-news-and-changelog` 目录
5. 外部依赖可用性检查：OpenClaw asset、Agent-Reach OpenClaw skill（含 MCP）
6. 调度器按固定时点绑定对应 skill（`09:00`、`09:20`）

---

_Last updated: 2026-03-09_
