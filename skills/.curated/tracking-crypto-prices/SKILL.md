---
name: tracking-crypto-prices
description: 'Track real-time cryptocurrency prices across exchanges with historical
  data and alerts.

  Provides price data infrastructure for dependent skills (portfolio, tax, DeFi, arbitrage).

  Use when checking crypto prices, monitoring markets, or fetching historical price
  data.

  Trigger with phrases like "check price", "BTC price", "crypto prices", "price history",

  "get quote for", "what''s ETH trading at", "show me top coins", or "track my watchlist".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*)
version: 1.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- monitoring
- tracking-crypto
compatibility: Designed for Claude Code
---
# Tracking Crypto Prices

## Contents

[Overview](#overview) | [Prerequisites](#prerequisites) | [Instructions](#instructions) | [Output](#output) | [Error Handling](#error-handling) | [Examples](#examples) | [Resources](#resources)

## Overview

Foundation skill providing real-time and historical cryptocurrency price data for 10,000+ coins. This is the data layer for the crypto plugin ecosystem -- 10+ other skills depend on it for price information.

## Prerequisites

1. Install dependencies: `pip install requests pandas yfinance`
2. Optional: `pip install python-dotenv` for API key management
3. Optional: Get free API key from https://www.coingecko.com/en/api for higher rate limits
4. Add API key to `${CLAUDE_SKILL_DIR}/config/settings.yaml` or set `COINGECKO_API_KEY` env var

## Instructions

1. Check current prices for one or more symbols:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/price_tracker.py --symbol BTC
   python ${CLAUDE_SKILL_DIR}/scripts/price_tracker.py --symbols BTC,ETH,SOL
   ```

2. Use watchlists to scan predefined groups (available: `top10`, `defi`, `layer2`, `stablecoins`, `memecoins`):

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/price_tracker.py --watchlist top10     # Top 10 by market cap
   python ${CLAUDE_SKILL_DIR}/scripts/price_tracker.py --watchlist defi      # DeFi tokens
   python ${CLAUDE_SKILL_DIR}/scripts/price_tracker.py --watchlist layer2    # Layer 2 tokens
   ```

3. Fetch historical data by period or custom date range:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/price_tracker.py --symbol BTC --period 30d
   python ${CLAUDE_SKILL_DIR}/scripts/price_tracker.py --symbol BTC --period 90d --output csv
   python ${CLAUDE_SKILL_DIR}/scripts/price_tracker.py --symbol ETH --start 2024-01-01 --end 2024-12-31  # 2024 full year
   ```

4. Configure settings by editing `${CLAUDE_SKILL_DIR}/config/settings.yaml` to customize cache TTLs, default currency, and custom watchlists. See `references/implementation.md` for the full configuration reference.

## Output

- **Table** (default): Symbol, price, 24h change, volume, market cap in formatted columns
- **JSON** (`--format json`): Machine-readable with prices array and metadata
- **CSV** (`--output csv`): OHLCV historical data export to `${CLAUDE_SKILL_DIR}/data/`

See [`references/implementation.md`](references/implementation.md) for detailed output format examples.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Unknown symbol: XYZ` | Invalid ticker | Check spelling, use `--list` to search |
| `Rate limit exceeded` | Too many API calls | Wait 60s, or add API key for higher limits |
| `Network error` | No internet | Check connection; cached data used automatically |
| `Cache stale` | Data older than TTL | Shown with warning, refreshes on next call |

The skill auto-manages rate limits: cache first, exponential backoff, yfinance fallback, stale cache as last resort.

## Examples

**Quick price check:**

```bash
python ${CLAUDE_SKILL_DIR}/scripts/price_tracker.py --symbol BTC
# Output: BTC (Bitcoin) $97,234.56 USD +2.34% (24h) | Vol: $28.5B | MCap: $1.92T
```

**Watchlist scan:**

```bash
python ${CLAUDE_SKILL_DIR}/scripts/price_tracker.py --watchlist top10
```

**Historical export:**

```bash
python ${CLAUDE_SKILL_DIR}/scripts/price_tracker.py --symbol ETH --period 90d --output csv
# Creates: ${CLAUDE_SKILL_DIR}/data/ETH_90d_[date].csv
```

## Resources

- [`references/implementation.md`](references/implementation.md) - Output formats, full config, integration guide, file map
- [CoinGecko API](https://www.coingecko.com/en/api) - Primary data source
- [yfinance](https://github.com/ranaroussi/yfinance) - Fallback for historical data
