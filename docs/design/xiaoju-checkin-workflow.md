# Xiaoju Check-in Workflow Design

## 1. 设计目标

将“小桔充电每日签到”以 **API-Driven Task Module** 方式接入 DailyHub，满足：

- 可被 AI Agent 直接理解和调用
- 执行流程幂等、可重试、可观测
- 认证和平台参数与业务逻辑解耦

---

## 2. 模块边界

```
checkin/
└── xiaojuchongdian/
    ├── skill/
    │   ├── overall/{skill.json,SKILL.md}
    │   ├── checkin/{skill.json,SKILL.md}
    │   └── get-params/{skill.json,SKILL.md}
    └── src/
        ├── main.py              # CLI 入口（run/status/list）
        ├── config.py            # 环境变量加载
        ├── router.py            # 任务注册与分发
        ├── task_base.py         # Task 抽象接口 & TaskResult
        ├── http.py              # HTTP 请求+重试
        ├── logger.py            # 统一日志
        ├── checkin_task.py      # 小桔签到任务实现
        └── checkin_workflow.yaml
```

---

## 3. API 序列与数据流

### 3.1 主链路

1. `POST /am/marketing/api/member/charge/activity/sign/main`
2. 解析 `signInfo[*].signTaskDTO.signRecordDTOList`
3. 若已包含当天日期 -> `already_signed`
4. 否则提取 `excitationId`，调用：
   `POST /am/marketing/api/member/charge/activity/sign/doSign`
5. 再调一次 `sign/main` 复核

### 3.2 可选核验链路

- `POST /excitation/api/excitation/signRecord`
- 获取近 30 天签到记录，辅助审计和排障

---

## 4. Task 接口设计

```python
class TaskModule(Protocol):
    def execute(self, **kwargs) -> TaskResult: ...
    def check_status(self, **kwargs) -> TaskResult: ...
```

`TaskResult` 结构：

- `success: bool`
- `status: str` (`already_signed` | `signed` | `failed` | `status_ok`)
- `message: str`
- `data: dict`
- `timestamp: str`
- `platform: str`
- `task: str`

---

## 5. 幂等与重试策略

### 幂等规则

- 已签到视为成功，不触发 `doSign`
- 复查 `main` 成功即判定本次执行完成

### 重试规则（HTTP）

- 对网络异常、`429`、`5xx` 进行指数退避重试
- 默认重试次数：3
- 认证错误处理（两个触发时机）：
  - **启动时检测**：任一必需参数（`TICKET`/`TOKEN`/`TOKEN_ID`）缺失时，自动调用 `get-params` skill
  - **运行时检测**：遇到 `401/403` 或 `TICKET ERROR` 时，自动调用 `get-params` skill 刷新凭证
  - 仅在需要时才要求用户提供手机号和验证码
  - 完成后自动（重新）执行签到任务

---

## 6. 可读性与可维护性

为提升 Codex/LLM 可维护性，采用以下策略：

1. API 路径集中为常量，避免散落硬编码
2. 认证字段集中在 `checkin/xiaojuchongdian/src/config.py`，Task 不直接读环境变量
3. 每个流程步骤写清楚中间结果（`main_before`、`do_sign`、`main_after`）
4. 失败原因语义化（认证失败、业务失败、网络失败）
5. CLI 输出 JSON，便于机器消费

### 6.1 隔离运行时配置补载设计

问题背景：
- OpenClaw 的 isolated cron session 不保证继承登录 shell 中的环境变量
- 小桔签到任务过去直接依赖 `os.getenv` 读取 `DAILYHUB_XIAOJU_*`
- 一旦 cron session 没有这些变量，就会在 `status` 前置阶段直接抛出 `missing required env`

设计要求：
1. 配置模块在首次读取环境变量前，先执行一次轻量级 bootstrap
2. bootstrap 优先保留当前进程里已存在的显式环境变量
3. 若变量缺失，则从常见本地 `.env` 位置补齐默认值
4. `.env` 解析仅支持简单 `KEY=VALUE` / `export KEY=VALUE` 赋值格式，满足当前 DailyHub 配置源即可
5. 仅使用 `os.environ.setdefault(...)` 注入，避免覆盖调用方显式传入的值
6. bootstrap 应幂等，避免在单次进程中重复加载

候选 `.env` 路径：
- 当前工作目录 `.env`
- 仓库根目录 `.env`
- 仓库父目录 `.env`
- `/root/DailyHub/.env`
- `/root/.env`

预期收益：
- 手动运行与 cron 隔离运行共享同一配置源
- 失败模式从“隐式缺 env”收敛为“补载后仍缺 env”
- 降低 cron 因环境继承差异导致的伪故障

---

## 7. 调用建议

- 执行签到：`python3 -m checkin.xiaojuchongdian.src.main run --task xiaoju.checkin --verify-record`
- 排障查询：`python3 -m checkin.xiaojuchongdian.src.main status --task xiaoju.checkin`

---

_Last updated: 2026-03-09_
