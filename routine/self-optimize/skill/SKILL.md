---
name: self-optimize
description: Comprehensive skill management for DailyHub - handles both creating new skills and modifying existing ones. For new skills, supports three patterns (pure custom, reuse external skill, extend external skill). For modifications, handles bug fixes, API updates, and improvements via docs-first workflow and automated PRs. Triggers on "create skill", "new skill", "fix skill", "improve skill", "skill broken", or skill path with issue description.
---

# Self-Optimize Skill

Enables DailyHub to self-improve by managing the complete skill lifecycle: creation and optimization.

## Purpose

This skill handles two main scenarios:

### Scenario A: Creating New Skills
When you need to add new functionality to DailyHub, this skill guides you through three patterns:
1. **Pure Custom Skill** - Build from scratch (e.g., `frontier-changelog`)
2. **Reuse External Skill** - Use existing skill as-is
3. **Extend External Skill** - Reuse + add customization (e.g., `daily-news`)

### Scenario B: Modifying Existing Skills
When skills fail or need optimization, this skill automates the fix-test-deploy cycle:
1. Cloning the repository
2. Analyzing and fixing issues
3. Following project conventions
4. Creating PRs for human review
5. Reloading updated skills after merge

## Decision Tree: Which Scenario?

**Ask user first:**
- "Are you creating a new skill or modifying an existing one?"

Then follow the appropriate workflow below.

---

# SCENARIO A: Creating New Skills

## Step 0: Identify Creation Pattern

**Ask user:**
1. What functionality do you need?
2. Is there an existing external skill that does this (partially or fully)?

**Based on answers, classify into one of three patterns:**

### Pattern 1: Pure Custom Skill (Build from Scratch)

**When to use:**
- No existing skill provides similar functionality
- Unique business logic specific to DailyHub

**Example:** `frontier-changelog` - custom logic to scrape IDE changelogs

**Tools needed:**
- `skill-creator` skill (for scaffolding)
- Custom implementation (Python, JS, etc.)

**Workflow:** → See [A1: Pure Custom Skill Workflow](#a1-pure-custom-skill-workflow)

---

### Pattern 2: Reuse External Skill (No Customization)

**When to use:**
- External skill fully satisfies requirements
- No need for additional logic or output customization

**Example:** Hypothetical - directly using `weather-forecast` skill without changes

**Tools needed:**
- `skill-installer` (to install external skill)
- SKILL.md wrapper (to invoke external skill)

**Workflow:** → See [A2: Reuse External Skill Workflow](#a2-reuse-external-skill-workflow)

---

### Pattern 3: Extend External Skill (Reuse + Customize)

**When to use:**
- External skill provides core functionality
- Need to add customization layer (style constraints, output formatting, pre/post-processing)

**Example:** `daily-news` - reuses `daily-intelligence-news` + adds style guard + output format

**Tools needed:**
- `skill-installer` (to install base skill)
- `skill-creator` (to scaffold wrapper)
- Custom implementation (for customization logic)

**Workflow:** → See [A3: Extend External Skill Workflow](#a3-extend-external-skill-workflow)

---

## A1: Pure Custom Skill Workflow

### Step 1: Use skill-creator

**Actions:**
1. Check if `skill-creator` is installed:
   ```bash
   npx skills list -g | grep skill-creator
   ```
2. If not installed:
   ```bash
   npx skills add https://github.com/anthropics/skills --skill skill-creator -y -g
   ```
3. Invoke `skill-creator` and provide:
   - Skill name
   - Description
   - Trigger conditions
   - Example use cases

**Output:** Scaffolded skill directory with `SKILL.md` template

---

### Step 2: Implement Custom Logic

**Actions:**
1. Create `src/` directory under skill path
2. Implement business logic in preferred language (Python, JS, Shell, etc.)
3. Follow `docs/standards/coding-standards.md`
4. Add error handling and logging

**Example structure:**
```
routine/<name>/skill/<skill-name>/
├── SKILL.md          # Skill definition
└── src/              # Implementation
    ├── main.py       # Entry point
    └── config.yaml   # Config (if needed)
```

---

### Step 3: Document Following Docs-First Workflow

**Actions:**
1. Create `docs/requirements/<skill-name>-requirements.md`
2. Create `docs/design/<skill-name>-design.md`
3. Update SKILL.md with:
   - Purpose
   - Execution flow
   - Input/output format
   - Failure policy

**Why:** Follow CLAUDE.md mandatory docs-first workflow

---

### Step 4: Test & Create PR

**Actions:**
1. Test skill locally
2. Create branch: `feat/skill-<skill-name>`
3. Commit changes with reference to docs
4. Create PR using `gh pr create`

**Output:** PR URL for review

---

## A2: Reuse External Skill Workflow

### Step 1: Install External Skill

**Actions:**
1. Identify external skill URL/identifier
2. Install via `skill-installer` or package manager:
   ```bash
   npx skills add <external-skill-url> -y -g
   ```
3. Verify installation:
   ```bash
   npx skills list -g | grep <skill-name>
   ```

**Output:** External skill available in runtime

---

### Step 2: Create Wrapper SKILL.md

**Actions:**
1. Create skill directory: `routine/<name>/skill/<skill-name>/`
2. Create minimal `SKILL.md`:
   ```yaml
   ---
   name: <skill-name>
   description: <brief description>
   ---

   # <Skill Name>

   ## Purpose
   <What this skill does>

   ## External Dependency
   - Skill: `<external-skill-name>`
   - Source: <URL>

   ## Execution Flow
   1. Verify `<external-skill-name>` is installed
   2. Invoke `<external-skill-name>` directly
   3. Return result to user

   ## Failure Policy
   - If external skill not found → Install it first
   - If execution fails → Report error, do not retry
   ```

**Why:** Wrapper provides discoverability and documentation

---

### Step 3: Document & Register

**Actions:**
1. Create `docs/requirements/<skill-name>-requirements.md` (minimal, reference external skill)
2. Add to `daily/skill/SKILL.md` if scheduled
3. Test invocation

**Output:** Skill ready to use

---

## A3: Extend External Skill Workflow

### Step 1: Install Base Skill

**Actions:**
1. Install external skill (same as A2 Step 1)
2. Verify base functionality works

---

### Step 2: Scaffold Extension with skill-creator

**Actions:**
1. Use `skill-creator` to create wrapper structure
2. Define customization points in SKILL.md:
   - Pre-processing steps
   - Post-processing steps
   - Style constraints
   - Output format transformations

**Example (from `daily-news`):**
```yaml
---
name: daily-news
description: Run the daily AI news workflow by invoking an existing external capability with style customization.
---

# AI Daily News Skill

## Purpose
Fetch morning AI daily news with anti-trope style constraints.

## External Capability
- Capability name: `daily-intelligence-news`
- Reference: https://openclawmp.cc/asset/s-027065c89db7e63f
- Style guard: https://tropes.fyi/tropes-md

## Execution Flow
1. Verify `daily-intelligence-news` is installed
2. Invoke with style constraint (anti-trope from tropes.md)
3. Apply output formatting rules
4. Return EXACT FULL Markdown content

## Customization Layer
- Style enforcement (avoid AI tropes)
- Output format enforcement (full content, not summary)
```

---

### Step 3: Implement Customization Logic

**Actions:**
1. Create `src/` directory if customization requires code
2. Implement:
   - Input transformation (before calling base skill)
   - Output transformation (after calling base skill)
   - Style guards, validators, formatters
3. Follow coding standards

**Example structure:**
```
routine/<name>/skill/<skill-name>/
├── SKILL.md                # Skill definition + extension spec
└── src/                    # Customization logic (optional)
    ├── wrapper.py          # Calls base skill + applies customization
    └── style_guard.py      # Style enforcement logic
```

---

### Step 4: Document Extension

**Actions:**
1. Create `docs/requirements/<skill-name>-requirements.md`:
   - Base skill reference
   - Customization requirements
2. Create `docs/design/<skill-name>-design.md`:
   - Extension architecture
   - Customization points
3. Update SKILL.md with clear separation:
   - External capability section
   - Customization layer section

---

### Step 5: Test & Create PR

**Actions:**
1. Test base skill invocation
2. Test customization layer
3. Create PR with pattern label: `feat(skill): add <skill-name> (extends <base-skill>)`

**Output:** PR URL for review

---

# SCENARIO B: Modifying Existing Skills

## Workflow

### Prerequisites Check

**Before any git operations, verify:**

1. **GitHub CLI authentication**:
   - Run: `gh auth status`
   - If not authenticated → Ask user: "GitHub CLI is not authenticated. Please run: `gh auth login` and confirm when ready."
   - Wait for user confirmation before proceeding

2. **Git configuration**:
   - Check: `git config user.name` and `git config user.email`
   - If missing → Ask user: "Git user info not configured. Please provide your name and email."
   - Set config: `git config --global user.name "<provided_name>"`
   - Set config: `git config --global user.email "<provided_email>"`

**Why:** Prevent failures mid-workflow due to auth issues. User interaction ensures proper setup.

---

### Input Parameters

**From User:**
- `issue_description`: Description of the problem (e.g., "Xiaoju check-in fails with 401")
- `repo_url`: User's repository URL (prompt if not provided)

**Inferred by AI:**
- `skill_path`: Automatically identify the skill path based on issue description
  - Parse user's description to extract skill name/platform
  - Search DailyHub directory structure to find matching skill
  - Examples:
    - "Xiaoju check-in fails" → `checkin/xiaojuchongdian/skill/checkin/`
    - "AI daily news broken" → `routine/ai-morning/skill/daily-news/`
    - "morning publish not working" → `routine/ai-morning/skill/morning-publish/`
  - If ambiguous → Ask user to clarify which skill

---

### Step 1: Clone & Analyze

**Actions:**
1. Clone repository to temp workspace:
   - Use system temp directory (e.g., `/tmp/` on Unix, `%TEMP%` on Windows)
   - Format: `<temp>/dailyhub-optimize-<timestamp>`
   - Use `--depth=1` for speed

2. **Identify skill path** (if not explicit in user input):
   - Parse issue description for keywords: platform names, skill names
   - Search repository for all `SKILL.md` files (typically under `*/skill/*/SKILL.md` pattern)
   - Read each SKILL.md's name and description fields
   - Match keywords from issue description against skill names/descriptions
   - If multiple matches → Present options and ask user to choose
   - If no match → List all available skills and ask user to select one
   - Record the skill's directory path for later steps

3. Read skill definition: `<skill_path>/SKILL.md`
4. Read implementation (if exists):
   - `<skill_path>/src/` directory - may contain Python, JavaScript, Shell scripts, or other code
   - Check for `*.py`, `*.js`, `*.sh`, `*.ts`, or any other source files
   - Also check for configuration files, requirements, package.json, etc.
5. Analyze issue:
   - Use `issue_description` as primary context
   - Also run heuristics: Check for `TODO`, `FIXME`, hardcoded secrets, missing error handling
6. Classify issue type:
   - `runtime_error`: Code crashes or exceptions
   - `api_deprecated`: External API changed
   - `doc_mismatch`: SKILL.md doesn't match code behavior
   - `error_handling`: Missing try/except or validation
   - `other`: General improvements

**Output:** Issue report with type, affected files, description, severity

---

### Step 2: Decide Fix Strategy

**Decision: Docs-First or Code-Only?**

| Issue Type | Docs Update Required? | Rationale |
|------------|----------------------|-----------|
| API change / behavior change | ✅ Yes | Update `docs/design/api-integrations.md` + requirements |
| Refactoring / new auth flow | ✅ Yes | Update `docs/requirements/*.md` + `docs/design/*.md` |
| Simple bug fix (typo, null check) | ❌ No | No behavior change, code-only |
| Skill logic change | ✅ Yes | Update `skill/SKILL.md` to match code |
| Documentation fix | ✅ Yes | Update relevant docs |

**Why:** Follow CLAUDE.md docs-first workflow; prevent undocumented behavior changes.

**Identify Files to Update:**
- Behavior change → `docs/requirements/` + `docs/design/`
- API integration → `docs/design/api-integrations.md`
- Skill logic → `skill/SKILL.md` + implementation code in `src/`
- Config/env vars → Config files in `src/` + `docs/requirements/*.md`

---

### Step 3: Generate Fix

**If Docs-First (behavior change):**
1. Update docs first:
   - `docs/requirements/` or `docs/design/` with new behavior
   - Follow existing doc structure
2. Generate code changes to match updated docs
3. Follow `docs/standards/coding-standards.md`

**If Code-Only (simple bug):**
1. Apply minimal code fix
2. Verify no behavior change
3. No doc updates needed

**Commit Message Format:**
```
fix(skill): <short description>

Affected: <list of changed files>

<Optional: reference to doc changes>
```

**Why:** Maintain traceability and follow project conventions.

---

### Step 4: Create PR

**Actions:**
1. Create branch: `fix/skill-<skill-name>-<timestamp>`
2. Commit changes with message from Step 3
3. Push branch to remote
4. Create PR using `gh pr create`:
   ```bash
   gh pr create --title "<title>" --body "$(cat <<'EOF'
   ## Issue
   <Issue description>

   ## Changes
   - Updated files: <list>
   - Key changes: <summary>

   ## Documentation Updates
   <If applicable, list updated docs with links>

   ## Verification Steps
   <How to verify the fix works>

   ## Checklist
   - [ ] Follows CLAUDE.md docs-first workflow
   - [ ] Follows coding standards
   - [ ] No secrets committed
   - [ ] Commit message references docs (if applicable)

   ---
   🤖 Auto-generated by DailyHub self-optimize skill
   EOF
   )"
   ```

**Output:** PR URL

**Why:** Provide full context for human review.

---

### Step 5: User Review & Merge

**Process:** (Manual by user)
1. User reviews PR on GitHub
2. Checks verification steps
3. Merges PR if approved

**Why:** Human oversight required (NFR1.2).

---

### Step 6: Reload Skill (After Merge)

**Actions:**
1. Run `git pull origin main` in live DailyHub instance
2. Notify user with reload instructions (agent-specific):
   - For OpenClaw: `openclaw reload <skill_path>`
   - For Claude Code: Skills auto-reload on file change
   - For other agents: Provide instructions based on their skill reload mechanism
   - Or simply: "Skill updated. Please reload your agent to use the updated skill."

**Output:** Reload instructions tailored to user's agent

---

## Error Handling

### Prerequisites Errors (Step 0)

| Error | Detection | Action |
|-------|----------|--------|
| `gh` not installed | `gh --version` fails | Ask user: "GitHub CLI not found. Install it from https://cli.github.com (or use your package manager: `brew install gh`, `apt install gh-cli`, etc.). Confirm when done." |
| `gh` not authenticated | `gh auth status` not logged in | Ask user: "Please run: `gh auth login` to authenticate. Confirm when ready." |
| Git config missing | `git config user.name` empty | Ask user: "Please provide your git name and email for commits." Then configure globally. |

**Principle:** Guide user through setup rather than halting with errors.

### Analysis Errors (Step 1)

| Error | Detection | Action |
|-------|----------|--------|
| Skill path not found | Directory doesn't exist | Suggest corrections, list similar paths |
| No issues detected | Heuristics find nothing | Return "No issues found" (not an error) |
| Cannot understand issue | Issue description too vague | Request more details from user |

**Principle:** Clarify before proceeding.

### Fix Generation Errors (Step 3)

| Error | Detection | Action |
|-------|----------|--------|
| Cannot generate fix | AI unsure how to fix | Save analysis, request user guidance |
| Secrets detected | Regex match for API keys/tokens | Block commit, alert user |
| Fix requires new dependencies | Detected new imports | Note in PR body, flag for manual review |

**Principle:** Safety over automation.

### Git/PR Errors (Step 4)

| Error | Detection | Action |
|-------|----------|--------|
| Push fails | Remote rejects push | Check permissions, retry once |
| PR creation fails | `gh pr create` errors | Log error, provide manual PR link |
| Branch conflict | Branch name exists | Append `-retry-<N>` suffix |

**Principle:** Graceful degradation; provide manual fallback.

---

## Pattern Selection Guide

Use this table to quickly identify which pattern fits your needs:

| Question | Pattern 1 (Pure Custom) | Pattern 2 (Reuse) | Pattern 3 (Extend) |
|----------|------------------------|-------------------|-------------------|
| **Does external skill exist?** | ❌ No | ✅ Yes, exact match | ✅ Yes, close match |
| **Need customization?** | N/A | ❌ No | ✅ Yes |
| **Implementation complexity** | High (build from scratch) | Low (wrapper only) | Medium (wrapper + custom logic) |
| **Example** | `frontier-changelog` | Direct external skill use | `daily-news` |

**Real DailyHub Examples:**

1. **frontier-changelog** (Pattern 1):
   - No external skill for IDE changelog scraping
   - Built custom web scraping logic
   - Pure custom implementation

2. **daily-news** (Pattern 3):
   - Base: `daily-intelligence-news` (external)
   - Extensions:
     - Style guard (anti-trope from tropes.md)
     - Output format enforcement (full content, not summary)
     - Optional publishing to Xiaohongshu

---

## Configuration

**Prerequisites:**
1. GitHub CLI (`gh`) installed and authenticated
2. Git user.name and user.email configured

**Runtime Parameters:**
- `repo_url`: User's repository URL (prompt if not set)
- `skill_path`: Required input
- `issue_description`: Optional (use heuristics if missing)

**Note:** Never hardcode repository URLs. Always prompt user.

---

## Security

1. **Secret Detection:**
   - Scan all changed files for patterns: API keys, tokens, passwords
   - Block commit if secrets detected
   - Alert user to remove secrets manually

2. **Path Validation:**
   - Reject paths with `../` traversal
   - Limit writes to temp workspace only

3. **SSH Key Management:**
   - Use `gh` auth for HTTPS cloning (preferred)
   - If SSH: verify key exists, never log private keys

---

## Supported Skills

### Scenario A (Creation):
- Any new skill following DailyHub conventions
- All three patterns (Pure Custom, Reuse, Extend)

### Scenario B (Modification):
- `checkin/xiaojuchongdian/skill/*` - Xiaoju Charging skills
- `routine/ai-morning/skill/*` - Morning routine skills
- Any future skills following DailyHub conventions

---

## Quick Reference: When to Use Each Approach

| Scenario | User Says | Action | Tools Needed |
|----------|-----------|--------|--------------|
| **New Skill: Pure Custom** | "Create a skill to scrape X" | Follow A1 workflow | `skill-creator` |
| **New Skill: Reuse** | "Use skill X as-is" | Follow A2 workflow | `skill-installer` |
| **New Skill: Extend** | "Use skill X but add Y customization" | Follow A3 workflow | `skill-installer` + `skill-creator` |
| **Fix Existing Skill** | "Skill X is broken" | Follow Scenario B workflow | Git + GitHub CLI |
| **Improve Existing Skill** | "Optimize skill X" | Follow Scenario B workflow | Git + GitHub CLI |

---

## Failure Policy

### Scenario A (Creation):
- If `skill-creator` unavailable → Guide installation
- If external skill unavailable → Guide installation
- If customization logic fails → Request user debugging help
- Always document before implementing

### Scenario B (Modification):
- If prerequisites check fails → Halt immediately, provide clear error
- If analysis finds no issues → Return success with "No issues detected"
- If fix generation fails → Save progress, request user guidance
- If PR creation fails → Keep branch pushed, provide manual PR instructions
- Always cleanup temp workspace (even on error)

---

_Last updated: 2026-03-15_
