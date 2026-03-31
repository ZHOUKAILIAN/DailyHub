---
name: personal-market-brief
description: Analyze three personal macro assets (CSI 300, Hong Kong dividend exposure, and gold) with a compact trend/risk snapshot and allocation-friendly interpretation. Use when user asks for quick recurring analysis of 沪深300、港股红利、黄金, or wants a personal daily/weekly market brief.
---

# Personal Market Brief

## Goal

Generate a compact snapshot for three default assets (沪深300、港股红利、黄金), assess the current market regime (risk-on / risk-off / mixed), and provide a short actionable interpretation for personal tracking.

## Default Assets

- CSI 300: `000300.SS`
- HK Dividend proxy: `3110.HK`
- Gold: `GC=F`

## Available Tools

Python script in `scripts/` directory. Read `brief.py` to understand usage, supported arguments, and output format.

## Output Guidelines

- Present per-asset metrics as reported by the script.
- Add a short interpretation section:
  - Risk-on if equities up and gold flat/down.
  - Risk-off if equities weak and gold strong.
  - Mixed otherwise.
- Keep the final summary short and actionable for personal tracking.
