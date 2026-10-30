# Backtesting Examples

## Example 1: Basic SMA Crossover Backtest

Test a simple moving average crossover strategy on Bitcoin:

```bash
python scripts/backtest.py \
  --strategy sma_crossover \
  --symbol BTC-USD \
  --period 1y \
  --capital 10000 \
  --params '{"fast_period": 20, "slow_period": 50}'
```

**Output layout (placeholders, not measured performance):**

```text
HISTORICAL SIMULATION: SMA_CROSSOVER
BTC-USD | [start_date] to [end_date]
Total Return: [computed] | Max Drawdown: [computed]
Sharpe Ratio: [computed] | Win Rate: [computed]
Profit Factor: [computed or N/A when there are no observed losses]
```

Results depend on the supplied historical series, fees, slippage and parameters.
A zero/one-trade sample does not establish performance or predict future returns.

## Example 2: RSI Reversal Strategy

Test an RSI mean reversion strategy on Ethereum:

```bash
python scripts/backtest.py \
  --strategy rsi_reversal \
  --symbol ETH-USD \
  --start 2023-01-01 \
  --end 2024-01-01 \
  --capital 25000 \
  --params '{"period": 14, "overbought": 70, "oversold": 30}'
```

## Example 3: MACD with Custom Costs

Test MACD on Solana with realistic exchange fees:

```bash
python scripts/backtest.py \
  --strategy macd \
  --symbol SOL-USD \
  --period 6m \
  --capital 5000 \
  --commission 0.002 \
  --slippage 0.001 \
  --params '{"fast": 12, "slow": 26, "signal": 9}'
```

## Example 4: Parameter Optimization

Find optimal SMA crossover parameters:

```bash
python scripts/optimize.py \
  --strategy sma_crossover \
  --symbol BTC-USD \
  --period 2y \
  --param-grid '{"fast_period": [10, 20, 30, 50], "slow_period": [50, 100, 150, 200]}'
```

The report ranks the tested parameter combinations using the selected metric.
Its return, drawdown and trade statistics describe an in-sample historical
simulation. Do not treat the winning combination as expected future performance.

## Example 5: Compare Multiple Strategies

Test different strategies on the same data:

```bash
# Fetch data once
python scripts/fetch_data.py --symbol BTC-USD --period 1y

# Run each strategy
for strategy in sma_crossover ema_crossover rsi_reversal macd bollinger_bands; do
  python scripts/backtest.py --strategy $strategy --symbol BTC-USD --period 1y --quiet
done
```

## Example 6: Bollinger Bands Mean Reversion

```bash
python scripts/backtest.py \
  --strategy bollinger_bands \
  --symbol ETH-USD \
  --period 1y \
  --params '{"period": 20, "std_dev": 2.0}'
```

## Example 7: Breakout Strategy

```bash
python scripts/backtest.py \
  --strategy breakout \
  --symbol BTC-USD \
  --period 6m \
  --params '{"lookback": 20, "threshold": 1.0}'
```

## Example 8: List Available Strategies

```bash
python scripts/backtest.py --list
```

**Output:**

```
Available strategies:
  sma_crossover: Simple Moving Average Crossover Strategy.
  ema_crossover: Exponential Moving Average Crossover Strategy.
  rsi_reversal: RSI Overbought/Oversold Reversal Strategy.
  macd: MACD Signal Line Crossover Strategy.
  bollinger_bands: Bollinger Bands Mean Reversion Strategy.
  breakout: Price Breakout Strategy.
  mean_reversion: Mean Reversion Strategy.
  momentum: Rate of Change Momentum Strategy.
```

## Example 9: Walk-Forward Analysis

Test strategy on rolling windows:

```bash
# Train on 2022, test on 2023
python scripts/backtest.py \
  --strategy sma_crossover \
  --symbol BTC-USD \
  --start 2023-01-01 \
  --end 2023-12-31 \
  --params '{"fast_period": 20, "slow_period": 100}'  # From 2022 optimization
```

## Example 10: Multi-Asset Portfolio

Test same strategy across multiple assets:

```bash
for symbol in BTC-USD ETH-USD SOL-USD AVAX-USD; do
  echo "=== $symbol ==="
  python scripts/backtest.py \
    --strategy sma_crossover \
    --symbol $symbol \
    --period 1y \
    --quiet
done
```

---

_[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)_
