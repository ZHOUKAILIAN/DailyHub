---
name: daily-news
description: Run the daily AI news workflow by invoking an existing external capability (e.g. daily-intelligence-news).
---

# AI Daily News Skill

## Purpose

Use this skill exclusively to fetch the morning AI daily news. It delegates the content generation to an existing skill or capability provided by third parties, ensuring stability and single responsibility.

## External Capability

- Capability name: `daily-intelligence-news`
- Reference link: `https://openclawmp.cc/asset/s-027065c89db7e63f`
- Style guard reference: `https://tropes.fyi/tropes-md`
- Policy:
  - If capability already exists in local/runtime environment, use it directly.
  - If missing, install it first via `skill-installer`, then continue.
  - Do not use URL lookup as runtime execution logic; treat the link as reference metadata.
  - When invoking `daily-intelligence-news`, include a style constraint to avoid common AI writing tropes from `tropes.md` while preserving factual accuracy and markdown structure.

## Execution Flow

1. Confirm `daily-intelligence-news` is available locally (installed skill/capability). If missing, install it first via `skill-installer`.
2. Invoke the externally provided `daily-intelligence-news` capability to retrieve the latest AI news, and explicitly request anti-trope writing style (based on `tropes.md`) without changing facts.
3. If configured or requested, publish the report to Xiaohongshu via an available local publishing capability.
4. **CRITICAL**: Present the exact Markdown content of the news report to the user in the prompt output.

## Output Format

Return a human-readable report summarizing:
1. Execution status (SUCCESS, FAILED).
2. The complete Markdown body of the daily AI news. **Do not summarize it; output the full text.**

## Failure Policy
- If the external news capability fails: stop execution, report the error, and do not make up news.
- If publishing fails: report the failure but still output the generated news text to the user.
