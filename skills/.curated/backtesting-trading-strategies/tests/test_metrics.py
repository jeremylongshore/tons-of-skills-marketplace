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


class UnavailableMetricTests(unittest.TestCase):
    def test_one_bar_equity_report_does_not_print_nan(self):
        index = pd.date_range("2024-01-01", periods=1)
        result = BacktestResult(
            strategy="fixture",
            symbol="SYNTHETIC",
            start_date=index[0],
            end_date=index[0],
            initial_capital=100,
            final_capital=100,
            trades=[],
            equity_curve=pd.Series([100], index=index),
            parameters={},
        )
        report = format_results(calculate_all_metrics(result))
        self.assertNotRegex(report.lower(), r"\b(?:nan|inf)\b")
        self.assertRegex(report, r"Volatility:\s+N/A")

    def test_report_formats_all_nonfinite_metrics_as_unavailable(self):
        index = pd.date_range("2024-01-01", periods=2)
        result = BacktestResult(
            strategy="fixture",
            symbol="SYNTHETIC",
            start_date=index[0],
            end_date=index[-1],
            initial_capital=100,
            final_capital=100,
            trades=[],
            equity_curve=pd.Series([100, 100], index=index),
            parameters={},
        )
        for field in (
            "total_return",
            "cagr",
            "sharpe_ratio",
            "sortino_ratio",
            "calmar_ratio",
            "max_drawdown",
            "volatility",
            "var_95",
            "cvar_95",
            "ulcer_index",
            "win_rate",
            "expectancy",
            "avg_win",
            "avg_loss",
        ):
            setattr(result, field, float("nan"))
        result.profit_factor = float("inf")
        self.assertNotRegex(format_results(result).lower(), r"\b(?:nan|inf)\b")
        result.sortino_ratio = None
        self.assertIn("N/A", format_results(result))

    def test_optimizer_keeps_numeric_missing_values_and_ranks_them_last(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from optimize import grid_search

        def result(**kw):
            period = kw["params"]["period"]
            return SimpleNamespace(
                total_return=0,
                sharpe_ratio=0,
                sortino_ratio=0,
                max_drawdown=0,
                win_rate=0,
                profit_factor=None if period == 1 else 2.0,
                total_trades=1,
                calmar_ratio=0,
            )

        with patch("optimize.run_backtest", side_effect=result):
            frame = grid_search("fixture", pd.DataFrame(), {"period": [1, 2]}, metric="profit_factor")
        self.assertTrue(pd.api.types.is_numeric_dtype(frame["profit_factor"]))
        self.assertEqual(frame["period"].tolist(), [2, 1])
        self.assertTrue(pd.isna(frame.iloc[-1]["profit_factor"]))
        report = format_optimization_results(frame, ["period"])
        self.assertIn("by profit_factor", report)
        self.assertIn("ProfitFactor", report)
        self.assertIn("Ranking metric (profit_factor): 2.00", report)
        self.assertIn("  period: 2", report.splitlines())
        frame = frame[frame["period"] == 1]
        self.assertIn("no best parameter set", format_optimization_results(frame, ["period"]))
        self.assertIn("no best parameter set", format_optimization_results(pd.DataFrame(), []))


if __name__ == "__main__":
    unittest.main()
