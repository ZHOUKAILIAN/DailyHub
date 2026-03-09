# DailyHub - Project Conventions

## Task Module Convention

每个平台集成遵循统一的 Task Module 约定：

### 目录命名
- 采用三层结构：
  - 第一层：能力域（如 `checkin/`）
  - 第二层：App 平台（如 `xiaojuchongdian/`）
  - 第三层：能力内资源（`skill/` 与 `src/`）
- 推荐示例：
```
checkin/
└── xiaojuchongdian/
    ├── skill/
    │   ├── overall/
    │   ├── checkin/
    │   └── get-params/
    └── src/
        ├── main.py
        └── checkin_task.py
```

### Task 分类标记
每个 Task Module 必须声明其类型：
```python
TASK_TYPE = "api-driven"   # 或 "prompt-driven"
PLATFORM = "jd"
DESCRIPTION = "京东每日签到"
```

---

## Git Convention

### Branch Strategy
- `main` — 稳定版本
- `feat/{platform}-{feature}` — 新平台/功能开发
- `fix/{issue}` — Bug 修复

### Commit Message Format
```
<type>(<scope>): <subject>

<body>  # 可选，说明 why

See: docs/design/...  # 关联文档
```

**Type**:
- `feat` — 新功能
- `fix` — Bug 修复
- `docs` — 仅文档变更
- `refactor` — 重构
- `chore` — 构建/工具变更

**示例**:
```
feat(jd): add daily check-in task

Automates JD daily sign-in to collect beans.

See: docs/design/api-integrations.md#京东
```

---

## Documentation Convention

### 文档更新时机
- 新增平台 → 更新 `docs/design/api-integrations.md`
- 新增功能 → 更新 `docs/requirements/project-requirements.md`
- 设计变更 → 更新 `docs/design/technical-design.md`
- 规范调整 → 更新 `docs/standards/`

### 文档末尾必须有
```markdown
_Last updated: YYYY-MM-DD_
```

---

## Environment Variables Convention

命名规则: `DAILYHUB_{PLATFORM}_{KEY}`

| 变量名 | 说明 |
|--------|------|
| `DAILYHUB_JD_COOKIE` | 京东 Cookie |
| `DAILYHUB_ALIYUN_TOKEN` | 阿里云盘 Token |
| `DAILYHUB_XIAOJU_TICKET` | 小桔充电 Ticket |
| `DAILYHUB_XIAOJU_TOKEN` | 小桔充电 Token |
| `DAILYHUB_XIAOJU_TOKEN_ID` | 小桔充电 TokenId |
| `DAILYHUB_LOG_LEVEL` | 日志级别，默认 INFO |

---

_Last updated: 2026-03-09_
