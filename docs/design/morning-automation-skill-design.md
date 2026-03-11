# Morning Automation Skill Design

## 1. 设计目标

以“文档可迁移 + skill 可执行”为核心，沉淀晨间自动化任务。

设计原则：

1. `09:00` 小桔签到复用现有实现，不重复建设。
2. 晨间 AI 链路采用拆分式执行：`09:20 daily-news`、`09:25 frontier-changelog`、`09:30 morning-publish`。
3. `daily/skill` 仅负责外层编排，不承载具体任务执行逻辑；编排 skill 名称为 `morning-orchestrator`。
4. 所有外部依赖（OpenClaw asset、Agent-Reach OpenClaw skill）在执行 skill 中显式声明用途与失败处理。
5. 长任务采用“分步执行、分步汇报、自动推进”模型，避免等待全量完成后一次性回复导致超时。

---

## 2. 技术边界

### 已有能力（复用）

- `daily/skill/SKILL.md`：晨间任务总编排入口（orchestration only, skill name=`morning-orchestrator`）
- `checkin/xiaojuchongdian/skill/overall`：小桔签到总入口
- `checkin/xiaojuchongdian/skill/checkin`：签到执行细节
- `checkin/xiaojuchongdian/skill/get-params`：凭证获取流程
- `routine/ai-morning/skill/daily-news`：09:20 日报链路
- `routine/ai-morning/skill/frontier-changelog`：09:25 前沿更新链路
- `routine/ai-morning/skill/morning-publish`：09:30 合并分发链路

### 职责边界（规范）

```
daily/skill/
├── SKILL.md                       # 仅编排：顺序、开关、失败策略、聚合输出
└── morning-task-schedule.md       # 权威任务表

checkin/xiaojuchongdian/skill/overall/
└── SKILL.md                       # 仅签到能力

routine/ai-morning/skill/daily-news/
└── SKILL.md                       # 仅 09:20 日报能力

routine/ai-morning/skill/frontier-changelog/
└── SKILL.md                       # 仅 09:25 前沿更新能力

routine/ai-morning/skill/morning-publish/
└── SKILL.md                       # 仅 09:30 合并分发能力
```

---

## 3. 编排流程

### 3.1 Daily 外层编排（09:00 -> 09:20 -> 09:25 -> 09:30，分步汇报）

执行周期固定为：`启动子 Agent -> 等待完成 -> 即时汇报 -> 自动推进`。

1. 启动 Step 1 子 Agent：调用 `xiaoju-overall`。
2. Step 1 完成后，立即发送独立消息 `Step 1 Report`：
   - 包含 Step 1 完整结果（成功/失败与关键细节）。
   - 消息末尾固定声明：`接下来将开始执行 Step 2 (AI 日报)`。
3. Step 1 消息发送后，无需人工确认，自动启动 Step 2 子 Agent。
4. 启动 Step 2 子 Agent：调用 `daily-news`。
5. Step 2 完成后，立即发送独立消息 `Step 2 Report`（包含完整结果）。
6. Step 2 汇报后，自动启动 Step 3 子 Agent：调用 `frontier-changelog`。
7. Step 3 完成后，立即发送独立消息 `Step 3 Report`（包含完整结果）。
8. Step 3 汇报后，自动启动 Step 4 子 Agent：调用 `morning-publish`。
9. Step 4 完成后，立即发送独立消息 `Step 4 Report`（包含完整结果）。
10. Step 4 汇报后，立即发送 `Final Global Summary`：
   - overall 状态（`SUCCESS` / `PARTIAL` / `FAILED`）
   - Step 1 至 Step 4 的结果归纳
   - 失败或异常时的建议动作

### 3.2 09:20~09:30 晨间 AI 子链路

1. `daily-news` 调用外部日报 skill：`daily-intelligence-news`（借用 OpenClaw asset：`https://openclawmp.cc/asset/s-027065c89db7e63f`）。
2. `frontier-changelog` 独立拉取 IDE/CLI 与模型更新，仅保留实质更新项。
3. `morning-publish` 合并前两步输出，写入 Blog 当日文件并发起 PR（仅日报单文件）。
4. `morning-publish` 通过 Agent-Reach OpenClaw skill 发布到小红书（该 skill 内含 MCP 能力，借用链路：`https://github.com/Panniantong/Agent-Reach`）。
5. 小红书仅要求接口调用发出即完成，不做重试与返回内容校验。

## 4. 失败处理策略

| 层级 | 场景 | 策略 |
|------|------|------|
| daily 编排层 | `09:00` 签到失败 | 记录失败并继续后续步骤 |
| daily 编排层 | Step 汇报消息发送失败 | 立即重试 1 次；若仍失败，在全局总结中标记 `report_send_failed` 并继续流程 |
| daily-news 执行层 | 日报生成失败 | 直接返回失败原因，不进入后续分发 |
| frontier-changelog 执行层 | IDE/CLI 或模型更新拉取失败 | 返回来源维度失败信息，不伪造“无更新” |
| frontier-changelog 执行层 | 无有效前沿更新 | 返回“本轮无实质更新” |
| morning-publish 执行层 | Blog 提交/PR 失败 | 返回失败原因，保留已生成内容以便人工处理 |
| morning-publish 执行层 | 小红书接口调用 | 仅发起请求，不做重试与回包语义校验 |

---

## 5. 输出约定

### 5.1 daily 编排 skill 输出

daily 编排输出不是单条消息，而是固定五段消息序列：

1. `Step 1 Report`（小桔签到结果 + 下一步声明）
2. `Step 2 Report`（AI 日报结果）
3. `Step 3 Report`（前沿更新结果）
4. `Step 4 Report`（合并分发结果）
5. `Final Global Summary`（总体状态 + 分步状态 + 建议动作）

推荐在全局总结中保留结构化字段：

- `success`
- `status`（`completed` / `partial_failed` / `failed`）
- `message`
- `data.step1`
- `data.step2`
- `data.report_delivery`（记录步骤汇报消息是否发送成功）

### 5.2 拆分子 skill 输出

- `daily-news`: `success/status/message/data.news_report`
- `frontier-changelog`: `success/status/message/data.frontier_updates`
- `morning-publish`: `success/status/message/data.blog_pr/data.xiaohongshu_publish`

---

## 6. 迁移策略

在新服务器迁移时，按以下最小集合恢复：

1. 仓库文档（requirements/design/summary）
2. `daily/skill` 编排目录
3. `checkin/xiaojuchongdian/skill/overall` 目录
4. `routine/ai-morning/skill/daily-news` 目录
5. `routine/ai-morning/skill/frontier-changelog` 目录
6. `routine/ai-morning/skill/morning-publish` 目录
7. 外部依赖可用性检查：OpenClaw asset、Agent-Reach OpenClaw skill（含 MCP）
8. 调度器按固定时点绑定对应 skill（`09:00`、`09:20`、`09:25`、`09:30`）

---

_Last updated: 2026-03-11_
