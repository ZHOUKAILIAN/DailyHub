---
name: morning-publish
description: Custom skill to gather outputs from the daily-news and frontier-changelog skills, merge them via a strict template, and publish them to Blog PR only.
---

# Morning Publish Skill

## Purpose

Use this skill strictly to merge the output results from `daily-news` and `frontier-changelog` into a single, unified markdown document and distribute it.

## Required Inputs
- Task A Content: The generated AI Daily News markdown string.
- Task B Content: The generated IDE/CLI & Model Changelog markdown string.
- (Optional) Destination configurations for Blog PR.

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
4. Do not publish to Xiaohongshu.
5. Provide a summary of semantic completion to the user.

## Output Format

Return a human-readable report summarizing:
1. Overall distribution status (SUCCESS, PARTIAL, FAILED).
2. The final **merged Markdown document** in full.
3. PR Link (if applicable).

## Failure Policy
- If PR submission fails, log the error and return FAILED/PARTIAL with clear reason.
