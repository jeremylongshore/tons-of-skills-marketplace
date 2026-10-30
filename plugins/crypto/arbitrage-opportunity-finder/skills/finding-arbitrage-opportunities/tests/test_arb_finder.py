#!/usr/bin/env python3
"""
Offline tests for the arbitrage finder.

They replay recorded real API responses (assets/demo-recording.json and
tests/fixtures/binance-bybit-recording.json) through the same parsers the
live tool uses, plus hand-built quotes for the spread arithmetic.

Run: python3 -m unittest discover -s tests -v   (from the skill directory)
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import arb_finder  # noqa: E402
import spot_venues  # noqa: E402
import spreads  # noqa: E402
from http_client import FetchError, Http, Recording  # noqa: E402

DEMO = Recording.load(SKILL_DIR / "assets" / "demo-recording.json")
BINANCE_BYBIT = Recording.load(SKILL_DIR / "tests" / "fixtures" / "binance-bybit-recording.json")
NOW = datetime(2026, 10, 25, 16, 0, tzinfo=timezone.utc)


def replay(responses: dict, status: dict | None = None) -> Http:
    status = status or {}
    return Http(replay=Recording(NOW, {k: {"status": status.get(k, 200), "body": v} for k, v in responses.items()}))


def run_cli(argv, http: Http):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = arb_finder.main(argv, http=http)
    return code, buf.getvalue()


def quote(venue, bid, ask, fee, bid_size=1.0, ask_size=1.0):
    return spot_venues.Quote(venue, "BTC/USDT", "X", bid, ask, bid_size, ask_size, fee, "test", 0.0, "test")


class TestSpreadMath(unittest.TestCase):
    def test_gross_and_net(self):
        buy = quote("a", 99.0, 100.0, 0.1)
        sell = quote("b", 101.0, 101.5, 0.2)
        s = spreads.CrossSpread(buy, sell)
        self.assertAlmostEqual(s.gross_pct, 1.0)
        expected = (101.0 * (1 - 0.002) / (100.0 * (1 + 0.001)) - 1) * 100
        self.assertAlmostEqual(s.net_pct, expected)

    def test_unknown_fee_gives_no_net(self):
        s = spreads.CrossSpread(quote("a", 99, 100, None), quote("b", 101, 102, 0.1))
        self.assertIsNone(s.net_pct)

    def test_size_is_the_smaller_side(self):
        s = spreads.CrossSpread(quote("a", 99, 100, 0.1, ask_size=0.3), quote("b", 101, 102, 0.1, bid_size=2.0))
        self.assertAlmostEqual(s.top_size, 0.3)

    def test_every_ordered_pair_is_ranked(self):
        qs = [quote("a", 99, 100, 0.1), quote("b", 100.5, 101, 0.1), quote("c", 98, 99, 0.1)]
        ranked = spreads.cross_spreads(qs)
        self.assertEqual(len(ranked), 6)
        self.assertEqual((ranked[0].buy.venue, ranked[0].sell.venue), ("c", "b"))

    def test_overlapping_books_are_described_plainly(self):
        notes = spreads.describe(spreads.cross_spreads([quote("a", 99, 100, 0.1), quote("b", 99.5, 100.5, 0.1)]))
        self.assertIn("books overlap", notes[0])


class TestTriangles(unittest.TestCase):
    def test_triangle_rates_use_bid_to_sell_and_ask_to_buy(self):
        http = replay(
            {
                "GET https://www.okx.com/api/v5/market/tickers?instType=SPOT": {
                    "code": "0",
                    "data": [
                        {"instId": "BTC-USDT", "bidPx": "100", "askPx": "100", "volCcy24h": "1e9"},
                        {"instId": "ETH-BTC", "bidPx": "0.1", "askPx": "0.1", "volCcy24h": "1e9"},
                        {"instId": "ETH-USDT", "bidPx": "10.1", "askPx": "10.1", "volCcy24h": "1e9"},
                    ],
                }
            }
        )
        found, evaluated, _ = spreads.find_triangles(http, "okx", "USDT", 0.0, 0, 10)
        best = found[0]
        # USDT -> BTC (1/100) -> ETH (1/0.1) -> USDT (10.1) = 1.01
        self.assertEqual(best.path, ("USDT", "BTC", "ETH", "USDT"))
        self.assertAlmostEqual(best.gross_pct, 1.0)
        self.assertEqual(evaluated, 2)

    def test_fee_applies_to_three_legs(self):
        http = replay(
            {
                "GET https://www.okx.com/api/v5/market/tickers?instType=SPOT": {
                    "code": "0",
                    "data": [
                        {"instId": "BTC-USDT", "bidPx": "100", "askPx": "100", "volCcy24h": "1e9"},
                        {"instId": "ETH-BTC", "bidPx": "0.1", "askPx": "0.1", "volCcy24h": "1e9"},
                        {"instId": "ETH-USDT", "bidPx": "10", "askPx": "10", "volCcy24h": "1e9"},
                    ],
                }
            }
        )
        found, _, _ = spreads.find_triangles(http, "okx", "USDT", 0.1, 0, 10)
        self.assertAlmostEqual(found[0].net_pct, ((1 - 0.001) ** 3 - 1) * 100)


class TestDemoRecording(unittest.TestCase):
    def test_scan_replays_and_marks_every_line(self):
        for argv in (["scan", "BTC", "USDT"], ["scan", "ETH", "USD"], ["triangular", "okx"]):
            code, text = run_cli(argv, Http(replay=DEMO))
            self.assertEqual(code, 0, argv)
            for line in text.splitlines():
                self.assertTrue(line.startswith("[DEMO]"), f"{argv}: {line!r}")

    def test_quotes_are_sane(self):
        quotes, failures = spot_venues.fetch_quotes(Http(replay=DEMO), "BTC", "USDT")
        self.assertGreaterEqual(len(quotes), 5)
        for q in quotes:
            self.assertGreater(q.bid, 0)
            self.assertGreaterEqual(q.ask, q.bid)
            self.assertLess(abs(q.mid / quotes[0].mid - 1), 0.01, q.venue)  # same pair, same price
        for f in failures:
            self.assertRegex(f.reason, r"HTTP (451|403)")

    def test_quote_assets_are_never_mixed(self):
        quotes, _ = spot_venues.fetch_quotes(Http(replay=DEMO), "ETH", "USD")
        self.assertTrue(all(q.pair == "ETH/USD" for q in quotes))

    def test_json_envelope(self):
        code, text = run_cli(["scan", "BTC", "USDT", "--format", "json"], Http(replay=DEMO))
        doc = json.loads(text)
        for key in ("skill", "version", "command", "generated_at", "mode", "sources", "failures", "data", "disclaimer"):
            self.assertIn(key, doc)
        self.assertEqual(doc["mode"], "demo")
        self.assertIn("withdrawal", doc["not_included"])

    def test_demo_rejects_unrecorded_requests(self):
        self.assertEqual(arb_finder.main(["scan", "SOL", "USDT", "--demo"]), 2)
        self.assertEqual(arb_finder.main(["monitor", "BTC", "USDT", "--demo"]), 2)


class TestVenues(unittest.TestCase):
    def test_binance_and_bybit_parse(self):
        http = Http(replay=BINANCE_BYBIT)
        b = spot_venues.fetch_quote(http, "binance", "BTC", "USDT", {})
        self.assertAlmostEqual(b.bid, 80624.0)
        self.assertEqual(b.taker_fee_pct, 0.10)
        y = spot_venues.fetch_quote(http, "bybit", "BTC", "USDT", {})
        self.assertGreater(y.ask, y.bid)

    def test_binance_unlisted_symbol_is_not_listed(self):
        with self.assertRaisesRegex(FetchError, "not listed"):
            spot_venues.fetch_quote(Http(replay=BINANCE_BYBIT), "binance", "NOPE", "USDT", {})

    def test_bitfinex_error_body_means_not_listed(self):
        url = "GET https://api-pub.bitfinex.com/v2/ticker/tNOPE:UST"
        http = replay({url: ["error", 10020, "symbol: invalid"]}, {url: 500})
        with self.assertRaisesRegex(FetchError, "not listed"):
            spot_venues.fetch_quote(http, "bitfinex", "NOPE", "USDT", {})

    def test_fee_override_wins(self):
        q = spot_venues.fetch_quote(Http(replay=BINANCE_BYBIT), "binance", "BTC", "USDT", {"binance": 0.075})
        self.assertEqual(q.taker_fee_pct, 0.075)
        self.assertEqual(q.fee_source, "set with --fee")

    def test_unconfirmed_fees_stay_unknown(self):
        self.assertIsNone(spot_venues.FEES["kucoin"].taker_pct)
        self.assertIsNone(spot_venues.FEES["coinbase"].taker_pct)

    def test_documented_fee_table_matches_code(self):
        """references/implementation.md must state the same fee as spot_venues.FEES for every venue."""
        names = {
            "Kraken": "kraken",
            "OKX": "okx",
            "Binance": "binance",
            "Bybit": "bybit",
            "Bitfinex": "bitfinex",
            "Crypto.com": "cryptocom",
            "Gate": "gate",
            "KuCoin": "kucoin",
            "Coinbase": "coinbase",
        }
        doc = (SKILL_DIR / "references" / "implementation.md").read_text()
        section = doc.split("## Fee assumptions", 1)[1].split("\n## ", 1)[0]
        documented = {}
        for line in section.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] in names:
                documented[names[cells[0]]] = cells[1]
        self.assertEqual(set(documented), set(spot_venues.FEES))
        for venue, assumption in spot_venues.FEES.items():
            if venue == "gate":
                expected = "live"
            elif assumption.taker_pct is None:
                expected = "unknown"
            else:
                expected = f"{assumption.taker_pct:.2f}%".replace(".00%", "%")
            self.assertEqual(documented[venue], expected, venue)

    def test_fee_parsing_rejects_nonsense(self):
        self.assertEqual(arb_finder.parse_fees(["okx=0.1,kraken=0.26"]), {"okx": 0.1, "kraken": 0.26})
        with self.assertRaises(SystemExit):
            arb_finder.parse_fees(["okx=25"])
        with self.assertRaises(SystemExit):
            arb_finder.parse_fees(["nowhere=0.1"])


class TestReadOnly(unittest.TestCase):
    FORBIDDEN = re.compile(
        r"/trade/|/orders?(?![a-z])|/account[/?]|/asset/|/withdraw|private/|/v5/position|"
        r"api[_-]?secret|api[_-]?key|signature|hmac",
        re.IGNORECASE,
    )

    def test_no_private_endpoints_or_signing_in_scripts(self):
        for path in (SKILL_DIR / "scripts").glob("*.py"):
            match = self.FORBIDDEN.search(path.read_text())
            self.assertIsNone(match, f"{path.name}: {match}")

    def test_no_post_requests(self):
        for path in (SKILL_DIR / "scripts").glob("*.py"):
            if path.name == "http_client.py":
                continue
            self.assertNotIn("post_json(", path.read_text(), path.name)


if __name__ == "__main__":
    unittest.main()
