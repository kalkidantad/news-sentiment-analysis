#!/usr/bin/env python3
"""Task 3: VADER sentiment, NYSE session alignment, daily returns, Pearson r, figures."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
_SRC = _REPO / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from news_price_correlation import (  # noqa: E402
    aggregate_daily_sentiment,
    fetch_us_equity_close_by_ny_date,
    merge_news_returns,
    pearson_corr,
    vader_compound_scores,
)


def _ensure_nltk_vader() -> None:
    import nltk

    nltk.download("vader_lexicon", quiet=True)


def _plot_scatter(panel: pd.DataFrame, r: float, p: float, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(panel["avg_sentiment"], panel["daily_return_pct"], alpha=0.55, edgecolors="none", s=42, c="#2563eb")
    ax.axvline(0, color="#94a3b8", linewidth=0.8, linestyle="--")
    ax.axhline(0, color="#94a3b8", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Average daily VADER compound sentiment")
    ax.set_ylabel("Daily return (% vs prior close)")
    ax.set_title("News sentiment vs same-session stock return (stock–day observations)")
    txt = f"Pearson r = {r:.3f}\np-value = {p:.3g}\nn = {len(panel)}"
    ax.text(0.02, 0.98, txt, transform=ax.transAxes, fontsize=10, verticalalignment="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.9))
    plt.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _plot_category_bars(panel: pd.DataFrame, out: Path) -> None:
    order = ["negative", "neutral", "positive"]
    g = panel.groupby("sentiment_category")["daily_return_pct"].mean().reindex(order).dropna()
    counts = panel.groupby("sentiment_category").size().reindex(order)
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    colors = {"negative": "#b91c1c", "neutral": "#64748b", "positive": "#15803d"}
    x = np.arange(len(g))
    bars = ax.bar(x, g.values, color=[colors.get(str(i), "#334155") for i in g.index], width=0.65)
    ax.set_xticks(x)
    ax.set_xticklabels([str(i).title() for i in g.index])
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_ylabel("Mean daily return (% vs prior close)")
    ax.set_title("Mean return by average-daily sentiment category (VADER ±0.05 compound)")
    for i, b in enumerate(bars):
        cat = g.index[i]
        n = int(counts.get(cat, 0)) if not pd.isna(counts.get(cat, np.nan)) else 0
        ax.annotate(f"n={n}", xy=(b.get_x() + b.get_width() / 2, b.get_height()), ha="center", va="bottom" if b.get_height() >= 0 else "top", fontsize=9)
    plt.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--news",
        type=Path,
        default=None,
        help="Normalized news CSV (default: data/newdata/news_normalized.csv)",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=None,
        help="PNG output directory (default: reports/figures)",
    )
    parser.add_argument(
        "--panel-out",
        type=Path,
        default=None,
        help="Optional CSV path for stock–day panel (default: data/newdata/task3_stock_day_panel.csv)",
    )
    parser.add_argument("--root", type=Path, default=None, help="Project root (default: parent of scripts/)")
    args = parser.parse_args()
    root = args.root.resolve() if args.root else _REPO
    news_path = args.news or (root / "data" / "newdata" / "news_normalized.csv")
    fig_dir = args.figures_dir or (root / "reports" / "figures")
    panel_out = args.panel_out if args.panel_out is not None else (root / "data" / "newdata" / "task3_stock_day_panel.csv")

    if not news_path.is_file():
        print("Missing news CSV:", news_path, file=sys.stderr)
        return 1

    plt.style.use("seaborn-v0_8-whitegrid")
    fig_dir.mkdir(parents=True, exist_ok=True)

    news = pd.read_csv(news_path)
    news["date"] = pd.to_datetime(news["date"], utc=True, errors="coerce")
    news = news.dropna(subset=["date", "headline", "stock"])
    news["stock"] = news["stock"].astype(str).str.upper()

    _ensure_nltk_vader()
    from nltk.sentiment import SentimentIntensityAnalyzer

    sid = SentimentIntensityAnalyzer()
    news["sentiment_compound"] = vader_compound_scores(news["headline"], sid)

    dmin = news["date"].min().date()
    dmax = news["date"].max().date()
    tickers = sorted(news["stock"].unique())
    close_by: dict[str, pd.Series] = {}
    for t in tickers:
        s = fetch_us_equity_close_by_ny_date(t, dmin, dmax)
        if s is not None and len(s) > 2:
            close_by[t] = s
        else:
            print("Warning: no usable OHLC for", t, file=sys.stderr)

    merged = merge_news_returns(news, close_by)
    if merged.empty:
        print("No merged rows (check tickers vs yfinance).", file=sys.stderr)
        return 1

    panel = aggregate_daily_sentiment(merged)
    panel = panel.dropna(subset=["daily_return_pct", "avg_sentiment"])
    if panel.empty:
        print("Empty panel after dropna.", file=sys.stderr)
        return 1

    r, p = pearson_corr(panel["avg_sentiment"].values, panel["daily_return_pct"].values)

    _plot_scatter(panel, r, p, fig_dir / "task3_scatter_sentiment_vs_return.png")
    _plot_category_bars(panel, fig_dir / "task3_bar_return_by_sentiment_category.png")

    panel_out.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(panel_out, index=False)

    print("Stock–day observations:", len(panel))
    print("Pearson r (avg sentiment vs daily return %):", f"{r:.4f}", "| p =", f"{p:.4g}")
    print("Wrote:", fig_dir / "task3_scatter_sentiment_vs_return.png")
    print("Wrote:", fig_dir / "task3_bar_return_by_sentiment_category.png")
    print("Wrote:", panel_out)

    print("\nPer-ticker Pearson (same-day avg sentiment vs return):")
    for t in sorted(panel["stock"].unique()):
        sub = panel[panel["stock"] == t]
        if len(sub) < 3:
            continue
        rt, pt = pearson_corr(sub["avg_sentiment"].values, sub["daily_return_pct"].values)
        print(f"  {t}: r={rt:.3f} p={pt:.3g} n={len(sub)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
