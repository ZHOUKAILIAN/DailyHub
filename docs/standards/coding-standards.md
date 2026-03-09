# DailyHub - Coding Standards

## Language & Runtime

> 技术栈待确定。确认后更新此文档。

当前候选方案（按适合度排序）：
1. **Python** — 生态成熟，适合 API 集成和自动化脚本
2. **TypeScript/Node.js** — 若 OpenClaw 是 JS 生态则优先

---

## Python Standards (若采用 Python)

### 代码风格
- 遵循 PEP 8
- 使用 `black` 格式化，`ruff` 做 lint
- 类型注解：所有公开函数必须有类型标注

### 文件结构
```
<ability>/<app>/
├── skill/          # Skill 定义与说明
└── src/            # 该能力在该 app 下的实现源码

<ability>/<app>/src/
├── main.py          # 该 app 的 CLI 入口
├── router.py        # 该 app 的任务注册路由
├── task_base.py     # 该 app 的 Task 抽象
├── config.py        # 该 app 的配置管理
├── http.py          # HTTP 客户端封装
├── logger.py        # 日志工具
└── *_task.py        # 具体任务实现
```

### 命名规范
- 类名: `PascalCase` (e.g., `JdCheckInTask`)
- 函数/变量: `snake_case`
- 常量: `UPPER_SNAKE_CASE`
- 私有成员: `_leading_underscore`

### 错误处理
- 禁止空 `except` 块
- 所有异常必须记录日志
- 业务异常使用自定义异常类，不裸抛 `Exception`

### 日志规范
```python
import logging
logger = logging.getLogger(__name__)

# 格式: [时间] [级别] [模块] 消息
logger.info("JD check-in success: +10 points")
logger.error("JD check-in failed: %s", error_msg)
```

---

## General Rules (语言无关)

- **禁止硬编码**：平台 URL、API 路径放配置，不写死在逻辑代码里
- **单一职责**：每个 Task Module 只负责一个平台
- **幂等设计**：签到等任务重复执行不应产生副作用（平台已签到则视为成功）
- **超时配置**：所有 HTTP 请求必须设置超时，默认 30s

---

_Last updated: 2026-03-09_
