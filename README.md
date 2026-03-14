# DailyHub (For OpenClaw)

**DailyHub** 是专为 OpenClaw 设计的每日自动化任务中心。
通过一个统一入口（`daily/skill/SKILL.md`）注册定时任务，每个任务是一个独立的垂直 Skill。

## 设计核心

```text
daily/skill/SKILL.md          ← 唯一入口：cron 注册表（只有时间 + Skill 路径）
     │
     ├── checkin/<platform>/skill/overall/SKILL.md   ← 每个签到平台的独立 Skill
     └── routine/<name>/skill/<task>/SKILL.md        ← 每个日常任务的独立 Skill
```

- **入口只做一件事**：注册定时任务，不包含任何业务逻辑。
- **每个任务自治**：执行逻辑、失败策略全部封装在对应 Skill 内。
- **新增任务只需两步**：建好垂直 Skill → 在入口加一行。

## 已落地任务

| 时间  | 任务                       | Skill 路径                                                       |
|-------|----------------------------|------------------------------------------------------------------|
| 09:00 | 小桔充电每日签到           | `checkin/xiaojuchongdian/skill/overall/SKILL.md`                |
| 09:20 | AI 行业日报生成            | `routine/ai-morning/skill/daily-news/SKILL.md`                  |
| 09:25 | 前沿 IDE/模型更新汇总      | `routine/ai-morning/skill/frontier-changelog/SKILL.md`          |
| 09:30 | 晨间日报发布               | `routine/ai-morning/skill/morning-publish/SKILL.md`             |

## 两类驱动引擎

- **API 协议驱动**：签到、状态查询等固定流程 — 精确、幂等、可验证。
- **Prompt 提示词驱动**：日报生成等灵活任务 — 自然语言描述，AI 自主执行。

## 🚀 快速开始 (Getting Started)

### 1) 环境准备

- Python 3.10+
- 安装依赖：

```bash
python3 -m pip install requests
```

### 2) 配置凭证

复制 `.env.example` 并注入你的小桔凭证（`ticket/token/token_id` 等）：

```bash
cp .env.example .env
```

然后用你的注入方式导出到环境变量（或由 OpenClaw 密钥管理注入）。

参数获取方法见：

- `checkin/xiaojuchongdian/skill/get-params/SKILL.md`

### 3) 任务发现

```bash
python3 -m checkin.xiaojuchongdian.src.main list
```

### 4) 查询小桔签到状态

```bash
python3 -m checkin.xiaojuchongdian.src.main status --task xiaoju.checkin
```

### 5) 执行小桔每日签到（幂等）

```bash
python3 -m checkin.xiaojuchongdian.src.main run --task xiaoju.checkin --verify-record
```

---

## 🧩 Skill 形式

仓库已提供按功能聚合的 Skill 形态封装（与 OpenClaw 资产风格对齐）：

- `daily/skill/*`（外层编排入口，仅 cron 注册表）
- `checkin/xiaojuchongdian/skill/overall/*`
- `checkin/xiaojuchongdian/skill/checkin/*`
- `checkin/xiaojuchongdian/skill/get-params/*`
- `routine/ai-morning/skill/daily-news/*`
- `routine/ai-morning/skill/frontier-changelog/*`
- `routine/ai-morning/skill/morning-publish/*`
- `routine/self-optimize/skill/*`

对应执行源码位于：

- `checkin/xiaojuchongdian/src/main.py`
- `checkin/xiaojuchongdian/src/router.py`
- `checkin/xiaojuchongdian/src/checkin_task.py`
- `checkin/xiaojuchongdian/src/checkin_workflow.yaml`

可作为 OpenClaw/Codex 的可读执行入口，直接复用 DailyHub 任务命令。

晨间任务迁移总览见：

- `docs/analysis/morning-routines-handover.md`

## 🤖 自动化日常任务规划 (Daily Automated Routines)

为了防范环境迁移导致记忆丢失，现将每日早晨由机器人自动执行的任务流与所用资产汇总如下：

### ⏰ 09:00 小桔充电签到

- **执行逻辑**：自动执行状态检查 + 签到 + 记录校验。
- **通知策略**：成功即回执结果；失败仅报原因，等待决定后再排查。

### ⏰ 09:20 AI 行业日报生成

- **执行逻辑**：调用 `daily-intelligence-news` skill 产出行业日报。
- **关联依赖资产**：借用日报生成 Skill: [s-027065c89db7e63f](https://openclawmp.cc/asset/s-027065c89db7e63f)

### ⏰ 09:25 前沿 IDE/模型更新汇总

- **执行逻辑**：抓取 Claude Code、Cursor、Windsurf 等前沿工具的更新日志，以及 Claude API、Gemini 等模型的变更记录。
- **输出策略**：只保留”有实质内容”的条目，并输出总览 + 关键变更点。

### ⏰ 09:30 晨间日报发布

- **执行逻辑**：统一编排日报和更新汇总的发布流程。
- **流转链路**：
  1. 写入 Blog 的当日文件并提 PR（只提交日报单文件）。
  2. 同步将日报内容发送一份通知。
  3. 同步发布到小红书（借用 Agent-Reach OpenClaw skill，内含 MCP 能力；失败会自动重试一次）。
- **关联依赖资产**：借用小红书分发 Skill（内含 MCP 能力）: [Agent-Reach](https://github.com/Panniantong/Agent-Reach)

---

_Designed for OpenClaw - Automate Your Digital Life._
