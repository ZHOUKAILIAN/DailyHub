---
name: self-optimize
description: Automatically fix and improve DailyHub skills by analyzing issues, following docs-first workflow, creating PRs with fixes, and reloading updated skills. Use when skills fail, APIs change, or improvements are needed. Handles bug fixes, documentation sync, error handling, and outdated API updates. Always triggers when user mentions "self-optimize", "fix skill", "improve skill", "skill broken", or provides a skill path with an issue description.
---

# Self-Optimize Skill

Enables DailyHub to self-improve by detecting issues in existing skills and automatically creating pull requests with fixes.

## Purpose

When skills fail or need optimization, this skill automates the fix-test-deploy cycle by:
1. Cloning the repository
2. Analyzing and fixing issues
3. Following project conventions
4. Creating PRs for human review
5. Reloading updated skills after merge

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

## Creating New Skills

**Important:** When creating new skills within DailyHub, always use the `skill-creator` skill.

**How to use skill-creator:**

1. **Check if skill-creator is installed:**
   ```bash
   npx skills list -g | grep skill-creator
   ```

2. **If not installed, install it:**
   ```bash
   npx skills add https://github.com/anthropics/skills --skill skill-creator -y -g
   ```

3. **Trigger skill-creator** (method depends on your AI agent):
   - For Claude Code: The skill is auto-loaded, just mention "create a new skill"
   - For OpenClaw: Reference the installed skill path
   - For other agents: Consult the skill based on your agent's skill invocation method

4. **Provide skill requirements:**
   - Skill name
   - Description of what it should do
   - When it should trigger
   - Example use cases

**Why:** Ensures skills follow best practices, have proper structure, and include test cases.

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

This skill can optimize:
- `checkin/xiaojuchongdian/skill/*` - Xiaoju Charging skills
- `routine/ai-morning/skill/*` - Morning routine skills
- Any future skills following DailyHub conventions

---

## Failure Policy

- If prerequisites check fails → Halt immediately, provide clear error
- If analysis finds no issues → Return success with "No issues detected"
- If fix generation fails → Save progress, request user guidance
- If PR creation fails → Keep branch pushed, provide manual PR instructions
- Always cleanup temp workspace (even on error)

---

_Last updated: 2026-03-14_
