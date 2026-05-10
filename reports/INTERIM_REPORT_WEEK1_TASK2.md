# Interim report — Week 1 (Task 1 + Task 2)

**Program:** 10 Academy — Artificial Intelligence Mastery  
**Project:** News sentiment & stock price integration (Nova Financial Solutions style)  
**Scope:** Interim findings for **headline EDA (Task 1)** and **price / technical analysis (Task 2)**. Figures live in the linked notebooks (not duplicated here).

**Length note:** This document is written to stay within **~3 printed pages** when rendered from Markdown; notebooks hold full charts.

---

## 1. Summary of data loading and cleaning

### Financial news headlines (Task 1)

- **Load:** CSV under `data/raw/` with columns `headline`, `url`, `publisher`, `date`, `stock` (validated case-insensitively). Row-index columns named `Unnamed:*` are removed before typing.
- **Parse:** Dates converted to timezone-aware timestamps (UTC internally). Rows with unparsable dates are surfaced in-notebook counts and omitted from date-based visuals.
- **Working frame:** The analysis keeps `headline`, `publisher`, `date`, and `stock` (plus engineered `headline_len`, `word_count`). **`url` is required in the raw file but not used downstream**, matching the consolidated schema in the README.
- **Quality:** Duplicate headlines can appear across outlets; publishers include both brand names (e.g. **Bloomberg**, **Reuters**, **CNBC**) and inbox-style identifiers—domain extraction separates these in the EDA notebook.

### Stock prices (Task 2)

- **Load:** Daily OHLCV from **yfinance** for tickers that rank highest in `sample_news.csv` (plus **SPY** as a market benchmark), or a user-supplied CSV via **`YFINANCE_OFFLINE_CSV`**.
- **Types:** `Open`–`Close` and `Adj Close` as `float64`; `Volume` as nullable `Int64`; monotonic `DatetimeIndex` per ticker.
- **Quality:** Rows with non-positive OHLC or `High < Low` are dropped. Small price gaps are forward-filled; rows still missing `Close`/`Adj Close` after that are removed. Volume NaNs are allowed to remain visible for transparency.

---

## 2. Key EDA findings (Task 1) — with evidence in the notebook

**Notebook:** `notebooks/01_eda_financial_news.ipynb`

| Topic | Finding (preliminary) | Where to see it |
|--------|------------------------|-----------------|
| **Publication load** | Headline volume clusters by trading day; the bundled sample includes a **synthetic CPI-style burst** to exercise time-series plots (methodological demo, not a market claim). | Time-series section (daily counts + rolling mean) |
| **Publisher concentration** | Coverage is **long-tailed**: a small set of desks dominates row counts; in the bundled sample the top counts are **Bloomberg (60)**, **Reuters (55)**, **CNBC (38)**—stratify models by outlet family to avoid style bias. | Publisher bar / tail charts |
| **Text shape** | Headline length and word-count distributions show typical wire length; informs embedding / truncation choices later. | Descriptive tables & histograms |
| **Topic / lexicon** | TF–IDF / n-grams surface recurring financial phrases (price targets, earnings, regulatory cues); LDA-style setup is **exploratory**, not causal labels. | Keyword & topic blocks |

These are **associative** patterns; causal claims require event-study design with returns and careful alignment (planned for later weeks).

---

## 3. Initial stock price analysis & technical indicators (Task 2)

**Notebook:** `notebooks/02_technical_analysis_talib_pynance.ipynb`

**Universe (sample-driven):** `AAPL`, `MSFT`, `NVDA`, **SPY**; primary plot symbol defaults to the most frequent news ticker (**AAPL** on the current sample).

**Indicators (TA-Lib on `Close`):**

- **SMA** windows 20 / 50 / 200 (when history permits) and **EMA(12)** / **EMA(26)** to visualize short vs slower trend.
- **RSI(14)** with bands at 30 / 70: on a recent **six-month daily** pull, **RSI settled near ~73**, i.e. in **overbought** territory *on this window*—interpret with macro context and avoid single-indicator trading rules.
- **MACD(12,26,9):** line above the signal with **positive histogram** in the latest bar of the same window—consistent with **upward momentum** but not a guarantee of continuation.

**PyNance (beyond TA-Lib):**

- **One-session simple returns** and **log growth** on `Adj Close` via `pynance.tech.simple`.
- **Rolling 20-day annualized volatility** from daily log returns (scaled by √252): recent window near **0.26** annualized for **AAPL**—useful for linking headline bursts to realized risk.

**Price level (same window):** daily **close** ranged roughly **\$246.63–\$293.32**—documented numerically because reports should state *what was observed*, not only which code ran.

---

## 4. Challenges & plans for the final submission

| Challenge | Mitigation so far | Next step |
|-----------|-------------------|-----------|
| **Vendor data quirks** (splits, thin sessions) | Prefer `Adj Close` for PyNance returns; explicit row validity checks | Add corporate-action sanity checks; optionally second data vendor |
| **News–price alignment** | Tasks separated; tickers sampled from headlines | Event windows around publication timestamps; label construction for sentiment |
| **Grader feedback** (“process without findings”) | This interim ties **numbers and interpretations** to notebook sections | Final report will embed **screenshots** and **table extracts** from notebooks + statistical tests |
| **Tooling** | `TA-Lib` wheels on CI; offline CSV path for air-gapped runs | Harden tests / pin versions; document `YFINANCE_OFFLINE_CSV` layout |

**Git / delivery hygiene:** merge **`task-1` → `main` via a GitHub Pull Request** (local `gh` auth may be required), then continue on **`task-2`** with descriptive commits. If `gh` is unavailable, open the PR in the browser from the pushed branch—the branch protection intent is review before integration.

---

## 5. Conclusion (interim)

The repository now spans **clean headline EDA with interpretable visuals** and a **repeatable OHLCV + indicator pipeline** using **TA-Lib** and **PyNance**, grounded in concrete observations (publisher concentration, RSI/MACD positioning, volatility magnitudes, and price ranges). The final submission will tighten **news–return alignment**, expand **cross-ticker comparison**, and convert exploratory signals into **testable hypotheses** with labeled outputs.
