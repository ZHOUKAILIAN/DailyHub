# Xiaoju Charging Daily Check-in Requirements

## 1. 目标与背景

在 DailyHub 中落地首个可运行的平台自动化任务：**小桔充电每日签到**。  
该任务用于给 OpenClaw/Codex Agent 提供一个稳定、幂等、可维护的 API 驱动执行流程。

核心目标：

1. 每日自动触发签到
2. 已签到场景幂等返回，不重复执行
3. 结果结构化输出，便于后续自动消费和审计

---

## 2. 范围

### In Scope

- 小桔充电签到主链路 API 编排：
  - `sign/main`（查询签到状态）
  - `sign/doSign`（执行签到）
  - `signRecord`（可选历史核验）
- DailyHub 内任务注册、执行路由、CLI 触发入口
- 环境变量注入认证信息（不落库、不硬编码）
- 清晰的成功判定与失败分类

### Out of Scope

- 登录态自动获取（本期由调用方提供 token/ticket/header）
- WebView/抓包链路自动化
- 多账号批量执行

---

## 3. 触发方式

- 手动触发：`python3 -m checkin.xiaojuchongdian.src.main run --task xiaoju.checkin`
- 外部调用：由上层系统按需调用 CLI 或 API

---

## 4. 执行流程（必须遵循）

1. 调用 `sign/main` 获取当日状态和 `excitationId`
2. 若已签到：直接返回 `already_signed`
3. 若未签到：调用 `sign/doSign(excitationId)`
4. 再次调用 `sign/main` 复核是否已签到
5. 可选调用 `signRecord` 做近 30 天核验

---

## 5. 认证与配置要求

凭证由调用方注入，代码仅负责读取并校验完整性：

- `DAILYHUB_XIAOJU_TICKET`
- `DAILYHUB_XIAOJU_TOKEN`
- `DAILYHUB_XIAOJU_TOKEN_ID`
- `DAILYHUB_XIAOJU_APP_ID`
- `DAILYHUB_XIAOJU_AM_CHANNEL`
- `DAILYHUB_XIAOJU_SOURCE`
- `DAILYHUB_XIAOJU_TTID`

### 认证失败自愈策略

自动恢复机制覆盖两个场景：

**场景 1: 启动时凭证缺失**
- 检测到任一必需参数缺失（`DAILYHUB_XIAOJU_TICKET`、`DAILYHUB_XIAOJU_TOKEN`、`DAILYHUB_XIAOJU_TOKEN_ID`）
- 自动调用 `get-params` skill 启动 SMS 登录流程
- 仅在 SMS 登录流程明确需要时才询问用户提供手机号和验证码

**场景 2: 运行时认证失败**
- 检测到认证失败（`401/403` 或 `TICKET ERROR`）
- 自动调用 `get-params` skill 刷新凭证
- 完成后自动重试签到任务

**核心原则**:
- 无需预询问用户"是否提供凭证"或"是否使用 API 刷新"
- 默认自动执行恢复流程
- 用户交互仅限于 SMS 验证码输入环节
- 在向用户索取 SMS 验证码前，必须已经实际触发验证码发送并确认发送接口成功；禁止在未发码时要求用户提供验证码
- 凭证刷新后，必须写入后续签到任务实际读取的配置源，并使用同一配置源完成状态校验

可选运行参数（带默认值）：

- `DAILYHUB_XIAOJU_BASE_URL`（默认 `https://energy.xiaojukeji.com`）
- `DAILYHUB_XIAOJU_CITY_ID`（默认 `5`）
- `DAILYHUB_XIAOJU_BIZ_LINE`（默认 `250`）
- `DAILYHUB_HTTP_TIMEOUT_SECONDS`（默认 `30`）
- `DAILYHUB_HTTP_RETRIES`（默认 `3`）

---

## 6. 成功判定

- `already_signed`：
  - `sign/main` 结果中包含当天签到日期
- `signed`：
  - 未签到 -> 调 `doSign` -> 复查 `sign/main` 包含当天签到日期

失败判定：

- 认证失败：`401/403` 或响应码明确提示 `TICKET ERROR`
- 业务失败：`doSign` 返回失败且复查仍未签到
- 网络失败：超时/连接异常且重试耗尽

---

## 7. 验收标准

1. 能通过单命令触发 `xiaoju.checkin` 任务
2. 任务结果包含：
   - `success`
   - `status`（`already_signed` / `signed` / `failed`）
   - `message`
   - `data`（含请求链路关键响应）
3. 已签到场景重复执行不报错
4. 所有认证信息来自环境变量，无硬编码密钥
5. 日志中可看到每个步骤开始/结束与错误原因

---

## 8. 验证步骤

```bash
# 1) 查看帮助
python3 -m checkin.xiaojuchongdian.src.main --help

# 2) 检查任务注册
python3 -m checkin.xiaojuchongdian.src.main list

# 3) 运行小桔签到（需先配置环境变量）
python3 -m checkin.xiaojuchongdian.src.main run --task xiaoju.checkin --verify-record

# 4) 仅查询状态
python3 -m checkin.xiaojuchongdian.src.main status --task xiaoju.checkin
```

---

_Last updated: 2026-03-09_
