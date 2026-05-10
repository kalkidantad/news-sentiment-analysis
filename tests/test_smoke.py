"""Smoke checks so CI validates the Python environment."""

from pathlib import Path


def test_core_imports():
    import matplotlib  # noqa: F401
    import numpy  # noqa: F401
    import pandas  # noqa: F401
    import seaborn  # noqa: F401
    import sklearn  # noqa: F401


def test_sample_news_exists():
    csv_path = Path(__file__).resolve().parents[1] / "data" / "raw" / "sample_news.csv"
    assert csv_path.is_file(), "Bundled sample should exist for reproducible EDA"
