#!/usr/bin/env python3
"""
Strategy Parameter Optimizer
Grid search and optimization for trading strategy parameters.

Usage:
    python optimize.py --strategy sma_crossover --symbol BTC-USD \
        --param-grid '{"fast_period": [10,20,30], "slow_period": [50,100,200]}'
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from itertools import product
from typing import Dict, Any, List

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from backtest import load_data, run_backtest
from fetch_data import parse_period
from metrics import format_metric


METRIC_COLUMNS = {
    "total_return": ("Return%", ".1f"),
    "sharpe_ratio": ("Sharpe", ".2f"),
    "sortino_ratio": ("Sortino", ".2f"),
    "max_drawdown": ("MaxDD%", ".1f"),
    "win_rate": ("WinRate%", ".1f"),
    "profit_factor": ("ProfitFactor", ".2f"),
    "calmar_ratio": ("Calmar", ".2f"),
    "total_trades": ("Trades", ".0f"),
}


def grid_search(
    strategy_name: str,
    data: pd.DataFrame,
    param_grid: Dict[str, List[Any]],
    initial_capital: float = 10000,
    metric: str = "sharpe_ratio",
) -> pd.DataFrame:
    """Run grid search over parameter combinations."""

    if metric not in METRIC_COLUMNS:
        raise ValueError(f"Unsupported ranking metric: {metric}")

    # Generate all parameter combinations
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    combinations = list(product(*param_values))

    print(f"Testing {len(combinations)} parameter combinations...")

    results = []

    for i, combo in enumerate(combinations):
        params = dict(zip(param_names, combo))

        try:
            result = run_backtest(
                strategy_name=strategy_name,
                data=data.copy(),
                initial_capital=initial_capital,
                params=params,
            )

            results.append(
                {
                    **params,
                    "total_return": result.total_return,
                    "sharpe_ratio": result.sharpe_ratio,
                    "sortino_ratio": result.sortino_ratio,
                    "max_drawdown": result.max_drawdown,
                    "win_rate": result.win_rate,
                    "profit_factor": float("nan") if result.profit_factor is None else result.profit_factor,
                    "total_trades": result.total_trades,
                    "calmar_ratio": result.calmar_ratio,
                }
            )

            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{len(combinations)}")

        except Exception as e:
            print(f"  Error with params {params}: {e}")
            continue

    df = pd.DataFrame(results)

    # Undefined ratios cannot outrank a finite measurement.
    if metric in df.columns:
        df[metric] = pd.to_numeric(df[metric], errors="coerce").replace([float("inf"), -float("inf")], float("nan"))
        df = df.sort_values(metric, ascending=False, na_position="last")
    df.attrs["ranking_metric"] = metric
    return df


def format_optimization_results(df: pd.DataFrame, param_names: List[str]) -> str:
    """Format optimization results as table."""

    output = []
    output.append("=" * 80)
    output.append("HISTORICAL SIMULATION: PARAMETER OPTIMIZATION")
    output.append("=" * 80)
    output.append("")

    metric = df.attrs.get("ranking_metric", "sharpe_ratio")
    if df.empty:
        output.append("No successful parameter simulations; no best parameter set.")
        return "\n".join(output)
    if metric not in df or not df[metric].notna().any():
        output.append(f"No finite {metric} values; no best parameter set.")
        return "\n".join(output)

    # Top 10 results
    output.append(f"TOP 10 PARAMETER COMBINATIONS (by {metric}):")
    output.append("-" * 80)

    columns = list(dict.fromkeys([metric, "total_return", "sharpe_ratio", "max_drawdown", "win_rate", "total_trades"]))
    header = param_names + [METRIC_COLUMNS[column][0] for column in columns]
    output.append("  ".join(f"{h:>10}" for h in header))
    output.append("-" * 80)

    for row in df.head(10).to_dict("records"):
        values = [row[p] for p in param_names]
        values += [format_metric(row[column], METRIC_COLUMNS[column][1]) for column in columns]
        output.append("  ".join(f"{v:>10}" for v in values))

    output.append("")
    output.append("=" * 80)

    # Best parameters
    best = df.head(1).to_dict("records")[0]
    output.append("BEST PARAMETERS:")
    for p in param_names:
        output.append(f"  {p}: {best[p]}")
    output.append("")
    output.append("In-sample historical simulation (not expected future performance):")
    output.append(f"  Ranking metric ({metric}): {format_metric(best[metric])}")
    output.append(f"  Total Return: {format_metric(best['total_return'], '.2f')}%")
    output.append(f"  Sharpe Ratio: {format_metric(best['sharpe_ratio'], '.2f')}")
    output.append(f"  Max Drawdown: {format_metric(best['max_drawdown'], '.2f')}%")
    output.append(f"  Win Rate: {format_metric(best['win_rate'], '.1f')}%")
    output.append("=" * 80)

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Optimize strategy parameters")
    parser.add_argument("--strategy", "-s", required=True, help="Strategy name")
    parser.add_argument("--symbol", required=True, help="Trading symbol")
    parser.add_argument("--param-grid", required=True, help="Parameter grid as JSON")
    parser.add_argument("--period", "-p", default="1y", help="Lookback period")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    parser.add_argument("--capital", "-c", type=float, default=10000, help="Initial capital")
    parser.add_argument(
        "--metric", "-m", default="sharpe_ratio", choices=tuple(METRIC_COLUMNS), help="Optimization metric"
    )
    parser.add_argument("--output", "-o", help="Output directory")

    args = parser.parse_args()

    # Parse parameter grid
    param_grid = json.loads(args.param_grid)

    # Determine date range
    if args.start and args.end:
        start = datetime.strptime(args.start, "%Y-%m-%d")
        end = datetime.strptime(args.end, "%Y-%m-%d")
    else:
        end = datetime.now()
        start = end - parse_period(args.period)

    # Load data
    script_dir = Path(__file__).parent.parent
    data_dir = script_dir / "data"

    print(f"Loading data for {args.symbol}...")
    data = load_data(args.symbol, start, end, data_dir)
    data.attrs["symbol"] = args.symbol

    print(f"Loaded {len(data)} bars")

    # Run optimization
    results_df = grid_search(
        strategy_name=args.strategy,
        data=data,
        param_grid=param_grid,
        initial_capital=args.capital,
        metric=args.metric,
    )

    # Format and print results
    param_names = list(param_grid.keys())
    output = format_optimization_results(results_df, param_names)
    print(output)

    # Save results
    output_dir = Path(args.output) if args.output else script_dir / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_file = output_dir / f"optimization_{args.strategy}_{timestamp}.csv"
    results_df.to_csv(csv_file, index=False)
    print(f"\nFull results saved to: {csv_file}")

    txt_file = output_dir / f"optimization_{args.strategy}_{timestamp}.txt"
    with open(txt_file, "w") as f:
        f.write(output)


if __name__ == "__main__":
    main()
