---
name: personal-market-brief
description: Analyze three personal macro assets (CSI 300, Hong Kong dividend exposure, and gold) with a compact trend/risk snapshot and allocation-friendly interpretation. Use when user asks for quick recurring analysis of 沪深300、港股红利、黄金, or wants a personal daily/weekly market brief.
---

# Personal Market Brief

Run the bundled script to generate a compact snapshot for the three default assets.

## Default assets
- CSI 300: `000300.SS`
- HK Dividend proxy: `3110.HK`
- Gold: `GC=F`

## Command
```bash
uv run {baseDir}/scripts/brief.py
```

## Optional overrides
```bash
uv run {baseDir}/scripts/brief.py \
  --csi300 000300.SS \
  --hkdiv 3110.HK \
  --gold GC=F \
  --period 6mo
```

## Output rules
- Report per asset: latest price, 1D/5D/20D return, MA20/MA60 trend, 20D annualized volatility.
- Add a short interpretation section:
  - Risk-on if equities up and gold flat/down.
  - Risk-off if equities weak and gold strong.
  - Mixed otherwise.
- Keep the final summary short and actionable for personal tracking.
