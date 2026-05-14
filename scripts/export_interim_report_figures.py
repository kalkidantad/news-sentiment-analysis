#!/usr/bin/env python3
"""Regenerate PNGs for reports/INTERIM_REPORT_WEEK1_TASK2.md — run from repo root."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def fig_eda_publishers(news_path: Path, out_dir: Path) -> None:
    df = pd.read_csv(news_path)
    top = df["publisher"].astype(str).value_counts().head(12)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    top.sort_values().plot(kind="barh", ax=ax, color="#2563eb")
    ax.set_title("Headline counts by publisher (top 12)\nSource: data/raw/sample_news.csv")
    ax.set_xlabel("Rows")
    plt.tight_layout()
    fig.savefig(out_dir / "eda_publisher_counts.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_eda_daily_volume(news_path: Path, out_dir: Path) -> None:
    df = pd.read_csv(news_path)
    dt = pd.to_datetime(df["date"], utc=True, errors="coerce")
    d = df.assign(d=dt.dt.floor("D")).dropna(subset=["d"])
    daily = d.groupby("d").size().rename("headlines").sort_index()
    fig, ax = plt.subplots(figsize=(7, 3.5))
    daily.plot(ax=ax, color="#0f766e", linewidth=1.2, label="Daily headlines")
    daily.rolling(7, min_periods=1).mean().plot(ax=ax, color="#c2410c", linewidth=1.5, label="7D rolling mean")
    ax.set_title("Publication intensity over time (bundled sample)")
    ax.set_ylabel("Headlines per day")
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    fig.savefig(out_dir / "eda_daily_headlines.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_price_with_ma(ohlc: pd.DataFrame, ticker: str, out_dir: Path) -> None:
    import talib

    close = ohlc["Close"].values.astype(np.float64)
    ohlc = ohlc.copy()
    for w in (20, 50):
        if len(close) >= w:
            ohlc[f"SMA{w}"] = talib.SMA(close, timeperiod=w)
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    ax.plot(ohlc.index, ohlc["Close"], label="Close", color="#1f2937", linewidth=1.1)
    for c in ("SMA20", "SMA50"):
        if c in ohlc:
            ax.plot(ohlc.index, ohlc[c], label=c, alpha=0.85, linewidth=1.0)
    ax.set_title(f"{ticker} — Close with TA-Lib SMAs (yfinance daily)")
    ax.set_ylabel("USD")
    ax.legend(loc="upper left", ncol=3, fontsize=8)
    plt.tight_layout()
    fig.savefig(out_dir / "price_close_sma.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_rsi_macd(ohlc: pd.DataFrame, ticker: str, out_dir: Path) -> None:
    import talib

    close = ohlc["Close"].values.astype(np.float64)
    rsi = talib.RSI(close, timeperiod=14)
    macd, sig, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 5.2), sharex=True, gridspec_kw={"height_ratios": [1, 1]})
    axes[0].plot(ohlc.index, rsi, color="#2563eb", linewidth=1)
    axes[0].axhline(70, color="red", linestyle="--", linewidth=0.8)
    axes[0].axhline(30, color="green", linestyle="--", linewidth=0.8)
    axes[0].set_ylabel("RSI(14)")
    axes[0].set_ylim(0, 100)
    axes[0].set_title(f"{ticker} — RSI(14) vs 30/70 reference bands")
    axes[1].plot(ohlc.index, macd, label="MACD", color="#0f766e")
    axes[1].plot(ohlc.index, sig, label="Signal", color="#c2410c")
    axes[1].bar(ohlc.index, hist, width=1.0, label="Hist", color="#94a3b8")
    axes[1].set_ylabel("MACD")
    axes[1].legend(ncol=3, fontsize=8, loc="upper left")
    axes[1].set_title("MACD(12,26,9)")
    plt.tight_layout()
    fig.savefig(out_dir / "price_rsi_macd.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def _fetch_ohlc(repo: Path, ticker: str, period: str = "1y") -> pd.DataFrame | None:
    try:
        import yfinance as yf
    except ImportError:
        return None
    raw = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=False)
    if raw.empty:
        return None
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [str(c[0]).strip() for c in raw.columns.values]
    else:
        raw.columns = [str(c).strip() for c in raw.columns]
    raw = raw.rename(
        columns={
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
            "Adj Close": "Adj Close",
            "Volume": "Volume",
        }
    )
    idx = pd.to_datetime(raw.index, utc=True)
    out = raw.copy()
    out.index = idx
    bad = (out[["Open", "High", "Low", "Close"]] <= 0).any(axis=1) | (out["High"] < out["Low"])
    out = out.loc[~bad]
    for c in ["Open", "High", "Low", "Close", "Adj Close"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out[["Open", "High", "Low", "Close", "Adj Close"]] = out[["Open", "High", "Low", "Close", "Adj Close"]].ffill()
    out = out.dropna(subset=["Close"])
    return out


def main() -> int:
    plt.style.use("seaborn-v0_8-whitegrid")
    repo = Path(__file__).resolve().parents[1]
    news = repo / "data" / "raw" / "sample_news.csv"
    out_dir = repo / "reports" / "figures"
    _ensure_dir(out_dir)

    if not news.is_file():
        print("Missing", news, file=sys.stderr)
        return 1

    fig_eda_publishers(news, out_dir)
    fig_eda_daily_volume(news, out_dir)

    focus = (
        pd.read_csv(news)["stock"]
        .astype(str)
        .str.upper()
        .value_counts()
        .head(1)
        .index[0]
    )
    ohlc = _fetch_ohlc(repo, focus, period="1y")
    if ohlc is not None and len(ohlc) > 30:
        fig_price_with_ma(ohlc, focus, out_dir)
        fig_rsi_macd(ohlc, focus, out_dir)
        print("Wrote figures to", out_dir, "| focus ticker", focus)
    else:
        print("yfinance OHLC unavailable — EDA figures only; re-run online to add price charts.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
