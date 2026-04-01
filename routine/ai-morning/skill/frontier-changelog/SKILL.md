---
name: frontier-changelog
description: Track frontier AI IDE/CLI and model updates daily.
---

# Frontier Changelog Tracking

## Goal

Gather the latest updates from frontier AI coding tools and major model releases, favor recall so important updates are not missed, and output a full changelog report that clearly separates confirmed updates from lower-confidence findings.

## IDE/CLI Sources

| Tool           | Changelog URL |
|----------------|---------------|
| Claude Code    | `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` |
| Codex          | `https://developers.openai.com/codex/changelog` |
| Cursor         | `https://cursor.com/changelog` |
| Gemini CLI     | `https://google-gemini.github.io/gemini-cli/docs/changelogs/` |
| Antigravity    | `https://antigravity.google/changelog` |
| OpenCode       | `https://opencode.ai/changelog` |

Rules:
- Use the fixed official URL list above first.
- `web_fetch` for these fixed URLs may run in parallel.
- Any `web_search` or fallback investigation must remain sequential.
- If the official page is reachable but only yields navigation, TOC, shell content, or obviously incomplete text, you may use one fallback source to recover the actual latest entry — but still cite the official source first and explain the fallback reason.

## Model Updates

Search for major AI model releases and capability changes (for example OpenAI, Anthropic, Google, Meta, xAI, Mistral) within the time window.

Rules:
- Model-update searches should remain sequential.
- Prefer official announcements, official changelogs, official release notes, or official product pages.
- If no official source yields readable evidence, do not fabricate certainty; downgrade confidence instead.

## Time Window

Default window: **yesterday 09:00 → today 09:00** (Beijing time, UTC+8).

Rules:
- Convert source timestamps to the Beijing-time window before deciding inclusion.
- If a source only provides a date without a specific time, and that date is either yesterday or today in Beijing time, keep it as a candidate to avoid misses.
- Date-only evidence should not be silently treated as fully certain if the exact in-window time cannot be proven.

## Evidence Quality and Verdict Tiers

For every IDE/CLI tool and every model item, produce one structured verdict.

### Evidence Quality

- `high`: clear changelog/release body with enough detail and a reliable date/time signal
- `medium`: readable substantive update exists, but time precision or extraction quality is incomplete
- `low`: weak evidence only (navigation page, shell page, partial extraction, or indirect evidence)

### Verdict Tiers

- `confirmed_in_window`: substantive update confirmed to be within the target window
- `likely_in_window`: likely within the target window, included to avoid misses, but evidence is incomplete
- `found_but_out_of_window`: a latest update was found, but it is outside the target window
- `source_unreadable`: official source failed, was unreadable, or only yielded shell/navigation/insufficient content

Rules:
- Favor recall, but never hide uncertainty.
- Weak or incomplete evidence may enter `likely_in_window`, but must not be presented as `confirmed_in_window`.
- If the latest visible item is older than the time window, report it as `found_but_out_of_window` rather than pretending there was no finding.

## Per-Source Evaluation Requirements

For each tool/model, report at least:
1. `latest_candidate` — the newest update entry you found
2. `source_link` — at least one source URL
3. `evidence_quality` — high / medium / low
4. `window_verdict` — one of the 4 verdict tiers above
5. `short_reason` — why it was classified that way

For Codex specifically:
- Distinguish `Codex CLI` and `Codex app` when the source mixes both.
- If the official Codex page is mostly navigation or documentation chrome, use one fallback to recover the actual latest changelog content, and explain that the fallback was needed.

## Output

Return the full changelog report directly.

Recommended structure:
1. **Status Overview**
   - SUCCESS / PARTIAL / NO_UPDATES
2. **Confirmed In-Window Updates**
   - only items with `confirmed_in_window`
3. **Likely In-Window Updates**
   - items with `likely_in_window`, clearly labeled as lower confidence
4. **Found But Out of Window**
   - items with `found_but_out_of_window`
5. **Unreadable / Failed Sources**
   - items with `source_unreadable`
6. **Per-Tool / Per-Model Detail**
   - include latest_candidate, evidence_quality, window_verdict, short_reason, and source_link

## Summary Consistency Rule

The final summary must be generated from the same per-source verdicts listed above.
Do not let the front section say an update was found while the final summary says `no_updates` for the same source.
If a source produced only an out-of-window item, summarize it under `found_but_out_of_window`, not under confirmed updates.

## Failure Policy

- If one source fails, continue with the rest.
- If an official source is reachable but unreadable, classify it as `source_unreadable` instead of over-claiming.
- If evidence is incomplete but still plausibly relevant to the time window, prefer `likely_in_window` over dropping it.
- If all sources fail or only unreadable shells are available, return `NO_UPDATES` or `PARTIAL` with the reasons visible in the report.
