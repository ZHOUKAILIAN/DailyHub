---
name: morning-publish
description: Custom skill to gather outputs from the daily-news and frontier-changelog skills, merge them via a strict template, and publish them to Blog (PR) and Xiaohongshu.
---

# Morning Publish Skill

## Purpose

Use this skill strictly to merge the output results from `daily-news` and `frontier-changelog` into a single, unified markdown document and distribute it.

## Required Inputs
- Task A Content: The generated AI Daily News markdown string.
- Task B Content: The generated IDE/CLI & Model Changelog markdown string.
- (Optional) Destination configurations for Blog PR and Xiaohongshu.
- Xiaohongshu API installation guide (if needed): `https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md`

## Execution Flow

1. Capture the content of the `daily-news` and `frontier-changelog` runs from the context or parameters.
2. Merge the two contents using EXACTLY the following template structure:
   ```markdown
   AI 日报
   [Task A Content Here]

   IDE/CLI changelog
   [Task B Content Here]
   ```
3. Use the unified markdown document to create a Blog file and submit a PR.
4. Pass the exact unified markdown document to the Xiaohongshu publishing API.
5. Treat request dispatch as completion for Xiaohongshu (no retry, no response-content validation).
6. Provide a summary of semantic completion to the user.

## Output Format

Return a human-readable report summarizing:
1. Overall distribution status (SUCCESS, PARTIAL, FAILED).
2. The final **merged Markdown document** in full.
3. PR Link (if applicable) and Xiaohongshu publishing status.

## Failure Policy
- If PR submission fails, log the error but proceed to XHS publishing.
- XHS side only guarantees request dispatch; no extra retry or post-validation.
