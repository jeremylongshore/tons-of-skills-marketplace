"""Regression contract for the crypto-derivatives-tracker plugin scripts.

Issue #1302: exchange_client.py was deleted in a bulk cleanup (#337), so every
analyzer failed at import. Version 2.0.0 (issue #1785) replaced the mock client
with live public-endpoint adapters. These tests pin that every module imports
and that every CLI subcommand runs end to end, offline, on the bundled recording
of real exchange responses (--demo), so CI needs no network.
"""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    ROOT / "plugins" / "crypto" / "crypto-derivatives-tracker" / "skills" / "tracking-crypto-derivatives" / "scripts"
)
MODULES = (
    "http_client",
    "perps",
    "basis_data",
    "liquidations",
    "options_data",
    "derivatives_tracker",
)
COMMANDS = (
    ["funding", "BTC"],
    ["oi", "BTC"],
    ["liquidations", "BTC"],
    ["options", "BTC", "--large-trades", "1000000"],
    ["basis", "BTC"],
    ["dashboard", "BTC"],
    ["venues"],
)


class DerivativesTrackerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(SCRIPTS))

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(str(SCRIPTS))

    def test_mock_client_is_gone(self):
        # The v1 client generated market data with random.uniform; it must not return.
        self.assertFalse((SCRIPTS / "exchange_client.py").exists())
        for path in SCRIPTS.glob("*.py"):
            self.assertNotIn("random.uniform", path.read_text(), path.name)

    def test_every_module_imports(self):
        for name in MODULES:
            with self.subTest(module=name):
                result = subprocess.run(
                    [sys.executable, "-c", f"import {name}"],
                    cwd=SCRIPTS,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_every_cli_subcommand_runs_on_recorded_data(self):
        for args in COMMANDS:
            with self.subTest(command=" ".join(args)):
                result = subprocess.run(
                    [sys.executable, "derivatives_tracker.py", *args, "--demo"],
                    cwd=SCRIPTS,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                if args[0] != "venues":
                    self.assertIn("[DEMO]", result.stdout)
                    self.assertIn("places no trades", result.stdout)

    def test_basis_term_structure_shape(self):
        import basis_data
        from http_client import Http, Recording

        recording = Recording.load(SCRIPTS.parent / "assets" / "demo-recording.json")
        points, _ = basis_data.fetch_all(Http(replay=recording), "BTC")
        self.assertTrue({p.venue for p in points} <= {"deribit", "okx"})
        self.assertTrue(points)
        for point in points:
            self.assertGreater(point.days_to_expiry, 0.5)
            self.assertGreater(point.index_price, 0)
            self.assertAlmostEqual(point.annualized_pct, point.basis_pct * 365 / point.days_to_expiry, places=9)


if __name__ == "__main__":
    unittest.main()
