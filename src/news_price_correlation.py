"""Align news to NYSE session dates, score headlines (VADER), merge with daily returns."""

from __future__ import annotations

import datetime as dt
from bisect import bisect_left
from collections.abc import Sequence

import numpy as np
import pandas as pd

NYSE_TZ = "America/New_York"
# VADER-recommended polarity bands for compound scores (short social/financial text).
VADER_POS = 0.05
VADER_NEG = -0.05


def ny_calendar_date(ts: pd.Timestamp | str | float) -> dt.date:
    """Publication instant in UTC → calendar date in America/New_York."""
    t = pd.Timestamp(ts)
    if t.tzinfo is None:
        t = t.tz_localize("UTC")
    else:
        t = t.tz_convert("UTC")
    return t.tz_convert(NYSE_TZ).date()


def align_to_next_trading_day(
    pub_date: dt.date,
    trading_days_sorted: Sequence[dt.date],
) -> dt.date | None:
    """If ``pub_date`` is not a session, use the first session on or after it (NYSE-style)."""
    if not trading_days_sorted:
        return None
    i = bisect_left(trading_days_sorted, pub_date)
    if i >= len(trading_days_sorted):
        return None
    return trading_days_sorted[i]


def daily_close_and_returns(
    close: pd.Series,
) -> tuple[pd.Series, pd.Series]:
    """Daily close indexed by NY calendar date; pct return vs prior close (*100)."""
    close = close.sort_index()
    dates = close.index
    ret = close.astype(float).pct_change() * 100.0
    ret = pd.Series(ret.values, index=dates, name="daily_return_pct")
    return close, ret


def sentiment_category(compound: float | pd.Series) -> str | pd.Series:
    """Map VADER compound to positive / neutral / negative (lexicon defaults)."""
    if isinstance(compound, pd.Series):
        s = compound.astype(float)
        return pd.Series(
            np.where(s >= VADER_POS, "positive", np.where(s <= VADER_NEG, "negative", "neutral")),
            index=s.index,
        )
    if compound >= VADER_POS:
        return "positive"
    if compound <= VADER_NEG:
        return "negative"
    return "neutral"


def vader_compound_scores(headlines: pd.Series, analyzer) -> np.ndarray:
    """Compound polarity in [-1, 1] for each headline (``analyzer``: VADER SID)."""
    out = np.empty(len(headlines), dtype=np.float64)
    for i, h in enumerate(headlines.astype(str).values):
        out[i] = float(analyzer.polarity_scores(h)["compound"])
    return out


def build_stock_trading_calendar(close_by_ny_date: pd.Series) -> list[dt.date]:
    return sorted(close_by_ny_date.index.tolist())  # type: ignore[arg-type]


def merge_news_returns(
    news: pd.DataFrame,
    close_by_ticker: dict[str, pd.Series],
) -> pd.DataFrame:
    """
    ``news`` must include: headline, stock, date (UTC-aware ok).
    ``close_by_ticker[t]`` = Close indexed by NY session ``datetime.date``.
    """
    rows: list[dict] = []
    for ticker, close_s in close_by_ticker.items():
        if close_s is None or close_s.empty:
            continue
        cal = build_stock_trading_calendar(close_s)
        _, rets = daily_close_and_returns(close_s)
        sub = news[news["stock"].astype(str).str.upper() == ticker.upper()].copy()
        if sub.empty:
            continue
        sub["ny_pub_date"] = sub["date"].map(ny_calendar_date)
        sub["session_date"] = sub["ny_pub_date"].map(lambda d: align_to_next_trading_day(d, cal))
        sub = sub.dropna(subset=["session_date"])
        # attach same-day return for that session
        sub["daily_return_pct"] = sub["session_date"].map(lambda d: rets.get(d, np.nan))
        rows.append(sub)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def aggregate_daily_sentiment(merged: pd.DataFrame) -> pd.DataFrame:
    """One row per (stock, session_date) with mean compound and mean return."""
    g = merged.groupby(["stock", "session_date"], as_index=False).agg(
        avg_sentiment=("sentiment_compound", "mean"),
        n_headlines=("sentiment_compound", "size"),
        daily_return_pct=("daily_return_pct", "mean"),
    )
    g["sentiment_category"] = sentiment_category(g["avg_sentiment"])
    return g


def pearson_corr(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    from scipy import stats

    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2:
        return float("nan"), float("nan")
    r, p = stats.pearsonr(x[mask], y[mask])
    return float(r), float(p)


def fetch_us_equity_close_by_ny_date(
    ticker: str,
    start_calendar: dt.date,
    end_calendar: dt.date,
) -> pd.Series | None:
    """
    Daily ``Close`` indexed by NY session calendar date (``datetime.date``).
    Pads the window so the first news session still has a prior close for returns.
    """
    import yfinance as yf

    start_pad = pd.Timestamp(start_calendar) - pd.Timedelta(days=45)
    end_pad = pd.Timestamp(end_calendar) + pd.Timedelta(days=7)
    raw = yf.download(
        ticker,
        start=start_pad.strftime("%Y-%m-%d"),
        end=(end_pad + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
        interval="1d",
        progress=False,
        auto_adjust=False,
    )
    if raw.empty:
        return None
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [str(c[0]).strip() for c in raw.columns.values]
    close = pd.to_numeric(raw["Close"], errors="coerce")
    idx = pd.DatetimeIndex(raw.index)
    if idx.tz is None:
        idx = idx.tz_localize("UTC")
    else:
        idx = idx.tz_convert("UTC")
    ny_dates = idx.tz_convert(NYSE_TZ).date
    ser = pd.Series(close.values, index=ny_dates, name="close")
    ser = ser.groupby(ser.index).last().sort_index()
    ser = ser.loc[ser.astype(float) > 0]
    return ser.astype(float)
