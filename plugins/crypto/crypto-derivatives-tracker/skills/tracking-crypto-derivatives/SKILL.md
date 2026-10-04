---
name: tracking-crypto-derivatives
description: 'Track cryptocurrency futures, options, and perpetual swaps with funding
  rates, open interest, liquidations, and comprehensive derivatives market analysis.

  Use when monitoring derivatives markets, analyzing funding rates, tracking open
  interest, finding liquidation levels, or researching options flow.

  Trigger with phrases like "funding rate", "open interest", "perpetual swap", "futures
  basis", "liquidation levels", "options flow", "put call ratio", "derivatives analysis",
  or "BTC perps".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(crypto:derivatives-*)
version: 1.29.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- monitoring
- tracking-crypto
compatibility: Designed for Claude Code
---
# Tracking Crypto Derivatives

## Overview

Aggregate funding rates, open interest, liquidations, and options data across CEX and DEX derivatives exchanges to produce actionable trading insights.

**Supported Markets**: Perpetual Swaps (Binance, Bybit, OKX, Deribit, BitMEX), Quarterly Futures, Options (Deribit, OKX, Bybit), DEX Perpetuals (dYdX, GMX, Drift Protocol).

## Prerequisites

- Python 3.8+ installed
- Network access to exchange APIs
- Optional: API keys for higher rate limits
- Understanding of derivatives concepts (funding, OI, basis)

## Instructions

1. **Check funding rates** across exchanges to identify sentiment and arbitrage opportunities:

   ```bash
   python derivatives_tracker.py funding BTC
   python derivatives_tracker.py funding BTC ETH SOL
   python derivatives_tracker.py funding BTC --history 7d
   ```

   - Positive funding (>0.01%): Longs pay shorts, bullish sentiment
   - Negative funding (<-0.01%): Shorts pay longs, bearish sentiment
   - Extreme funding (>0.1%): Potential contrarian opportunity

2. **Analyze open interest** to gauge market positioning and trend strength:

   ```bash
   python derivatives_tracker.py oi BTC
   python derivatives_tracker.py oi BTC --changes
   python derivatives_tracker.py oi BTC --divergence
   ```

   - Rising OI + Rising Price = strong bullish trend
   - Rising OI + Falling Price = strong bearish trend
   - Falling OI + Rising Price = short covering rally
   - Falling OI + Falling Price = long liquidations

3. **Monitor liquidations** to find support/resistance clusters:

   ```bash
   python derivatives_tracker.py liquidations BTC
   python derivatives_tracker.py liquidations BTC --recent
   python derivatives_tracker.py liquidations BTC --min-size 100000  # 100000 = minimum USD liquidation size filter
   ```

4. **Analyze options market** for IV, put/call ratio, and max pain:

   ```bash
   python derivatives_tracker.py options BTC
   python derivatives_tracker.py options BTC --pcr
   python derivatives_tracker.py options BTC --expiry 2025-01-31  # 2025 = target expiry year
   ```

5. **Calculate basis** for spot-futures arbitrage opportunities:

   ```bash
   python derivatives_tracker.py basis BTC
   python derivatives_tracker.py basis BTC --quarterly
   python derivatives_tracker.py basis --all
   ```

6. **Run full dashboard** for comprehensive derivatives overview:

   ```bash
   python derivatives_tracker.py dashboard BTC
   python derivatives_tracker.py dashboard BTC ETH SOL
   python derivatives_tracker.py dashboard BTC --output json
   ```

## Output

The skill produces structured reports per market type:

- **Funding Rate Report**: Current, 24h avg, 7d avg rates per exchange with annualized yield and sentiment
- **Open Interest Report**: OI per exchange with 24h/7d changes, share %, and long/short ratio
- **Liquidation Heatmap**: Long/short liquidation clusters by price level with USD density
- **Options Overview**: Put/call ratio, IV rank, max pain, and large flow alerts
- **Basis Report**: Spot-perp and quarterly basis with annualized carry rates

See `${CLAUDE_SKILL_DIR}/references/implementation.md` for detailed output format examples.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `ERR_RATE_LIMIT` | Too many API requests | Reduce frequency or add API key |
| `ERR_EXCHANGE_DOWN` | Exchange API unavailable | Try alternative exchange |
| `ERR_SYMBOL_INVALID` | Wrong symbol format | Use BTC, ETH (not BTCUSDT) |

## Examples

**Morning derivatives check** - Scan funding, OI, and liquidations for top assets:

```bash
python derivatives_tracker.py dashboard BTC ETH SOL
```

**Funding rate arbitrage** - Alert when funding exceeds threshold for cash-and-carry:

```bash
python derivatives_tracker.py funding BTC --alert-threshold 0.08
```

**Pre-expiry options analysis** - Check max pain and IV before Friday expiry:

```bash
python derivatives_tracker.py options BTC --expiry friday
```

**Basis trading scan** - Find all pairs with annualized yield above 5%:

```bash
python derivatives_tracker.py basis --all --min-yield 5  # 5 = minimum annualized yield %
```

## Resources

- **Coinglass**: Aggregated derivatives data
- **Exchange APIs**: Binance, Bybit, OKX, Deribit
- **The Graph**: DEX perpetuals data
- `${CLAUDE_SKILL_DIR}/references/implementation.md` - Detailed output formats, options/basis guides, key concepts
