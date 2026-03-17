#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "yfinance>=0.2.40",
#   "pandas>=2.0.0",
# ]
# ///

import argparse
import json
from dataclasses import dataclass, asdict
import pandas as pd
import yfinance as yf


@dataclass
class AssetBrief:
    name: str
    ticker: str
    last: float
    ret_1d: float
    ret_5d: float
    ret_20d: float
    ma20: float
    ma60: float
    trend: str
    vol20_ann: float


def pct(a, b):
    if b == 0 or pd.isna(a) or pd.isna(b):
        return 0.0
    return (a / b - 1.0) * 100.0


def analyze(name: str, ticker: str, period: str) -> AssetBrief:
    df = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
    if df.empty or "Close" not in df:
        raise RuntimeError(f"No data for {ticker}")

    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.dropna()
    if len(close) < 65:
        raise RuntimeError(f"Not enough data for {ticker}")

    last = float(close.iloc[-1])
    ret_1d = pct(close.iloc[-1], close.iloc[-2])
    ret_5d = pct(close.iloc[-1], close.iloc[-6])
    ret_20d = pct(close.iloc[-1], close.iloc[-21])

    ma20 = float(close.tail(20).mean())
    ma60 = float(close.tail(60).mean())
    trend = "up" if (last > ma20 > ma60) else "down" if (last < ma20 < ma60) else "mixed"

    vol20 = close.pct_change().dropna().tail(20).std()
    vol20_ann = float(vol20 * (252 ** 0.5) * 100)

    return AssetBrief(
        name=name,
        ticker=ticker,
        last=round(last, 3),
        ret_1d=round(ret_1d, 2),
        ret_5d=round(ret_5d, 2),
        ret_20d=round(ret_20d, 2),
        ma20=round(ma20, 3),
        ma60=round(ma60, 3),
        trend=trend,
        vol20_ann=round(vol20_ann, 2),
    )


def regime(csi: AssetBrief, hk: AssetBrief, gold: AssetBrief) -> str:
    eq_score = (1 if csi.ret_20d > 0 else -1) + (1 if hk.ret_20d > 0 else -1)
    gold_score = 1 if gold.ret_20d > 0 else -1
    if eq_score > 0 and gold_score < 0:
        return "risk-on"
    if eq_score < 0 and gold_score > 0:
        return "risk-off"
    return "mixed"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csi300", default="000300.SS")
    p.add_argument("--hkdiv", default="3110.HK")
    p.add_argument("--gold", default="GC=F")
    p.add_argument("--period", default="6mo")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    assets = [
        ("沪深300", args.csi300),
        ("港股红利", args.hkdiv),
        ("黄金", args.gold),
    ]

    briefs = [analyze(n, t, args.period) for n, t in assets]
    r = regime(briefs[0], briefs[1], briefs[2])

    out = {
        "regime": r,
        "assets": [asdict(b) for b in briefs],
    }

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    print("个人三资产快照")
    print(f"市场状态: {r}")
    for b in briefs:
        print(
            f"- {b.name}({b.ticker}): 最新 {b.last}, 1D {b.ret_1d:+.2f}%, 5D {b.ret_5d:+.2f}%, 20D {b.ret_20d:+.2f}%, "
            f"趋势 {b.trend} (MA20 {b.ma20} / MA60 {b.ma60}), 年化波动20D {b.vol20_ann:.2f}%"
        )


if __name__ == "__main__":
    main()
