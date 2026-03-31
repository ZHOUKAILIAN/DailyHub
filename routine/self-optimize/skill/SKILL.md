---
name: self-optimize
description: Manage DailyHub skill lifecycle — create new skills, fix and improve existing ones.
---

# Self-Optimize Skill

Enables DailyHub to self-improve by creating, fixing, and optimizing skills.

## Goal

When user asks to create a new skill or fix/improve an existing one, handle the full lifecycle: understand the need → implement → test → submit PR.

---

## Skill Writing Standard

**Every skill produced by self-optimize MUST follow these principles:**

### 1. Goal-Oriented, Not Step-by-Step

Tell the AI **what** to achieve, not **how** to execute. The AI can figure out commands, file discovery, and execution order on its own. Before writing, understand the user's intent by asking 2-3 clarifying questions (e.g., what is the goal? what does success look like? any constraints?).

- ✅ "Complete the daily check-in and fetch sign record to verify"
- ❌ "Run `python3 -m checkin.xiaojuchongdian.src.main run --task xiaoju.checkin --verify-record`"

### 2. Declare Available Tools, Don't Dictate Usage

If the skill has programmatic assets (scripts, CLI tools, APIs), describe **what they do** and **where they are** relative to the skill. Let the AI read the code and decide how to use them.

- ✅ "Entry point: `main.py`. Read the file to understand usage."
- ❌ "Run `python3 -m checkin.xiaojuchongdian.src.main status --task xiaoju.checkin`"

### 3. Portable Paths Only

Never hardcode absolute or repo-root-relative paths. Use paths relative to the skill itself.

- ✅ "Located in the `scripts/` directory of this skill"
- ❌ "Location: `checkin/xiaojuchongdian/skill/get-params/scripts/`"

### 4. Know What AI Can and Cannot Do

**AI can figure out on its own** (don't over-specify):
- How to run a Python/Shell/Node script after reading it
- Which subcommands or flags a CLI supports
- How to parse JSON output
- How to find files in a directory
- Error handling and retry logic

**AI needs to be told** (must specify):
- The goal and success criteria
- What programmatic assets exist and their purpose
- Key constraints (auth requirements, idempotency, user interaction needed)
- Dependencies on other skills (by skill name, not path)

### 5. Reference by Skill Name, Not Path

Skills depend on each other by **name**. OpenClaw resolves names to locations.

- ✅ "Use the `xiaoju-get-params` skill to refresh credentials"
- ❌ "Switch to `checkin/xiaojuchongdian/skill/get-params/SKILL.md`"

### 6. Declare Dependencies in skill.json

External or sub-skill dependencies must be declared in `skill.json` under `sub_skills` (by skill name), so OpenClaw can auto-install them.

---

## Scenario A: Creating New Skills

### Patterns

1. **Pure Custom** — no existing skill, build from scratch (e.g., `frontier-changelog`)
2. **Reuse External** — use an existing OpenClaw skill as-is
3. **Extend External** — wrap an existing skill with customization

### Workflow

1. Clarify what the user needs and which pattern fits
2. Scaffold the skill directory with `SKILL.md` + `skill.json`
3. Write the SKILL.md following the **Skill Writing Standard** above
4. Implement code if needed (in a `src/` or `scripts/` directory within the skill)
5. Register in `daily/skill/SKILL.md` if it's a scheduled task
6. Test and create PR

---

## Scenario B: Fixing / Improving Existing Skills

### Workflow

1. Identify which skill is affected (by skill name or user description)
2. Read the skill's SKILL.md and implementation code to understand current behavior
3. Diagnose the issue
4. Fix code and/or update SKILL.md
5. If the SKILL.md violates the **Skill Writing Standard** above, refactor it as part of the fix
6. Test and create PR

---

## Key Constraints

- **No secrets in code** — API keys/tokens via environment variables only
- **PR required** — all changes go through PR for human review
- **Docs-first for behavior changes** — update `docs/requirements/` or `docs/design/` before changing behavior
- **Simple bug fixes** can skip docs and go straight to code
