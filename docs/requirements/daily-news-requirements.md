# Daily News & Changelog Requirements

## 1. 目标与背景

为了提升稳定性并解耦职责，本需求提出剥离原有的综合长链路技能。通过新建两个独立的 skill：其中第一个新闻主体获取任务依赖其他人提供的一款可用 skill（例如 `daily-intelligence-news`）；第二个更新追踪任务则由我们自行编写实现。

目标时段与任务：

1. `09:20` AI 日报主任务（通过 MCP 调用生成每日新闻）
2. `09:25` 前沿追踪主任务（IDE/CLI + 模型更新）

---

## 2. 范围

### In Scope

- 新建三个明确职责的 skill：
  - `daily-news`：专司每日 AI 新闻获取。该 skill 内部直接调用他人已经提供的现有新闻获取 skill。
  - `frontier-changelog`：专司 IDE/CLI 和模型更新获取。该 skill 为我们自定义编写的核心能力。
  - `morning-publish`：作为最后环节，将上述两个任务的结果整合，以固定模板发布到 Blog（PR）和小红书。
- 任务定义与执行策略文档化（本篇文档及对应的设计文档）。
- 调用已提供的 `daily-intelligence-news` Skill/Capability 来获取基础情报。
- 调用搜索引擎获取特定的 IDE/CLI 和大模型更新，并独立输出。
- 更新 `daily/skill/SKILL.md` (cron registry) 分别在 `09:20`、`09:25` 和 `09:30` 指向这三个新的 skill。
- 本需求不使用 `daily/skill/morning-task-schedule.md`，调度注册以 `daily/skill/SKILL.md` 为唯一入口。

### Skill 依赖关系（必须遵循）

1. `daily-news` 依赖外部 `daily-intelligence-news` 能力，仅产出 AI 日报正文。
2. `frontier-changelog` 独立执行，仅产出 IDE/CLI 与模型更新正文。
3. `morning-publish` 依赖前两者产出，负责模板合并与分发。
4. 依赖方向固定为：`daily-news` + `frontier-changelog` -> `morning-publish`。
5. 禁止反向依赖：`daily-news`/`frontier-changelog` 不得调用 `morning-publish`。
6. 禁止职责串线：`daily-news` 不抓 changelog，`frontier-changelog` 不生成日报，`morning-publish` 不重算内容。

### Out of Scope

- 不再维护原有 `ai-daily-news-and-changelog` 的执行逻辑，并从仓库中删除该废弃入口。
- 不修改 `09:00` 小桔充电等其他任务。

---

## 3. 功能需求

### FR-001: 依赖明确分离的能力提供方

- 日报新闻获取：调用其他人现成提供的 `daily-intelligence-news` skill。
- 由于不再走原有的合并大锅饭链路，降低了网络与解析超时风险。
- 外部依赖按“可直接使用”处理，不在本需求中增加额外契约定义。
- 外部能力参考链接（文档用途）：
  - `daily-intelligence-news`（OpenClaw asset）：`https://openclawmp.cc/asset/s-027065c89db7e63f`
- 能力使用策略：
  - 若本地/运行环境已存在该能力：直接调用。
  - 若不存在：先通过 `skill-installer` 安装对应能力，再执行任务。
- `daily-news` 可使用的工具前提（参考旧链路）：
  - 可直接调用的 `daily-intelligence-news` skill / capability。
  - 可用 MCP 调用链路（由运行环境预置）。
  - 运行时不依赖 URL 动态发现能力（链接仅用于文档指引）。

### FR-002: 前沿更新追踪 (IDE/CLI & Models)

- 强制要求 AI **依次搜索** 特定 IDE/CLI 工具的 Changelog（Claude Code, Codex, Cursor, Gemini CLI, Antigravity, OpenCode）。
- 强制要求搜索核心大模型的更新发布。
- 作为独立的任务执行，输出结构化的变更汇总。
- `web_search` 执行约束：必须串行执行（单次仅查询一个工具），按固定顺序依次完成，不可并行或批量合并查询。
- Changelog 来源策略（按优先级）：
  1. 官方网站的 release notes / changelog 页面。
  2. GitHub 官方组织/仓库的 `Releases` 或官方公告。
  3. 仅当官方来源暂无信息时，才使用可信二级来源，并在结果中标注“非官方来源”。
- IDE/CLI 官方来源清单（已核对可访问）：
  - Claude Code:
    - `https://docs.anthropic.com/en/release-notes/claude-code`
    - `https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md`
  - Codex:
    - `https://developers.openai.com/codex/changelog`
    - `https://github.com/openai/codex/releases`
  - Cursor:
    - `https://cursor.com/changelog`
  - Gemini CLI:
    - `https://google-gemini.github.io/gemini-cli/docs/changelogs/`（官方 changelog 页）
    - `https://r.jina.ai/http://google-gemini.github.io/gemini-cli/docs/changelogs/`（抓取兜底入口）
    - `https://github.com/google-gemini/gemini-cli/releases`
  - Antigravity:
    - `https://antigravity.google/changelog`（官方 changelog 页）
    - `https://r.jina.ai/http://antigravity.google/changelog`（抓取兜底入口）
  - OpenCode:
    - `https://opencode.ai/changelog`
    - `https://github.com/anomalyco/opencode/tags`
- 输出要求：每条 IDE/CLI 变更至少附 1 个可追溯来源链接（优先官网或 GitHub 官方）。

### FR-003: 合并发布与分发 (Blog PR & 小红书)

- 完成以上两个任务后，通过一个聚合的分发任务完成发布。
- 发布模板必须严格为：

  ```
  AI 日报
  [Task 1 产生的内容]

  IDE/CLI changelog
  [Task 2 产生的内容]
  ```

- 按此模板写入 Blog 文件并提交 PR。
- 按此模板发布到小红书（调用对应的发布插件/Skill）；请求发出即视为成功，不校验返回内容。
- 小红书发布能力参考链接（文档用途）：
  - Agent-Reach 安装文档: `https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md`
- 小红书能力使用策略：
  - 若本地/运行环境已有可用小红书发布 skill：直接使用。
  - 若不存在：按安装文档执行安装，默认命令为：
    - `pip install https://github.com/Panniantong/agent-reach/archive/main.zip`
    - `agent-reach install --env=auto`
  - 若生产环境要求安全安装：使用 `agent-reach install --env=auto --safe`。
- 必须在终端回执合并后的全文内容以及分发（PR链接、小红书已发起）的最终状态。

---

## 4. 验收标准

1. 创建对应的 `daily-news`、`frontier-changelog` 和 `morning-publish` 开发文档。
2. 新增的三个 skill 必须由 `skill-creator` 创建以保证合规性。
3. `daily/skill/SKILL.md` 成功指向这三个新入口。
4. 执行时不通过 URL 动态发现能力；依赖能力应来自本地已安装/预置技能（链接仅为文档参考）。
5. 验证生成的最终内容是否严格遵循合并模板，并成功完成 PR 及小红书分发。
6. 依赖关系符合“`daily-news` + `frontier-changelog` -> `morning-publish`”，无反向调用与职责串线。

_Last updated: 2026-03-11_
