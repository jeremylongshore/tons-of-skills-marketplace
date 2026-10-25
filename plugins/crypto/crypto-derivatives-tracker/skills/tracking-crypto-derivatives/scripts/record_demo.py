#!/usr/bin/env python3
"""
Maintainer tool: refresh the bundled demo recording from live public data.

Runs every tracker command for BTC through one recording client (one clock),
trims the two large Deribit payloads to what the demo commands display, and
writes ../assets/demo-recording.json. `--demo` replays that file.

Usage:
    python record_demo.py
"""

from __future__ import annotations

import contextlib
import io
import json
from datetime import datetime, timezone

import derivatives_tracker as tracker
from http_client import Http

DEMO_COMMANDS = [
    ["funding", "BTC"],
    ["oi", "BTC"],
    ["options", "BTC", "--large-trades", "1000000"],
    ["basis", "BTC"],
    ["liquidations", "BTC"],
    ["dashboard", "BTC"],
]
KEEP_EXPIRIES = 6
KEEP_TRADE_NOTIONAL_USD = 250_000
# Fields the options parser reads; the rest of each row is dropped from the recording.
OPTION_FIELDS = ("instrument_name", "open_interest", "volume", "mark_iv", "underlying_price")
TRADE_FIELDS = ("timestamp", "instrument_name", "direction", "amount", "price", "index_price", "iv", "block_trade_id")


def trim(responses: dict, now: datetime) -> None:
    for key, entry in responses.items():
        body = entry.get("body")
        if body is None:
            continue
        if "get_book_summary_by_currency" in key and "kind=option" in key:
            rows = body["result"]
            expiries = sorted(
                {r["instrument_name"].split("-")[1] for r in rows},
                key=lambda c: datetime.strptime(c, "%d%b%y"),
            )
            live = [c for c in expiries if datetime.strptime(c, "%d%b%y").replace(hour=8, tzinfo=timezone.utc) > now]
            keep = set(live[:KEEP_EXPIRIES])
            body["result"] = [
                {f: r.get(f) for f in OPTION_FIELDS} for r in rows if r["instrument_name"].split("-")[1] in keep
            ]
        elif "get_last_trades_by_currency" in key:
            trades = body["result"]["trades"]
            body["result"]["trades"] = [
                {f: t[f] for f in TRADE_FIELDS if f in t}
                for t in trades
                if float(t["amount"]) * float(t["index_price"]) >= KEEP_TRADE_NOTIONAL_USD
            ]
        elif "metaAndAssetCtxs" in key:
            meta, ctxs = body
            keep_idx = [i for i, u in enumerate(meta["universe"]) if u["name"] == "BTC"]
            meta["universe"] = [meta["universe"][i] for i in keep_idx]
            entry["body"] = [meta, [ctxs[i] for i in keep_idx]]


def main() -> int:
    http = Http(record_path=tracker.DEMO_RECORDING)
    for argv in DEMO_COMMANDS:
        with contextlib.redirect_stdout(io.StringIO()):
            tracker.main(argv + ["--format", "json"], http=http)
    trim(http._recorded, http.now())
    http.write_recording(
        note=(
            "Real public API responses for BTC, recorded in one run. Trimmed to what the demo "
            f"commands read: Deribit option summaries to the {KEEP_EXPIRIES} nearest expiries and the "
            f"fields used, option trades to notional >= ${KEEP_TRADE_NOTIONAL_USD:,}, Hyperliquid to BTC. "
            "Replayed by --demo; not live data."
        )
    )
    doc = json.loads(tracker.DEMO_RECORDING.read_text())
    print(f"wrote {tracker.DEMO_RECORDING} ({len(doc['responses'])} responses, recorded {doc['recorded_at']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
