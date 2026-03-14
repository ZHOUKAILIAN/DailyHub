# Self-Optimize Skill - Design

## Overview

Enable DailyHub to automatically fix and improve existing skills through automated PR creation. The skill focuses on **workflow orchestration** and **decision logic**, not implementation details (AI will handle the code).

---

## Core Workflow

```
User Reports Issue
    ↓
[0] Prerequisites Check (gh auth + git config)
    ↓
[1] Clone & Analyze
    ↓
[2] Decide: Docs-First or Code-Only?
    ↓
[3] Generate Fix
    ↓
[4] Create PR
    ↓
[5] User Reviews & Merges
    ↓
[6] Auto-Reload Skill (optional)
```

---

## Decision Points

### Decision 1: Prerequisites Check

**When:** Before any git operations
**Check:**
1. Is `gh` CLI installed and authenticated? (`gh auth status`)
2. Is git config set? (`git config user.name` / `user.email`)

**Actions:**
- ✅ All ready → Proceed to clone
- ❌ `gh` not ready → Halt, ask user to run `gh auth login`
- ❌ Git config missing → Halt, ask user to configure git user info

**Why:** Prevent failures mid-workflow due to auth issues.

---

### Decision 2: Docs-First or Code-Only?

**When:** After analyzing the issue
**Criteria:**

| Issue Type | Docs Update Required? | Examples |
|------------|----------------------|----------|
| Behavior change | ✅ Yes | API endpoint changed, new auth flow |
| Bug fix (non-trivial) | ✅ Yes | Logic error requiring workflow change |
| Simple bug fix | ❌ No | Typo in variable name, missing null check |
| Refactoring | ✅ Yes | Restructure modules, change conventions |
| Documentation fix | ✅ Yes | Update SKILL.md, add missing params |

**Actions:**
- If **docs required**:
  1. Update `docs/requirements/` or `docs/design/` first
  2. Then update code
  3. Reference doc changes in commit message
- If **code-only**:
  1. Apply code fix directly
  2. Ensure no behavior change
  3. Commit with clear description

**Why:** Follow CLAUDE.md docs-first workflow; prevent undocumented behavior changes.

---

### Decision 3: What Files to Modify?

**When:** During fix generation
**Criteria:**

| Change Category | Files to Touch | Notes |
|-----------------|---------------|-------|
| API integration fix | `src/*.py` + `docs/design/api-integrations.md` | Document new endpoints/headers |
| Auth flow change | `src/*.py` + `docs/requirements/*.md` + `docs/design/*.md` | Update both requirements and design |
| Error handling improvement | `src/*.py` only | No docs if behavior unchanged |
| Skill logic fix | `skill/SKILL.md` + `src/*.py` | Sync SKILL.md with code changes |
| Config/env var change | `src/config.py` + `docs/requirements/*.md` | Document new env vars |

**Why:** Maintain consistency between docs and code.

---

## Workflow Steps (Detailed)

### Step 0: Prerequisites Check

**Inputs:** None (environment check)
**Process:**
1. Check `gh` CLI: Run `gh auth status`
   - If not authenticated, return error: "Please run: `gh auth login`"
2. Check git config: Run `git config user.name` and `git config user.email`
   - If missing, return error: "Please configure git user.name/email"

**Outputs:**
- ✅ All checks pass → Continue
- ❌ Any check fails → Halt with descriptive error

**Why:** Avoid wasting time cloning/analyzing only to fail at commit/push stage.

---

### Step 1: Clone & Analyze

**Inputs:**
- `issue_description`: User-provided issue description (e.g., "Xiaoju check-in fails with 401")
- `repo_url`: User's repository URL (prompt user if not set)

**Process:**
1. Clone repo to temp workspace (system temp directory + `dailyhub-optimize-<timestamp>`)
   - Use `--depth=1` for speed

2. **Identify skill path** (AI infers from description):
   - Search repository for all `SKILL.md` files
   - Parse each skill's name and description
   - Match keywords from issue description
   - If ambiguous → Ask user to choose from matching skills
   - If no match → List all skills and ask user to select

3. Read skill definition: `<skill_path>/SKILL.md`

4. Read implementation (if exists):
   - Check `<skill_path>/src/` for any source files (Python, JS, Shell, etc.)
   - Read relevant code files

5. Analyze issue:
   - Use `issue_description` as primary context
   - Run heuristics: Check for `TODO`, `FIXME`, hardcoded secrets, missing error handling

6. Classify issue type: `runtime_error` | `api_deprecated` | `doc_mismatch` | `error_handling` | `other`

**Outputs:**
- Issue report: `{ type, affected_files, description, severity }`

**Why:** Understand the problem before generating a fix. AI locates the skill rather than requiring user to know exact paths.

---

### Step 2: Decide Fix Strategy

**Inputs:** Issue report from Step 1
**Process:**
1. Check issue type:
   - If `api_deprecated` or behavior change → Docs-first workflow
   - If simple bug (typo, null check) → Code-only workflow
2. Identify affected doc files:
   - Behavior change → `docs/requirements/*.md` + `docs/design/*.md`
   - API change → `docs/design/api-integrations.md`
   - Skill logic change → `skill/SKILL.md`

**Outputs:**
- Fix strategy: `{ docs_first: bool, files_to_update: [docs, code] }`

**Why:** Ensure compliance with CLAUDE.md workflow.

---

### Step 3: Generate Fix

**Inputs:** Fix strategy + Issue report
**Process:**

**If Docs-First:**
1. Generate doc updates first:
   - Update `docs/requirements/` or `docs/design/` with new behavior
   - Follow existing doc structure and conventions
2. Generate code changes:
   - Implement changes to match updated docs
   - Follow `docs/standards/coding-standards.md`

**If Code-Only:**
1. Generate code fix directly:
   - Apply minimal changes to fix the issue
   - Ensure no behavior change
2. Verify no doc updates needed

**Commit Message Format:**
```
fix(skill): <short description>

Affected: <list of changed files>

<Optional: reference to doc changes>
```

**Outputs:**
- Files to commit: `{ doc_files: [...], code_files: [...] }`
- Commit message

**Why:** Maintain traceability and follow project conventions.

---

### Step 4: Create PR

**Inputs:** Committed changes + Issue report
**Process:**
1. Create branch: `fix/skill-<skill-name>-<timestamp>`
2. Push branch to remote
3. Create PR using `gh pr create`:
   - Title: First line of commit message
   - Body: Use template below
4. Return PR URL to user

**PR Body Template:**
```markdown
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
```

**Outputs:**
- PR URL

**Why:** Provide full context for human review.

---

### Step 5: User Review & Merge

**Process:** (Manual by user)
1. User reviews PR on GitHub
2. Checks verification steps
3. Merges PR if approved

**Why:** Human oversight required (see requirements NFR1.2).

---

### Step 6: Auto-Reload Skill (Optional)

**Inputs:** `skill_path` (same as Step 1)
**Process:**
1. Run `git pull origin main` in live DailyHub instance
2. Notify user with agent-appropriate reload instructions:
   - OpenClaw: `openclaw reload <skill_path>`
   - Claude Code: Auto-reloads on file change
   - Generic: "Skill updated. Please reload your agent."

**Outputs:**
- Reload instructions

**Why:** Simplify post-merge workflow. Instructions adapt to user's agent.

---

## Error Handling Strategy

### Category 1: Prerequisites Errors (Step 0)

| Error | Detection | Action |
|-------|----------|--------|
| `gh` not installed | `gh --version` fails | Ask user: "Install gh from https://cli.github.com" |
| `gh` not authenticated | `gh auth status` shows not logged in | Return error: "Run: `gh auth login`" |
| Git config missing | `git config user.name` empty | Return error: "Configure git user.name/email" |

**Principle:** Fail fast before cloning/analyzing.

---

### Category 2: Analysis Errors (Step 1)

| Error | Detection | Action |
|-------|----------|--------|
| Skill path not found | Directory doesn't exist | Suggest corrections, list similar paths |
| No issues detected | Heuristics find nothing | Return "No issues found" (not an error) |
| Cannot understand issue | Issue description too vague | Request more details from user |

**Principle:** Clarify before proceeding.

---

### Category 3: Fix Generation Errors (Step 3)

| Error | Detection | Action |
|-------|----------|--------|
| Cannot generate fix | AI unsure how to fix | Save analysis, request user guidance |
| Fix requires new dependencies | Detected new imports | Note in PR body, flag for manual review |
| Secrets detected | Regex match for API keys/tokens | Block commit, alert user |

**Principle:** Safety over automation.

---

### Category 4: Git/PR Errors (Step 4)

| Error | Detection | Action |
|-------|----------|--------|
| Push fails | Remote rejects push | Check permissions, retry once |
| PR creation fails | `gh pr create` errors | Log error, provide manual PR link |
| Branch conflict | Branch name exists | Append `-retry-<N>` suffix |

**Principle:** Graceful degradation; provide manual fallback.

---

## Configuration

### Prerequisites

1. **GitHub CLI (`gh`)**: Must be installed and authenticated
   ```bash
   gh auth login
   ```

2. **Git Config**: Must have user.name and user.email configured
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your@example.com"
   ```

### Runtime Parameters

| Parameter | Source | Default | Notes |
|-----------|--------|---------|-------|
| `repo_url` | User prompt | None | Ask user for their repo URL |
| `skill_path` | User input | None | Required |
| `issue_description` | User input | None | Optional; use heuristics if missing |

**Note:** Never hardcode repository URLs. Always prompt user.

---

## Usage Examples

### Example 1: Fix Xiaoju Check-in Auth Issue

```bash
# Invoke the self-optimize skill (exact command depends on your AI agent)
# For example, in a conversation with your AI agent:
"My xiaoju check-in is failing with 401 Unauthorized. Can you use self-optimize to fix it?"

# The skill will handle:
# - Locating the skill path automatically
# - Prompting for repo_url if needed

# Output:
# [INFO] Checking prerequisites...
# [SUCCESS] gh authenticated, git configured
# [INFO] Cloning repository...
# [INFO] Analyzing issue: Check-in fails with 401 Unauthorized
# [INFO] Issue type: api_deprecated (requires docs update)
# [INFO] Updating docs/design/api-integrations.md...
# [INFO] Updating src/checkin.py...
# [INFO] Creating PR...
# [SUCCESS] PR created: https://github.com/user/DailyHub/pull/123
# [INFO] Please review and merge.
```

### Example 2: Prerequisites Not Ready

```bash
# User invokes self-optimize (via natural language to their AI agent)
"Can you optimize the xiaoju check-in skill?"

# Output:
# [INFO] Checking prerequisites...
# [ERROR] gh CLI not authenticated
# [ERROR] Please run: gh auth login
# [INFO] Aborting. Run this skill again after authentication.
```

### Example 3: No Issue Found

```bash
$ openclaw run routine/self-optimize/skill/SKILL.md \
  --input skill_path="routine/ai-morning/skill/daily-news/"

# Output:
# [INFO] Checking prerequisites...
# [SUCCESS] gh authenticated, git configured
# [INFO] Cloning repository...
# [INFO] Analyzing skill: routine/ai-morning/skill/daily-news/
# [INFO] No issues detected
# [INFO] Skill appears healthy. No action taken.
```

---

## Security Considerations

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

## Open Questions

1. **Q:** Support auto-merge for trivial fixes (typos)?
   **A:** No, not in V1. All PRs require human review.

2. **Q:** Handle concurrent PRs?
   **A:** Use timestamp in branch names. User merges in order.

3. **Q:** Require external dependencies (new packages)?
   **A:** Out of scope for V1. Flag in PR for manual review.

---

## Future Enhancements

1. **Proactive Monitoring:** Daily scan for issues without user input
2. **Batch Fixes:** Fix similar issues across multiple skills in one PR
3. **AI Test Generation:** Generate unit tests for fixed code
4. **Auto-Merge:** Auto-merge low-risk fixes after CI passes

---

_Last updated: 2026-03-14_
