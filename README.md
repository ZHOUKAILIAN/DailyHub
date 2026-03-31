# DailyHub (For OpenClaw)

**DailyHub** 是专为 OpenClaw 设计的每日自动化任务中心。
通过一个统一入口（`daily/skill/SKILL.md`）注册定时任务，每个任务是一个独立的垂直 Skill。

## 设计核心

```text
daily/skill/SKILL.md          ← 唯一入口：cron 注册表（时间 + Skill Name + 目标）
     │
     ├── xiaoju-overall                ← 签到类 Skill（API 驱动）
     └── frontier-changelog            ← 更新汇总 Skill（Prompt 驱动）
```

- **入口只做一件事**：注册定时任务，不包含任何业务逻辑。
- **每个 Skill 自包含**：目标、可用工具、约束、成功标准全在一个 SKILL.md 里。
- **按 Skill Name 引用**：不依赖文件路径，OpenClaw 按名字查找安装。
- **新增任务只需两步**：建好 Skill → 在入口加一行。

## 已落地任务

| 时间  | Skill Name           | 目标                                    |
|-------|----------------------|-----------------------------------------|
| 09:00 | xiaoju-overall       | 完成小桔充电每日签到（幂等）             |
| 09:25 | frontier-changelog   | 汇总近 24h AI IDE/CLI 和模型的更新日志   |

## 两类驱动引擎

- **API 协议驱动**：签到、状态查询等固定流程 — 精确、幂等、可验证。
- **Prompt 提示词驱动**：更新汇总等灵活任务 — 自然语言描述，AI 自主执行。

## 🧩 Skill 清单

| Skill Name               | 类型         | 说明                                     |
|---------------------------|-------------|------------------------------------------|
| `morning-orchestrator`    | orchestration | 顶层 cron 注册表（`daily/skill/`）       |
| `xiaoju-overall`          | api-driven  | 小桔充电签到（含认证刷新依赖）            |
| `xiaoju-get-params`       | api-driven  | 短信验证码刷新小桔认证参数                |
| `frontier-changelog`      | prompt-driven | 前沿 IDE/CLI 和模型更新汇总              |
| `self-optimize`           | prompt-driven | Skill 生命周期管理（创建/优化）           |

---

_Designed for OpenClaw - Automate Your Digital Life._
