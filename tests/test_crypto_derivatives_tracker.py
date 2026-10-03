"""Regression contract for the crypto-derivatives-tracker plugin scripts.

Issue #1302: exchange_client.py was deleted in a bulk cleanup (#337), so every
analyzer failed at import. These tests pin that the module exists, that each
analyzer imports, and that every CLI subcommand runs end to end on mock data.
"""

import subprocess
import sys
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    ROOT / "plugins" / "crypto" / "crypto-derivatives-tracker" / "skills" / "tracking-crypto-derivatives" / "scripts"
)
ANALYZERS = (
    "funding_tracker",
    "oi_analyzer",
    "options_analyzer",
    "liquidation_monitor",
    "basis_calculator",
    "derivatives_tracker",
)
COMMANDS = (
    ["funding", "BTC"],
    ["oi", "BTC"],
    ["liquidations", "BTC"],
    ["options", "BTC"],
    ["basis", "BTC"],
    ["basis", "ETH"],
    ["dashboard", "BTC", "ETH"],
)


class DerivativesTrackerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(SCRIPTS))

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(str(SCRIPTS))

    def test_exchange_client_module_is_shipped(self):
        self.assertTrue((SCRIPTS / "exchange_client.py").is_file())

    def test_every_analyzer_imports(self):
        for name in ANALYZERS:
            with self.subTest(module=name):
                result = subprocess.run(
                    [sys.executable, "-c", f"import {name}"],
                    cwd=SCRIPTS,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_every_cli_subcommand_runs_on_mock_data(self):
        for args in COMMANDS:
            with self.subTest(command=" ".join(args)):
                result = subprocess.run(
                    [sys.executable, "derivatives_tracker.py", *args],
                    cwd=SCRIPTS,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_basis_term_structure_shape(self):
        from exchange_client import Exchange, ExchangeClient

        points = ExchangeClient(use_mock=True).get_all_basis("BTC", Decimal("67500"), [Exchange.BINANCE, Exchange.OKX])
        self.assertEqual({p.exchange for p in points}, {"binance", "okx"})
        for point in points:
            self.assertGreater(point.days_to_expiry, 0)
            self.assertGreater(point.futures_price, point.spot_price)
            self.assertAlmostEqual(
                point.annualized_pct,
                point.basis_pct * 365 / point.days_to_expiry,
                delta=0.05,
            )

    def test_quarterly_expiries_are_last_fridays_after_today(self):
        from exchange_client import ExchangeClient

        expiries = ExchangeClient._quarterly_expiries(datetime(2026, 12, 26))
        self.assertEqual(
            [e.strftime("%Y-%m-%d") for e in expiries],
            ["2027-03-26", "2027-06-25", "2027-09-24"],
        )
        for expiry in expiries:
            self.assertEqual(expiry.weekday(), 4)


if __name__ == "__main__":
    unittest.main()
