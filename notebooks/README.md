# Notebooks

- `01_eda_financial_news.ipynb` — Task 1 exploratory analysis: descriptive stats on headlines, topical structure (`CountVectorizer` / TF-IDF / LDA-ready features), publishing time trends, publisher concentration.
- `02_technical_analysis_talib_pynance.ipynb` — Task 2: download or load offline OHLCV, clean types and gaps, **TA-Lib** (SMA, EMA, RSI, MACD) and **PyNance** (returns / log growth; rolling volatility), multi-panel plots.

**Data:** resolves which CSV to read in notebook 01 (see repo **README → Data**, including `EDA_NEWS_PATH`). Notebook 02 uses `yfinance` by default (`YFINANCE_OFFLINE_CSV` for offline CSV).

**Kernel:** repo **README → Environment** (`TA-Lib` ships binary wheels on many platforms; legacy installs may still need the system `ta-lib` C library—see TA-Lib project docs).
