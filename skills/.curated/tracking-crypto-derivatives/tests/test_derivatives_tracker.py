#!/usr/bin/env python3
"""
Offline tests for the derivatives tracker.

They replay recorded real API responses (assets/demo-recording.json and
tests/fixtures/binance-bybit-recording.json) through the same parsers the
live tool uses, plus small hand-built payloads for unit conversions.

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

import basis_data  # noqa: E402
import derivatives_tracker as tracker  # noqa: E402
import liquidations  # noqa: E402
import options_data  # noqa: E402
import perps  # noqa: E402
from http_client import FetchError, Http, Recording  # noqa: E402

DEMO = Recording.load(SKILL_DIR / "assets" / "demo-recording.json")
BINANCE_BYBIT = Recording.load(SKILL_DIR / "tests" / "fixtures" / "binance-bybit-recording.json")
NOW = datetime(2026, 10, 25, 16, 0, tzinfo=timezone.utc)


def replay(responses: dict) -> Http:
    """Http that serves hand-built payloads."""
    return Http(replay=Recording(NOW, {k: {"status": 200, "body": v} for k, v in responses.items()}))


def run_cli(argv, http: Http):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = tracker.main(argv, http=http)
    return code, buf.getvalue()


class TestDemoRecording(unittest.TestCase):
    def test_every_default_venue_is_accounted_for(self):
        snaps, failures = perps.fetch_all(Http(replay=DEMO), "BTC")
        seen = {s.venue for s in snaps} | {f.venue for f in failures}
        self.assertEqual(seen, set(perps.VENUES))
        self.assertGreaterEqual(len(snaps), 5)

    def test_refused_venues_are_reported_not_invented(self):
        _, failures = perps.fetch_all(Http(replay=DEMO), "BTC")
        for failure in failures:
            self.assertRegex(failure.reason, r"HTTP (451|403)")

    def test_funding_values_are_in_a_plausible_range(self):
        snaps, _ = perps.fetch_all(Http(replay=DEMO), "BTC")
        for s in snaps:
            # Venue caps sit near 0.3-0.4% per 8h; anything beyond 1% means a unit error.
            self.assertLess(abs(s.rate_8h), 0.01, s.venue)
            self.assertGreater(s.oi_usd, 0, s.venue)

    def test_every_console_line_is_marked_demo(self):
        for argv in (
            ["funding", "BTC"],
            ["oi", "BTC"],
            ["basis", "BTC"],
            ["liquidations", "BTC"],
            ["dashboard", "BTC"],
        ):
            code, text = run_cli(argv, Http(replay=DEMO))
            self.assertEqual(code, 0, argv)
            for line in text.splitlines():
                self.assertTrue(line.startswith("[DEMO]"), f"{argv}: {line!r}")

    def test_json_envelope(self):
        code, text = run_cli(["funding", "BTC", "--format", "json"], Http(replay=DEMO))
        self.assertEqual(code, 0)
        doc = json.loads(text)
        for key in ("skill", "version", "command", "generated_at", "mode", "sources", "failures", "data", "disclaimer"):
            self.assertIn(key, doc)
        self.assertEqual(doc["mode"], "demo")
        self.assertTrue(doc["sources"])
        self.assertIn("places no trades", doc["disclaimer"])

    def test_options_from_recording(self):
        report = options_data.build_report(Http(replay=DEMO), "BTC", trades_min_usd=1_000_000)
        self.assertTrue(report.expiries)
        for e in report.expiries:
            self.assertGreater(e.underlying_price, 0)
            self.assertGreater(e.max_pain, 0)
            self.assertLess(abs(e.atm_strike / e.underlying_price - 1), 0.05)
            if e.atm_iv is not None:
                self.assertTrue(5 < e.atm_iv < 300)
        self.assertIsNotNone(report.dvol)
        self.assertTrue(0 <= report.dvol.percentile_365d <= 100)
        for t in report.trades:
            self.assertGreaterEqual(t.notional_usd, 1_000_000)

    def test_basis_and_liquidations_from_recording(self):
        points, _ = basis_data.fetch_all(Http(replay=DEMO), "BTC")
        self.assertTrue(points)
        self.assertTrue(all(p.days_to_expiry > 0.5 for p in points))
        report = liquidations.fetch(Http(replay=DEMO), "BTC")
        self.assertGreater(len(report.orders), 0)
        self.assertLessEqual(report.window_end, DEMO.recorded_at)

    def test_demo_rejects_other_symbols(self):
        code = tracker.main(["funding", "ETH", "--demo"])
        self.assertEqual(code, 2)


class TestBinanceBybit(unittest.TestCase):
    """Real responses recorded from a network these venues serve."""

    def test_binance_parse(self):
        s = perps.fetch_binance(Http(replay=BINANCE_BYBIT), "BTC")
        self.assertEqual(s.interval_hours, 8.0)  # BTCUSDT absent from fundingInfo means the default
        self.assertAlmostEqual(s.funding_rate, 0.00007998)
        self.assertAlmostEqual(s.oi_base, 93562.649)

    def test_bybit_uses_single_side_open_interest(self):
        s = perps.fetch_bybit(Http(replay=BINANCE_BYBIT), "BTC")
        self.assertAlmostEqual(s.oi_base, 31323.011)  # not the both-sides 62646.021
        self.assertEqual(s.interval_hours, 8.0)

    def test_history_and_ratios(self):
        changes, ratios, failures = perps.fetch_positioning(Http(replay=BINANCE_BYBIT), "BTC", ["binance", "bybit"])
        self.assertEqual(failures, [])
        self.assertEqual({c.venue for c in changes}, {"binance", "bybit"})
        for c in changes:
            self.assertLess(abs(c.change_pct), 50)
        for r in ratios:
            self.assertTrue(0 < r.long_accounts_pct < 100)


class TestUnits(unittest.TestCase):
    def test_hourly_rate_scales_to_eight_hours(self):
        http = replay(
            {
                "GET https://futures.kraken.com/derivatives/api/v3/tickers/PF_XBTUSD": {
                    "result": "success",
                    "ticker": {
                        "relativeFundingRate": 1e-5,
                        "markPrice": 80000,
                        "indexPrice": 80000,
                        "openInterest": 10,
                    },
                }
            }
        )
        s = perps.fetch_kraken(http, "BTC")
        self.assertAlmostEqual(s.rate_8h, 8e-5)
        self.assertAlmostEqual(s.annualized_pct, 1e-5 * 8760 * 100)
        self.assertAlmostEqual(s.oi_usd, 800_000)

    def test_gate_open_interest_is_long_side_times_multiplier(self):
        http = replay(
            {
                "GET https://api.gateio.ws/api/v4/futures/usdt/contracts/BTC_USDT": {
                    "funding_rate": "0.0001",
                    "funding_interval": 28800,
                    "funding_next_apply": 1792972800,
                    "mark_price": "80000",
                    "index_price": "80000",
                    "position_size": 20000,
                    "quanto_multiplier": "0.0001",
                }
            }
        )
        self.assertAlmostEqual(perps.fetch_gate(http, "BTC").oi_base, 2.0)

    def test_deribit_inverse_open_interest_converts_from_usd(self):
        http = replay(
            {
                "GET https://www.deribit.com/api/v2/public/ticker?instrument_name=BTC-PERPETUAL": {
                    "result": {
                        "mark_price": 80000,
                        "index_price": 80000,
                        "open_interest": 8_000_000,
                        "funding_8h": 1e-4,
                    }
                }
            }
        )
        s = perps.fetch_deribit(http, "BTC")
        self.assertAlmostEqual(s.oi_base, 100)
        self.assertAlmostEqual(s.oi_usd, 8_000_000)

    def test_unlisted_symbol_is_a_failure_not_a_value(self):
        http = replay(
            {"GET https://www.okx.com/api/v5/public/funding-rate?instId=NOPE-USDT-SWAP": {"code": "51001", "data": []}}
        )
        with self.assertRaises(FetchError):
            perps.fetch_okx(http, "NOPE")

    def test_all_venues_failing_exits_nonzero(self):
        code, text = run_cli(["funding", "NOPE", "--venues", "okx"], replay({}))
        self.assertEqual(code, 2)
        self.assertIn("Unavailable", text)


class TestOptionsMath(unittest.TestCase):
    def row(self, strike, kind, oi):
        return options_data.OptionRow(NOW, "30OCT26", strike, kind, oi, 0, 50.0, 100.0)

    def test_max_pain(self):
        rows = [
            self.row(90, "C", 10),
            self.row(100, "C", 5),
            self.row(110, "C", 1),
            self.row(90, "P", 1),
            self.row(100, "P", 5),
            self.row(110, "P", 10),
        ]
        # Settling at 100 owes 10*10 (calls at 90) + 10*10 (puts at 110) = 200.
        # Settling at 90 owes 5*10 + 10*20 (puts) = 250; at 110, 10*20 + 5*10 (calls) = 250.
        self.assertEqual(options_data.max_pain(rows), 100)

    def test_parse_instrument(self):
        expiry, code, strike, kind = options_data.parse_instrument("BTC-27NOV26-80000-C")
        self.assertEqual((expiry.year, expiry.month, expiry.day, expiry.hour), (2026, 11, 27, 8))
        self.assertEqual((code, strike, kind), ("27NOV26", 80000.0, "C"))


class TestReadOnly(unittest.TestCase):
    """The tracker must never reach an order, account or withdrawal endpoint."""

    FORBIDDEN = re.compile(
        r"/trade/|/orders?(?![a-z])|/account[/?]|/asset/|/withdraw|private/|/v5/position|"
        r"api[_-]?secret|api[_-]?key|signature|hmac|\"type\":\s*\"order\"",
        re.IGNORECASE,
    )

    def test_no_private_endpoints_or_signing_in_scripts(self):
        for path in (SKILL_DIR / "scripts").glob("*.py"):
            text = path.read_text()
            self.assertIsNone(self.FORBIDDEN.search(text), f"{path.name}: {self.FORBIDDEN.search(text)}")

    def test_only_post_is_hyperliquid_info(self):
        for path in (SKILL_DIR / "scripts").glob("*.py"):
            for match in re.finditer(r"post_json\(([^,]+),", path.read_text()):
                if path.name == "http_client.py":
                    continue
                self.assertEqual(match.group(1).strip(), "HYPERLIQUID", path.name)


if __name__ == "__main__":
    unittest.main()
