# Self-Optimize Skill - Requirements

## Overview

A meta-skill that enables DailyHub to self-improve by detecting issues in existing skills and automatically creating pull requests with fixes.

## Problem Statement

Currently, when skills fail or need optimization:
- Manual intervention is required to identify the issue
- Code changes must be done outside the DailyHub runtime
- The fix-test-deploy cycle is slow and manual

## Objective

Create a skill that can:
1. Clone the DailyHub repository
2. Create a feature branch
3. Analyze and fix issues in existing skills
4. Follow project conventions (CLAUDE.md rules)
5. Submit a PR for human review
6. After PR merge, pull the updated skill to replace the running version

## Scope

### In Scope

**Skills covered by self-optimization:**
- `checkin/xiaojuchongdian/skill/overall/` - Xiaoju Charging entry
- `checkin/xiaojuchongdian/skill/checkin/` - Xiaoju check-in execution
- `checkin/xiaojuchongdian/skill/get-params/` - Xiaoju auth guidance
- `routine/ai-morning/skill/daily-news/` - AI daily news
- `routine/ai-morning/skill/frontier-changelog/` - Frontier changelog
- `routine/ai-morning/skill/morning-publish/` - Morning publish
- `routine/ai-morning/skill/ai-daily-news-and-changelog/` - Combined news and changelog

**Operations:**
- Bug fixes in SKILL.md logic
- Python implementation fixes (`src/` directories)
- Improvement of error handling
- Update of outdated APIs or parameters
- Documentation synchronization

### Out of Scope

- Architecture changes (require human design)
- Adding new platforms (not self-optimization)
- Changes to `CLAUDE.md` core rules
- Automated merge (must wait for human review)

## Functional Requirements

### FR1: Repository Management
- **FR1.1**: Clone `git@github.com:ZHOUKAILIAN/DailyHub.git` to a temporary workspace
- **FR1.2**: Create feature branch with naming: `fix/skill-<platform>-<timestamp>`
- **FR1.3**: Configure git user for commits

### FR2: Issue Detection
- **FR2.1**: Accept skill path as input (e.g., `checkin/xiaojuchongdian/skill/checkin/`)
- **FR2.2**: Read skill definition (SKILL.md) and implementation (src/)
- **FR2.3**: Identify issues:
  - Runtime errors from logs
  - Deprecated API endpoints
  - Missing error handling
  - Documentation-code mismatch

### FR3: Fix Implementation
- **FR3.1**: Follow documentation-first workflow (CLAUDE.md):
  - Update or create docs in `docs/requirements/` and `docs/design/` if needed
  - Then modify code
- **FR3.2**: Apply fixes to SKILL.md and/or Python code
- **FR3.3**: Follow coding standards in `docs/standards/`
- **FR3.4**: Run verification (if skill has tests)

### FR4: Pull Request Creation
- **FR4.1**: Commit changes with descriptive message
- **FR4.2**: Push branch to GitHub
- **FR4.3**: Create PR with:
  - Title: `fix(skill): <brief description>`
  - Body: issue description, changes made, verification steps
  - Label: `self-optimize`
- **FR4.4**: Notify user (via PR link)

### FR5: Skill Update (Post-Merge)
- **FR5.1**: After PR merge, pull latest main branch
- **FR5.2**: Identify updated skill paths
- **FR5.3**: Reload skill in OpenClaw runtime (implementation-dependent)

## Non-Functional Requirements

### NFR1: Safety
- **NFR1.1**: Never force-push to main
- **NFR1.2**: Never auto-merge PRs (human review required)
- **NFR1.3**: Create branch from latest main
- **NFR1.4**: Rollback if any step fails critically

### NFR2: Traceability
- **NFR2.1**: Log all operations (clone, branch, commit, push)
- **NFR2.2**: PR must reference the original error/issue
- **NFR2.3**: Commit messages must reference changed files

### NFR3: Performance
- **NFR3.1**: Complete fix cycle (clone to PR) within 5 minutes
- **NFR3.2**: Use shallow clone to reduce bandwidth

### NFR4: Compliance
- **NFR4.1**: Must follow CLAUDE.md workflow (docs first)
- **NFR4.2**: Must follow commit guidelines
- **NFR4.3**: Must not commit secrets

## Acceptance Criteria

### AC1: Successful Fix Cycle
```
GIVEN a skill with a known bug (e.g., xiaoju check-in fails)
WHEN the self-optimize skill is invoked with that skill path
THEN:
  - A new branch is created
  - Relevant files are updated
  - A PR is created on GitHub
  - PR contains clear description of fix
  - User receives PR link for review
```

### AC2: Documentation Compliance
```
GIVEN a fix that changes behavior
WHEN the PR is created
THEN:
  - Relevant docs in docs/requirements/ or docs/design/ are updated
  - Commit message references doc files
```

### AC3: Post-Merge Update
```
GIVEN a merged PR with skill fixes
WHEN the update step is triggered
THEN:
  - Latest main branch is pulled
  - Updated skill files are identified
  - Skill is reloaded (or instructions provided)
```

### AC4: Error Handling
```
GIVEN any step fails (e.g., git push fails)
WHEN the error occurs
THEN:
  - Clear error message is logged
  - Temporary workspace is cleaned up
  - User is notified with actionable error
```

## User Stories

### US1: Developer - Fix Runtime Error
```
AS A developer
WHEN a skill fails at runtime
I WANT to invoke the self-optimize skill with the failing skill path
SO THAT a PR with the fix is automatically created for my review
```

### US2: Maintainer - Update Outdated API
```
AS A maintainer
WHEN an external API changes
I WANT the self-optimize skill to detect and update the API calls
SO THAT I can review and merge the fix without manual coding
```

### US3: User - Apply Approved Fix
```
AS A user
WHEN a self-optimize PR is merged
I WANT the skill to automatically update in my DailyHub instance
SO THAT the fix is immediately active
```

## Dependencies

- Git installed and configured
- GitHub CLI (`gh`) for PR creation
- SSH key for `git@github.com:ZHOUKAILIAN/DailyHub.git`
- Python environment for running tests (if applicable)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Incorrect fix breaks skill | High | Require human review before merge |
| PR conflicts with concurrent changes | Medium | Use latest main, document conflict resolution |
| Skill reload fails | Medium | Provide manual reload instructions |
| Git auth fails | High | Pre-check SSH key, clear error messages |

## Future Enhancements (Out of Scope for V1)

- Auto-detect issues without user input (proactive monitoring)
- Multi-skill batch fixes
- AI-driven test generation
- Auto-merge for trivial fixes (typos, formatting)
