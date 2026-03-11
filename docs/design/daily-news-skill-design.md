# Daily News & Changelog Design

## 1. 设计目标
基于 `routine/ai-morning/skill/ai-daily-news-and-changelog` 的痛点，本设计旨在将原来大一统的大长链路任务**拆解**为三步：
1. **纯粹的 AI 日报获取**：调用其他人提供的现成 skill（如 `daily-intelligence-news`）生成基础新闻。
2. **前沿版本追踪**：自定义 skill 通过搜索关注特定开发工具和大模型的更新。
3. **聚合分发**：以固定模板合并两者的输出，并统一分发到 Blog (PR) 和小红书。

设计原则：
1. **单一职责**：内容获取（新闻、Changelog）与内容分发（合并发布）相互解耦，通过对话上下文或临时存储连接。
2. **本地环境强依赖**：所有外部能力（新闻生成、小红书发布）均由系统在运行前作为内置 Skill 提供，避开动态抓取解析 URL。
3. **标准化构建**：所有新增的 Skill 必须要通过系统提供的 `skill-creator`进行创建和规范化保障。

---

## 2. 技术边界

### 现有资产
- 工具列表中拥有的 `daily-intelligence-news` Skill / Capability (由第三方或其它渠道提供)。
- 可用的 `web_search` 工具。
- （可选）分发渠道如小红书发布的 Skill/Capability。

### 新增层级
```
routine/ai-morning/skill/
├── daily-news/
│   └── SKILL.md                 # 获取 AI 新闻
├── frontier-changelog/
│   └── SKILL.md                 # 搜集 IDE/CLI 变更日志
└── morning-publish/
    └── SKILL.md                 # 合并二者并分发(Blog PR + 小红书)
```

---

## 3. 分拆执行流程

### Task A: `daily-news`
1. 调用工具箱/系统中提供的别人写好的 `daily-intelligence-news` 来生成当日新闻摘要。
2. **强输出**：在这个会话中，将生成好的新闻 Markdown 格式全文直接打在对话流中返回给用户，等待后续步骤使用该结果。

### Task B: `frontier-changelog`
1. 调用 web search 能力，*严格串行*执行（一次只搜一个工具，不允许并行）：
   - Claude Code 近期版本更新日志（changelog）或发布动态。
   - Codex (或 GitHub Copilot) 关键能力提升。
   - Cursor 近期更新或 release notes。
   - Gemini CLI 近期更新或 release notes。
   - Antigravity 更新。
   - OpenCode 更新。
   - 主流基座大模型（如 GPT-4, Claude-3.5, Gemini 1.5, DeepSeek 等）发布、价格调整或能力变化。
2. 来源选择规则（按优先级）：
   - 官网 changelog / release notes 页面（首选）。
   - GitHub 官方仓库 `Releases` 或官方公告（次选）。
   - 仅在无官方来源时使用可信二级来源，并在结果中明确标注“非官方来源”。
3. IDE/CLI 推荐官方来源：
   - Claude Code: `https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md`
   - Codex: `https://developers.openai.com/codex/changelog`, `https://github.com/openai/codex/releases`
   - Cursor: `https://cursor.com/changelog`
   - Gemini CLI: `https://google-gemini.github.io/gemini-cli/docs/changelogs/`, `https://r.jina.ai/http://google-gemini.github.io/gemini-cli/docs/changelogs/`, `https://github.com/google-gemini/gemini-cli/releases`
   - Antigravity: `https://antigravity.google/changelog`, `https://r.jina.ai/http://antigravity.google/changelog`
   - OpenCode: `https://opencode.ai/changelog`, `https://github.com/anomalyco/opencode/tags`
4. 精简过滤：若无实质进展（如仅修了个别非感知 bug），则忽略该产品的变更日志。
5. 汇总成一份专属的《AI 前沿工具与模型更新追踪》Markdown 报告。
6. **强输出**：将汇总好的 Changelog 报告全文返回给用户，作为 Task C 的基础输入；每个工具条目附来源链接。

### Task C: `morning-publish`
1. 提取上下文（或者接收用户在同一编排中传递的下文）中 Task A 和 Task B 的输出。
2. 按照严格模板合并：
   ```markdown
   AI 日报
   [Task A 的原始输出内容]

   IDE/CLI changelog
   [Task B 的原始输出内容]
   ```
3. 写盘并提交 PR（Blog 归档）。
4. 调用小红书发布功能，完成线上图文投放。若失败重试 1 次。
5. **最终强输出**：报告分发结果（PR #、小红书状态）并在终端最终展示上述合并模板全文。

---

## 4. 失败处理策略

| 执行层 | 场景 | 策略 |
|--------|------|------|
| Task A | 日报主体生成失败 | 返回失败结果并在最终报错中止整个流程。 |
| Task B | 搜索失败或无更新内容| 忽略该单品，汇总更新部分。若均无更新，则在报告段落填“无”。 |
| Task C | 合并输出小红书失败 | 重试仍失败时，保留已创建的 PR，并在尾部打印失败原因。 |

## 5. 输出结构参考

### Task A 输出样例
```markdown
### AI Daily News
- xxxx
- yyyy

(若开启分发则附加：[小红书发布状态])
```

### Task B 输出样例
```markdown
### Frontier Updates (IDE & CLI)
- **Claude Code**: v1.X (更新内容缩影)
- **Gemini CLI**: vX.X (更新内容缩影)
- **Cursor**: vX.X (更新内容缩影)
- **Codex**: vX.X (更新内容缩影)
- **Antigravity**: vX.X (更新内容缩影)
- **OpenCode**: vX.X (更新内容缩影)

### Model Updates
- **Claude 3.5 Sonnet**: 能力加强点...
```
