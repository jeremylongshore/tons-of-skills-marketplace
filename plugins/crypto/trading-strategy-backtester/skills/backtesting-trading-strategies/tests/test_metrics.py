"""Offline edge cases for historical simulation reports."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from metrics import BacktestResult, Trade, calculate_all_metrics, calculate_trade_stats, format_results
from optimize import format_optimization_results


def trade(exit_price):
    return Trade(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"), 100, exit_price, "long", 1)


class HistoricalMetricsTests(unittest.TestCase):
    def test_zero_trades_has_no_profit_factor(self):
        self.assertIsNone(calculate_trade_stats([])["profit_factor"])

    def test_single_winner_has_no_profit_factor(self):
        self.assertIsNone(calculate_trade_stats([trade(110)])["profit_factor"])

    def test_single_breakeven_has_no_profit_factor(self):
        self.assertIsNone(calculate_trade_stats([trade(100)])["profit_factor"])

    def test_single_loser_has_zero_profit_factor(self):
        self.assertEqual(calculate_trade_stats([trade(90)])["profit_factor"], 0)

    def test_mixed_trades_retain_computed_ratio(self):
        self.assertEqual(calculate_trade_stats([trade(120), trade(90)])["profit_factor"], 2)

    def test_no_losses_is_not_infinite_profit_factor(self):
        self.assertIsNone(calculate_trade_stats([trade(110), trade(120)])["profit_factor"])

    def test_render_zero_and_one_trade_results(self):
        for trades in ([], [trade(110)], [trade(100)], [trade(90)]):
            with self.subTest(trades=len(trades), pnl=trades[0].pnl if trades else None):
                index = pd.date_range("2024-01-01", periods=3)
                result = BacktestResult(
                    "fixture",
                    "SYNTHETIC",
                    index[0],
                    index[-1],
                    100,
                    102,
                    trades,
                    pd.Series([100, 101, 102], index=index),
                    {},
                )
                report = format_results(calculate_all_metrics(result))
                self.assertIn("Historical simulation only", report)
                self.assertNotRegex(report.lower(), r"\b(?:inf|nan)\b")
                self.assertIn("insufficient for inference", report)
                if not trades or trades[0].pnl >= 0:
                    self.assertRegex(report, r"Profit Factor:\s+N/A")
                else:
                    self.assertRegex(report, r"Profit Factor:\s+0\.00")

    def test_optimization_labels_in_sample_results(self):
        row = {
            "period": 10,
            "total_return": 1,
            "sharpe_ratio": 0.2,
            "max_drawdown": -1,
            "win_rate": 50,
            "total_trades": 2,
        }
        report = format_optimization_results(pd.DataFrame([row]), ["period"])
        self.assertIn("HISTORICAL SIMULATION", report)
        self.assertIn("not expected future performance", report)
        self.assertNotIn("Expected Performance:", report)


if __name__ == "__main__":
    unittest.main()
