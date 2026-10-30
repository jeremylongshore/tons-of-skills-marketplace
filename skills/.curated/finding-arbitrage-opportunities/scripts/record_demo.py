#!/usr/bin/env python3
"""
Maintainer tool: refresh the bundled demo recording from live public data.

Runs the demo commands through one recording client (one clock), trims OKX's
full spot ticker list to assets that have a USDT market with at least
TRIM_VOLUME_USD of 24-hour volume (every triangle the default volume floor can
form is kept), and writes ../assets/demo-recording.json. `--demo` replays it.

Usage:
    python record_demo.py
"""

from __future__ import annotations

import contextlib
import io
import json

import arb_finder
from http_client import Http

DEMO_COMMANDS = [
    ["scan", "BTC", "USDT"],
    ["scan", "ETH", "USD"],
    ["triangular", "okx"],
]
TRIM_VOLUME_USD = 1_000_000
STABLES = {"USDT", "USDC", "USD"}


def trim(responses: dict) -> None:
    for key, entry in responses.items():
        if "market/tickers?instType=SPOT" not in key or entry.get("body") is None:
            continue
        rows = entry["body"]["data"]
        liquid = {
            r["instId"].split("-")[0]
            for r in rows
            if r["instId"].endswith("-USDT") and float(r.get("volCcy24h") or 0) >= TRIM_VOLUME_USD
        }
        keep = liquid | STABLES
        entry["body"]["data"] = [r for r in rows if set(r["instId"].split("-")) <= keep]


def main() -> int:
    http = Http(record_path=arb_finder.DEMO_RECORDING)
    for argv in DEMO_COMMANDS:
        with contextlib.redirect_stdout(io.StringIO()):
            arb_finder.main(argv + ["--format", "json"], http=http)
    trim(http._recorded)
    http.write_recording(
        note=(
            "Real public API responses, recorded in one run: BTC/USDT and ETH/USD top of book on every "
            "venue, and OKX spot tickers trimmed to assets with a USDT market of at least "
            f"${TRIM_VOLUME_USD:,} 24h volume. Replayed by --demo; not live data."
        )
    )
    doc = json.loads(arb_finder.DEMO_RECORDING.read_text())
    print(f"wrote {arb_finder.DEMO_RECORDING} ({len(doc['responses'])} responses, recorded {doc['recorded_at']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
