---
name: backtesting-trading-strategies
description: 'Backtest crypto and traditional trading strategies against historical
  data.

  Calculates performance metrics (Sharpe, Sortino, max drawdown), generates equity
  curves,

  and optimizes strategy parameters. Use when user wants to test a trading strategy,

  validate signals, or compare approaches.

  Trigger with phrases like "backtest strategy", "test trading strategy", "historical
  performance",

  "simulate trades", "optimize parameters", or "validate signals".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*)
version: 1.29.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- testing
- performance
compatibility: Designed for Claude Code
---
# Backtesting Trading Strategies

## Overview

Validate trading strategies against historical data before risking real capital. This skill provides a complete backtesting framework with 8 built-in strategies, comprehensive performance metrics, and parameter optimization.

**Key Features:**

- 8 pre-built trading strategies (SMA, EMA, RSI, MACD, Bollinger, Breakout, Mean Reversion, Momentum)
- Full performance metrics (Sharpe, Sortino, Calmar, VaR, max drawdown)
- Parameter grid search optimization
- Equity curve visualization
- Trade-by-trade analysis

## Prerequisites

Install required dependencies:

```bash
set -euo pipefail
pip install pandas numpy yfinance matplotlib
```

Optional for advanced features:

```bash
set -euo pipefail
pip install ta-lib scipy scikit-learn
```

## Instructions

1. Fetch historical data (cached to `${CLAUDE_SKILL_DIR}/data/` for reuse):

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/fetch_data.py --symbol BTC-USD --period 2y --interval 1d
   ```

2. Run a backtest with default or custom parameters:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/backtest.py --strategy sma_crossover --symbol BTC-USD --period 1y
   python ${CLAUDE_SKILL_DIR}/scripts/backtest.py \
     --strategy rsi_reversal \
     --symbol ETH-USD \
     --period 1y \
     --capital 10000 \  # 10000: 10 seconds in ms
     --params '{"period": 14, "overbought": 70, "oversold": 30}'
   ```

3. Analyze results saved to `${CLAUDE_SKILL_DIR}/reports/` -- includes `*_summary.txt` (performance metrics), `*_trades.csv` (trade log), `*_equity.csv` (equity curve data), and `*_chart.png` (visual equity curve).
4. Optimize parameters via grid search to find the best combination:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/optimize.py \
     --strategy sma_crossover \
     --symbol BTC-USD \
     --period 1y \
     --param-grid '{"fast_period": [10, 20, 30], "slow_period": [50, 100, 200]}'  # HTTP 200 OK
   ```

## Output

### Performance Metrics

| Metric | Description |
|--------|-------------|
| Total Return | Overall percentage gain/loss |
| CAGR | Compound annual growth rate |
| Sharpe Ratio | Risk-adjusted return (target: >1.5) |
| Sortino Ratio | Downside risk-adjusted return |
| Calmar Ratio | Return divided by max drawdown |

### Risk Metrics

| Metric | Description |
|--------|-------------|
| Max Drawdown | Largest peak-to-trough decline |
| VaR (95%) | Value at Risk at 95% confidence |
| CVaR (95%) | Expected loss beyond VaR |
| Volatility | Annualized standard deviation |

### Trade Statistics

| Metric | Description |
|--------|-------------|
| Total Trades | Number of round-trip trades |
| Win Rate | Percentage of profitable trades |
| Profit Factor | Gross profit divided by gross loss |
| Expectancy | Expected value per trade |

### Example Output

```
================================================================================
                    BACKTEST RESULTS: SMA CROSSOVER
                    BTC-USD | [start_date] to [end_date]
================================================================================
 PERFORMANCE                          | RISK
 Total Return:        +47.32%         | Max Drawdown:      -18.45%
 CAGR:                +47.32%         | VaR (95%):         -2.34%
 Sharpe Ratio:        1.87            | Volatility:        42.1%
 Sortino Ratio:       2.41            | Ulcer Index:       8.2
--------------------------------------------------------------------------------
 TRADE STATISTICS
 Total Trades:        24              | Profit Factor:     2.34
 Win Rate:            58.3%           | Expectancy:        $197.17
 Avg Win:             $892.45         | Max Consec. Losses: 3
================================================================================
```

## Supported Strategies

| Strategy | Description | Key Parameters |
|----------|-------------|----------------|
| `sma_crossover` | Simple moving average crossover | `fast_period`, `slow_period` |
| `ema_crossover` | Exponential MA crossover | `fast_period`, `slow_period` |
| `rsi_reversal` | RSI overbought/oversold | `period`, `overbought`, `oversold` |
| `macd` | MACD signal line crossover | `fast`, `slow`, `signal` |
| `bollinger_bands` | Mean reversion on bands | `period`, `std_dev` |
| `breakout` | Price breakout from range | `lookback`, `threshold` |
| `mean_reversion` | Return to moving average | `period`, `z_threshold` |
| `momentum` | Rate of change momentum | `period`, `threshold` |

## Configuration

Create `${CLAUDE_SKILL_DIR}/config/settings.yaml`:

```yaml
data:
  provider: yfinance
  cache_dir: ./data

backtest:
  default_capital: 10000  # 10000: 10 seconds in ms
  commission: 0.001     # 0.1% per trade
  slippage: 0.0005      # 0.05% slippage

risk:
  max_position_size: 0.95
  stop_loss: null       # Optional fixed stop loss
  take_profit: null     # Optional fixed take profit
```

## Error Handling

See [`references/errors.md`](references/errors.md) for common issues and solutions.

## Examples

See [`references/examples.md`](references/examples.md) for detailed usage examples including:

- Multi-asset comparison
- Walk-forward analysis
- Parameter optimization workflows

## Files

| File | Purpose |
|------|---------|
| `scripts/backtest.py` | Main backtesting engine |
| `scripts/fetch_data.py` | Historical data fetcher |
| `scripts/strategies.py` | Strategy definitions |
| `scripts/metrics.py` | Performance calculations |
| `scripts/optimize.py` | Parameter optimization |

## Resources

- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance data
- [TA-Lib](https://ta-lib.org/) - Technical analysis library
- [QuantStats](https://github.com/ranaroussi/quantstats) - Portfolio analytics
