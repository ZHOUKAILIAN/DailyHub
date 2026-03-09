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

## MVP Implementation (Xiaoju Check-in)

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

该实现目标是为 OpenClaw 提供统一调用面，后续新平台复用同一 Task 接口。

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
