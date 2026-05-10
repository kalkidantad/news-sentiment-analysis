# Scripts

Use this folder for **CLI helpers** (downloads, batch ETL, feature builds)—run them from the repository root (`python scripts/<name>.py`) so imports and paths resolve.

- **`raw_to_newdata.py`** — read an FNSPID-style CSV from `data/raw` (same resolution rules as notebook 01), write normalized columns under `data/newdata/` (`news_normalized.csv` by default).

Add new scripts beside notebooks/modules as pipelines grow.
