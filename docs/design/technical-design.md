# DailyHub - Technical Design

## Architecture Overview

DailyHub 采用双引擎架构，驱动 OpenClaw 执行数字生活自动化任务。

```
OpenClaw
    │
    ▼
DailyHub Task Router
    ├── API-Driven Engine    ──▶ HTTP/API Clients  ──▶ 各平台 API
    └── Prompt-Driven Engine ──▶ LLM Instructions ──▶ 自然语言执行
```

---

## Dual-Engine Design

### API-Driven Engine

**适用场景**: 固定流程、需精确执行的任务
- 多平台签到
- 账户余额/积分查询
- 短信退订

**设计原则**:
- 每个平台封装为独立 Task Module
- 统一的 Task 接口规范（见下方接口设计）
- HTTP 客户端复用，支持重试和超时配置

### Prompt-Driven Engine

**适用场景**: 非标准化、自然语言描述的任务
- 用自然语言描述复杂操作
- 需要 LLM 推理才能完成的任务

---

## Task Module Interface (草案)

每个平台 Task Module 应实现以下接口：

```python
class TaskModule:
    def execute(self) -> TaskResult:
        """执行主任务"""
        ...

    def check_status(self) -> StatusResult:
        """查询当前状态"""
        ...

class TaskResult:
    success: bool
    message: str
    data: dict | None
    timestamp: str
```

---

## API Integrations

详见 `docs/design/api-integrations.md`

---

## Skill Architecture

Skills 是 DailyHub 与 OpenClaw 之间的接口层，每个功能必须有对应 skill 才能被调用。

```
daily/skill/SKILL.md                              ← 顶层每日调度入口
     │
     ├── checkin/<platform>/skill/overall/         ← 平台级签到入口
     └── routine/<name>/skill/<task>/              ← 场景任务入口
```

**原则**: 编排 skill 只做链接和顺序控制，不包含实现逻辑。

### Skill Output Format (Case-Specific)

所有 skill 输出采用“人类可读优先”策略，但**不要求统一模板**。每个 skill 可按自身场景定义输出格式。

每个 skill 的 `Output Format` 至少要明确：

1. 如何表达任务成功/部分成功/失败。
2. 人类可读摘要要包含哪些关键信息。
3. 失败时如何给出原因与下一步建议。
4. 如需链路编排，可附加结构化 `details` 补充信息。

可选表达形式（按 skill 自行选择）：

- 短段落 + 关键要点列表
- 分段标题（Result / Summary / Key Details / Next Step）
- 表格化结果摘要

---

## Current Implementation (Xiaoju Check-in)

首个落地任务采用 Python 实现，目录结构遵循标准约定：

```
checkin/
└── xiaojuchongdian/
    ├── skill/
    │   ├── overall/{skill.json,SKILL.md}
    │   ├── checkin/{skill.json,SKILL.md}
    │   └── get-params/{skill.json,SKILL.md}
    └── src/
        ├── main.py
        ├── config.py
        ├── router.py
        ├── task_base.py
        ├── http.py
        ├── logger.py
        ├── checkin_task.py
        └── checkin_workflow.yaml
```

执行入口：

- `python3 -m checkin.xiaojuchongdian.src.main list`
- `python3 -m checkin.xiaojuchongdian.src.main status --task xiaoju.checkin`
- `python3 -m checkin.xiaojuchongdian.src.main run --task xiaoju.checkin --verify-record`

---

## Adding a New Platform

1. 创建 `checkin/<platform>/skill/overall/SKILL.md` — 定义调用入口
2. 创建 `checkin/<platform>/src/` — 实现 TaskModule 接口
3. 在 `daily/skill/morning-task-schedule.md` 添加行，并更新 `daily/skill/SKILL.md`
4. 在 `docs/requirements/` 和 `docs/design/` 补充文档

---

## Error Handling Strategy

| 错误类型 | 处理方式 |
|---------|---------|
| 网络超时 | 指数退避重试，最多 3 次 |
| 认证失败 (401/403) | 立即失败，触发告警 |
| 平台限流 (429) | 等待后重试，记录限流事件 |
| 平台维护 (5xx) | 记录，跳过当日任务 |
| 未知错误 | 记录完整错误信息，不静默失败 |

---

## Secrets Management

- API Token / Cookie 通过**环境变量**注入，不得硬编码
- 命名规范: `DAILYHUB_{PLATFORM}_{KEY_TYPE}`
  - 示例: `DAILYHUB_JD_COOKIE`, `DAILYHUB_ALIYUN_TOKEN`
- 本地开发使用 `.env` 文件（已加入 .gitignore）
- 生产环境使用 OpenClaw 的密钥管理机制

---

_Last updated: 2026-03-09_
