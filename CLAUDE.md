# DailyHub - Claude Code Guidelines

## Project Overview

**DailyHub** 是专为 OpenClaw（机器人）设计的任务策略中心，通过 API 协议驱动 + Prompt 提示词驱动双引擎，实现全场景的数字生活自动化。

---

## MANDATORY: Documentation-First Workflow

> **CRITICAL**: You MUST follow this workflow for ALL development tasks. Direct code implementation WITHOUT prior documentation is STRICTLY PROHIBITED.

### Required Workflow (Non-Negotiable)

```
1. DOCUMENT FIRST  →  2. REVIEW DOCS  →  3. IMPLEMENT  →  4. VERIFY
```

**Step 1: Document First**
- Before writing ANY code, create or update the relevant documentation
- Requirements go in `docs/requirements/`
- Technical design goes in `docs/design/`
- Must define: What, Why, How, Acceptance Criteria

**Step 2: Review Docs**
- Confirm documentation is complete and clear
- Check for conflicts with existing design/standards
- Get user approval on approach before coding

**Step 3: Implement**
- Follow the documented spec exactly
- Adhere to `docs/standards/coding-standards.md`
- Reference `docs/standards/project-conventions.md`

**Step 4: Verify**
- Run verification steps defined in the requirement doc
- Update docs if implementation differs from design
- No "it should work" claims — run actual verification commands

### When to Create Documentation

| Situation | Required Doc |
|-----------|-------------|
| New feature / integration | `docs/requirements/` + `docs/design/` |
| API integration (new platform) | `docs/design/api-integrations.md` |
| Bug fix (non-trivial) | Note in relevant design doc |
| Refactoring | Update `docs/design/` + `docs/standards/` |
| New conventions adopted | `docs/standards/project-conventions.md` |

### MANDATORY: README Synchronization

> **CRITICAL**: `README.md` is the user-facing documentation and MUST be kept in sync with `CLAUDE.md` and the actual codebase state.

**When you modify ANY of the following, you MUST update `README.md`:**

1. **Task Schedule Changes** → Update "已落地任务" table in README
   - Adding/removing tasks in `daily/skill/SKILL.md`
   - Changing task timing or descriptions

2. **Architecture Changes** → Update "设计核心" and directory structure sections
   - Modifying project structure
   - Changing the dual-engine design

3. **New Skills Added** → Update "🧩 Skill 清单" table in README
   - Creating new skill directories
   - Adding platform integrations

4. **Workflow Changes** → Update "🤖 自动化日常任务规划" section
   - Changing execution logic
   - Modifying notification strategies
   - Updating dependency assets

**Rule**: Every change to `CLAUDE.md` or the project structure requires a README review. Check the README diff before committing.

---

## Project Architecture

### Dual-Engine Design

```
DailyHub
├── API-Driven Tasks      # 固定流程、需精确执行
│   ├── Check-ins         # 多平台自动签到
│   ├── State Queries     # 账户状态查询
│   └── Unsubscribe       # 退订/取消订阅
└── Prompt-Driven Tasks   # 自然语言、灵活处理
    └── Natural Language Commands
```

### Directory Structure

```
DailyHub/
├── CLAUDE.md                          # This file
├── README.md                          # Project overview
├── daily/                             # Top-level entry point
│   └── skill/
│       └── SKILL.md                   # Cron registry ONLY — no logic (edit here to add tasks)
├── checkin/                           # API-driven check-in modules (per platform)
│   └── xiaojuchongdian/
│       ├── skill/                     # Skill definitions for OpenClaw
│       │   ├── overall/               # Self-contained entry skill (xiaoju-overall)
│       │   ├── checkin/               # [DEPRECATED] merged into overall
│       │   └── get-params/            # Auth refresh skill (xiaoju-get-params)
│       └── src/                       # Python implementation (沉淀的程序化资产)
├── routine/                           # Prompt-driven or scheduled routines
│   └── ai-morning/
│       └── skill/
│           ├── daily-news/
│           ├── frontier-changelog/
│           └── morning-publish/
├── docs/
│   ├── requirements/                  # Feature requirements
│   ├── design/                        # Technical design docs
│   ├── standards/                     # Coding standards & conventions
│   └── analysis/                      # Project analysis
└── tests/                             # Test suite
```

### Skill Architecture

`daily/skill/SKILL.md` is the **single entry point** — a cron registry that maps times to **skill names**.
Every skill is self-contained: goal, available tools, constraints, and success criteria in one SKILL.md.

```
daily/skill/SKILL.md          ← Cron registry (Time | Skill Name | Goal). No logic here.
     │
     ├── xiaoju-overall       ← Self-contained checkin skill (depends on xiaoju-get-params)
     ├── daily-news           ← AI daily news skill
     ├── frontier-changelog   ← IDE/model changelog skill
     └── morning-publish      ← Merge & publish skill
```

**Skill design principle**: Tell the AI **what to do** + **what tools are available**, not **how to execute**. Programmatic assets (Python CLI, Shell scripts) are described as "available tools" — the AI reads the code and decides how to use them.

**Rule**: `daily/skill/SKILL.md` contains only a table of `Time | Skill Name | Goal`. All logic belongs inside each skill. Skills reference each other by **name** (not path).

### Adding a New Task to the Daily Schedule

1. Build the vertical skill: `checkin/<platform>/skill/` or `routine/<name>/skill/`
2. Add one row to `daily/skill/SKILL.md`: `Time | Skill Name | Goal`
3. That's it — no other files need editing.

---

## Development Standards

### Code Style
- Follow conventions in `docs/standards/coding-standards.md`
- Follow project patterns in `docs/standards/project-conventions.md`

### Adding New Platform Integrations
1. Document the platform's API in `docs/design/api-integrations.md`
2. Define the task type (API-driven or Prompt-driven)
3. Document authentication method and rate limits
4. Define error handling strategy
5. Then implement

### Commit Guidelines
- Commits must reference the relevant doc file
- Format: `feat: [platform] add auto check-in (see docs/design/...)`

---

## Key Constraints

- **No undocumented features**: Every feature needs a doc before code
- **No magic numbers**: All platform-specific configs must be documented
- **No silent failures**: All API integrations must have defined error handling
- **Secrets management**: API keys/tokens must NEVER be committed — document storage strategy in design docs
