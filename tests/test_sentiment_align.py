"""Unit tests for NYSE next-session alignment (no network)."""

import datetime as dt

from news_price_correlation import align_to_next_trading_day


def test_weekend_aligns_to_next_monday():
    cal = [dt.date(2024, 1, 2), dt.date(2024, 1, 3), dt.date(2024, 1, 8)]
    assert align_to_next_trading_day(dt.date(2024, 1, 6), cal) == dt.date(2024, 1, 8)


def test_trading_day_unchanged():
    cal = [dt.date(2024, 1, 2), dt.date(2024, 1, 3)]
    assert align_to_next_trading_day(dt.date(2024, 1, 3), cal) == dt.date(2024, 1, 3)


def test_after_last_session_returns_none():
    cal = [dt.date(2024, 1, 2), dt.date(2024, 1, 3)]
    assert align_to_next_trading_day(dt.date(2099, 1, 1), cal) is None


def test_empty_calendar():
    assert align_to_next_trading_day(dt.date(2024, 1, 1), []) is None
