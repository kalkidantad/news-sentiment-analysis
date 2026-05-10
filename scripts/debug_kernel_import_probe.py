#!/usr/bin/env python3
"""Time each heavy import; append NDJSON to .cursor/debug-499ffa.log. Run: .venv/bin/python scripts/debug_kernel_import_probe.py"""

from __future__ import annotations

# region agent log
import json
import time
from pathlib import Path

_LOG = Path(__file__).resolve().parents[1] / ".cursor" / "debug-499ffa.log"
_SESSION = "499ffa"


def _log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    line = json.dumps(
        {
            "sessionId": _SESSION,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
            "runId": "import-probe",
        },
        ensure_ascii=False,
    )
    _LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# endregion


def main() -> None:
    t0 = time.perf_counter()
    _log("H3", "probe:main", "probe_start", {"context": "terminal_subprocess"})

    def timed(hid: str, name: str, fn):
        t = time.perf_counter()
        fn()
        _log(hid, f"probe:{name}", "import_done", {"seconds": round(time.perf_counter() - t, 4)})

    timed("H1", "matplotlib.pyplot", lambda: __import__("matplotlib.pyplot"))
    timed("H1", "numpy", lambda: __import__("numpy"))
    timed("H1", "pandas", lambda: __import__("pandas"))
    timed("H1", "talib", lambda: __import__("talib"))
    timed("H1", "yfinance", lambda: __import__("yfinance"))
    timed("H1", "pynance", lambda: __import__("pynance"))

    t_style = time.perf_counter()
    import matplotlib.pyplot as plt

    plt.style.use("seaborn-v0_8-whitegrid")
    _log("H2", "probe:plt.style", "style_applied", {"seconds": round(time.perf_counter() - t_style, 4)})

    _log("H3", "probe:main", "probe_total", {"seconds": round(time.perf_counter() - t0, 4)})
    print("Wrote timings to", _LOG)


if __name__ == "__main__":
    main()
