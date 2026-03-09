# DailyHub (For OpenClaw)

**DailyHub** 当前聚焦两类晨间能力：  
1) 小桔充电每日签到自动化  
2) AI 日报与 changelog 同步自动化  
目标是让 OpenClaw/Codex 直接理解并执行这些固定任务流程。

## 🎯 核心场景与功能 (Core Features)

- ✅ **当前已落地能力：小桔充电签到 (Xiaoju Charging Check-in)**
  内置幂等判断与签到记录复核，重点覆盖两件事：
  1. 如何执行签到
  2. 如何获取身份认证参数
- ✅ **当前已落地能力：晨间 AI 信息流任务**
  覆盖 `09:20` 日报主任务（内含更新同步）。

## 🧠 设计理念 (Philosophy)

- **API 协议驱动**：把签到链路固定为可重复、可验证、可维护的执行流程。
- **Skill 驱动**：把“签到执行”和“参数获取”拆成可读的技能文档，便于 AI Agent 维护。

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

- `daily/skill/*`（外层编排入口，仅组合子任务）
- `checkin/xiaojuchongdian/skill/overall/*`
- `checkin/xiaojuchongdian/skill/checkin/*`
- `checkin/xiaojuchongdian/skill/get-params/*`
- `routine/ai-morning/skill/ai-daily-news-and-changelog/*`

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

### ⏰ 09:20 AI 日报主任务

- **执行逻辑**：调用指定的 `daily-intelligence-news` skill 产出行业日报，并合并前沿 IDE/CLI 与模型更新。
- **流转链路**：
  1. 写入 Blog 的当日文件并提 PR（只提交日报单文件）。
  2. 同步将日报内容发送一份通知。
  3. 同步发布到小红书（借用 Agent-Reach OpenClaw skill，内含 MCP 能力；失败会自动重试一次）。
  4. 更新模块只保留“有实质内容”的条目，并输出总览 + 关键变更点。
- **关联依赖资产**：
  - 借用日报生成 Skill: [s-027065c89db7e63f](https://openclawmp.cc/asset/s-027065c89db7e63f)
  - 借用小红书分发 Skill（内含 MCP 能力）: [Agent-Reach](https://github.com/Panniantong/Agent-Reach)

---

_Designed for OpenClaw - Automate Your Digital Life._
