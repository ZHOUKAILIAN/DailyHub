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
│       │   ├── overall/               # Entry skill for this platform
│       │   ├── checkin/               # Execution skill
│       │   └── get-params/            # Auth capture guidance skill
│       └── src/                       # Python implementation
├── routine/                           # Prompt-driven or scheduled routines
│   └── ai-morning/
│       └── skill/
│           └── ai-daily-news-and-changelog/
├── docs/
│   ├── requirements/                  # Feature requirements
│   ├── design/                        # Technical design docs
│   ├── standards/                     # Coding standards & conventions
│   └── analysis/                      # Project analysis
└── tests/                             # Test suite
```

### Skill Architecture

`daily/skill/SKILL.md` is the **single entry point** — a cron registry that maps times to skill paths.
Every task is a self-contained vertical skill with its own execution logic and failure policy.

```
daily/skill/SKILL.md          ← Cron registry (Time | Task | Skill path). No logic here.
     │
     ├── checkin/<platform>/skill/overall/SKILL.md   ← Per-platform entry skill
     └── routine/<name>/skill/<task>/SKILL.md        ← Per-routine entry skill
```

**Rule**: `daily/skill/SKILL.md` contains only a table of `Time | Task | Skill`. All logic belongs inside each vertical skill.

### Adding a New Task to the Daily Schedule

1. Build the vertical skill: `checkin/<platform>/skill/` or `routine/<name>/skill/`
2. Add one row to `daily/skill/SKILL.md`: `Time | Task name | path to SKILL.md`
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
