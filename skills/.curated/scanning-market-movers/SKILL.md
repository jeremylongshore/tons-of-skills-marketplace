---
name: scanning-market-movers
description: 'Detect significant price movements and unusual volume across crypto
  markets.

  Calculates significance scores combining price change, volume ratio, and market
  cap.

  Use when tracking market movers, finding gainers/losers, or detecting volume spikes.

  Trigger with phrases like "scan market movers", "top gainers", "biggest losers",

  "volume spikes", "what''s moving", "find pumps", or "market scan".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*)
version: 1.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- scanning-market
compatibility: Designed for Claude Code
---
# Scanning Market Movers

## Overview

Real-time detection of significant price movements and unusual volume patterns across 1,000+ cryptocurrencies, ranked by composite significance score.

## Prerequisites

1. **Python 3.8+** installed
2. **Dependencies**: `pip install requests pandas`
3. **market-price-tracker** plugin installed with `tracking-crypto-prices` skill configured

## Instructions

1. **Run a default scan** for top gainers and losers (top 20 each by 24h change with volume confirmation):

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py
   ```

2. **Set custom thresholds** for minimum change and volume spike:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --min-change 10 --volume-spike 3
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --min-cap 100000000 --max-cap 1000000000  # 100000000 = $100M min cap, 1000000000 = $1B max cap
   ```

3. **Filter by category** (defi, layer2, nft, gaming, meme):

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --category defi
   ```

4. **Scan different timeframes** (1h, 24h, 7d):

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --timeframe 1h
   ```

5. **Export results** to JSON or CSV:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --format json --output movers.json
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --format csv --output movers.csv
   ```

6. **Use named presets** for predefined threshold sets:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --preset aggressive
   ```

## Output

Default table shows top gainers and losers ranked by significance score (0-100), combining price change (40%), volume ratio (40%), and market cap (20%):

```
================================================================================
  MARKET MOVERS                                    Updated: 2025-01-14 15:30:00  # 2025 timestamp
================================================================================

  TOP GAINERS (24h)
--------------------------------------------------------------------------------
  Rank  Symbol      Price         Change    Vol Ratio   Market Cap    Score
--------------------------------------------------------------------------------
    1   XYZ       $1.234        +45.67%        5.2x      $123.4M      89.3
    2   ABC       $0.567        +32.10%        3.8x       $45.6M      76.5
    3   DEF       $2.890        +28.45%        2.9x      $234.5M      71.2
--------------------------------------------------------------------------------

  TOP LOSERS (24h)
--------------------------------------------------------------------------------
  Rank  Symbol      Price         Change    Vol Ratio   Market Cap    Score
--------------------------------------------------------------------------------
    1   GHI       $3.456        -28.90%        4.1x       $89.1M      72.1
    2   JKL       $0.123        -22.34%        2.5x       $12.3M      58.9
--------------------------------------------------------------------------------

  Summary: 42 movers found | Scanned: 1000 assets  # 1000 assets in scan universe
================================================================================
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Dependency not found` | tracking-crypto-prices unavailable | Install market-price-tracker plugin |
| `No movers found` | Thresholds too strict | Relax thresholds with lower values |
| `Rate limit exceeded` | Too many API calls | Wait or use cached data |
| `Partial results` | Some assets unavailable | Normal, proceed with available data |

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

Common scanning patterns for different market analysis scenarios:

```bash
# Daily scan - top 20 gainers/losers
python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --timeframe 24h --top 20

# Volume spike hunt (5x+ volume, $1M+ daily volume)
python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --volume-spike 5 --min-volume 1000000  # 1000000 = $1M min volume

# DeFi movers exported to CSV
python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --category defi --format csv --output defi_movers.csv

# High-cap gainers only (>$1B market cap)
python ${CLAUDE_SKILL_DIR}/scripts/scanner.py --min-cap 1000000000 --gainers-only --top 10  # 1000000000 = $1B cap
```

## Resources

- [`references/implementation.md`](references/implementation.md) - Configuration, presets, JSON format, scoring details
- [`references/errors.md`](references/errors.md) - Comprehensive error handling
- [`references/examples.md`](references/examples.md) - Detailed usage examples
- Depends on: tracking-crypto-prices skill
- CoinGecko API: https://www.coingecko.com/en/api
