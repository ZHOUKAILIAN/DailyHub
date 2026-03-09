# DailyHub (For OpenClaw)

**DailyHub** 当前聚焦于一个能力：小桔充电每日签到自动化。  
目标是让 OpenClaw/Codex 直接理解并执行“签到”和“认证参数获取”这两条流程。

## 🎯 核心场景与功能 (Core Features)

- ✅ **当前已落地能力：小桔充电签到 (Xiaoju Charging Check-in)**
  内置幂等判断与签到记录复核，重点覆盖两件事：
  1) 如何执行签到
  2) 如何获取身份认证参数

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

- `checkin/xiaojuchongdian/skill/overall/*`
- `checkin/xiaojuchongdian/skill/checkin/*`
- `checkin/xiaojuchongdian/skill/get-params/*`

对应执行源码位于：

- `checkin/xiaojuchongdian/src/main.py`
- `checkin/xiaojuchongdian/src/router.py`
- `checkin/xiaojuchongdian/src/checkin_task.py`
- `checkin/xiaojuchongdian/src/checkin_workflow.yaml`

可作为 OpenClaw/Codex 的可读执行入口，直接复用 DailyHub 任务命令。

---

_Designed for OpenClaw - Automate Your Digital Life._
