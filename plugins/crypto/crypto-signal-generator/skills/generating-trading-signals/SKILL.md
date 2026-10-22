---
name: generating-trading-signals
description: 'Generate trading signals using technical indicators (RSI, MACD, Bollinger
  Bands, etc.).

  Combines multiple indicators into composite signals with confidence scores.

  Use when analyzing assets for trading opportunities or checking technical indicators.

  Trigger with phrases like "get trading signals", "check indicators", "analyze for
  entry",

  "scan for opportunities", "generate buy/sell signals", or "technical analysis".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*)
version: 1.31.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- trading-signals
compatibility: Designed for Claude Code
---
# Generating Trading Signals

## Overview

Multi-indicator signal generation system that analyzes price action using 7 technical indicators and produces composite BUY/SELL signals with confidence scores and risk management levels.

**Indicators**: RSI, MACD, Bollinger Bands, Trend (SMA 20/50/200), Volume, Stochastic Oscillator, ADX.

## Prerequisites

Install required dependencies:

```bash
set -euo pipefail
pip install yfinance pandas numpy
```

Optional for visualization: `pip install matplotlib`

## Instructions

1. **Quick signal scan** across multiple assets:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --watchlist crypto_top10 --period 6m
   ```

   Output shows signal type (STRONG_BUY/BUY/NEUTRAL/SELL/STRONG_SELL) and confidence per asset.

2. **Detailed signal analysis** for a specific symbol:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --symbols BTC-USD --detail
   ```

   Shows each indicator's individual signal, value, and reasoning.

3. **Filter and rank** the best opportunities:

   ```bash
   # Only buy signals with 70%+ confidence
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --filter buy --min-confidence 70 --rank confidence

   # Save results to JSON
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --output signals.json
   ```

4. **Use predefined watchlists**:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --list-watchlists
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --watchlist crypto_defi
   ```

   Available: `crypto_top10`, `crypto_defi`, `crypto_layer2`, `stocks_tech`, `etfs_major`

## Output

The scanner produces a summary table with symbol, signal type, confidence %, price, and stop loss for each asset scanned. Detailed mode adds per-indicator breakdowns with risk management levels (stop loss, take profit, risk/reward ratio).

**Signal types**: STRONG_BUY (+2), BUY (+1), NEUTRAL (0), SELL (-1), STRONG_SELL (-2)

**Confidence ranges**: 70-100% high conviction | 50-70% moderate | 30-50% weak | 0-30% avoid

See [`references/implementation.md`](references/implementation.md) for full output format examples and signal type tables.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| No data for symbol | Invalid ticker or delisted | Verify symbol exists on Yahoo Finance |
| Insufficient data | Period too short for indicators | Use `--period 6m` minimum |
| Rate limit exceeded | Too many rapid API calls | Add delay between scans |

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

**Morning crypto scan** - Check all top-10 crypto assets for entry opportunities:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --watchlist crypto_top10 --period 6m
```

**Deep dive on Bitcoin** - Full indicator breakdown with risk management levels:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --symbols BTC-USD --detail
```

**Find strongest DeFi buy signals** - Filter and rank by confidence:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --watchlist crypto_defi --filter buy --rank confidence
```

**Export results** - Save to JSON for automated pipeline or further analysis:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --watchlist crypto_top10 --output signals.json
```

## Resources

- **yfinance** for price data
- **pandas/numpy** for calculations
- Compatible with trading-strategy-backtester plugin
- [`references/implementation.md`](references/implementation.md) - Output formats, configuration, backtester integration, file reference
