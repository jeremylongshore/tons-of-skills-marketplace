---
name: finding-arbitrage-opportunities
description: 'Detect profitable arbitrage opportunities across CEX, DEX, and cross-chain
  markets in real-time.

  Use when scanning for price spreads, finding arbitrage paths, comparing exchange
  prices, or analyzing triangular arbitrage opportunities.

  Trigger with phrases like "find arbitrage", "scan for arb", "price spread", "exchange
  arbitrage", "triangular arb", "DEX price difference", or "cross-exchange opportunity".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(crypto:arbitrage-*)
version: 1.27.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- finding-arbitrage
compatibility: Designed for Claude Code
---
# Finding Arbitrage Opportunities

## Overview

Detect and analyze arbitrage opportunities across cryptocurrency exchanges and DeFi protocols. Aggregates prices from CEX and DEX sources, calculates net profit after fees, and identifies direct, triangular, and cross-chain arbitrage paths.

## Prerequisites

- Python 3.9+ with `httpx`, `rich`, and `networkx` packages
- Internet access for API calls (no API keys required for basic use)
- Optional: Exchange API keys for real-time order book access
- Understanding of arbitrage concepts and trading fees

## Instructions

1. **Quick spread scan** on a specific pair:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py scan ETH USDC
   ```

   Shows current prices per exchange, spread %, estimated profit after fees, and recommended action.

2. **Multi-exchange comparison** across specific exchanges:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py scan ETH USDC \
     --exchanges binance,coinbase,kraken,kucoin,okx
   ```

3. **DEX price comparison** across decentralized exchanges:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py scan ETH USDC --dex-only
   ```

   Compares Uniswap V3, SushiSwap, Curve, Balancer with gas cost estimates.

4. **Triangular arbitrage discovery** within a single exchange:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py triangular binance --min-profit 0.5
   ```

5. **Cross-chain opportunities** across different blockchains:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py cross-chain USDC \
     --chains ethereum,polygon,arbitrum
   ```

6. **Real-time monitoring** with threshold alerts:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py monitor ETH USDC \
     --threshold 0.5 --interval 5
   ```

7. **Export opportunities** for bot integration:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py scan ETH USDC --output json > opportunities.json
   ```

## Output

- **Quick mode** (default): Best opportunity with profit estimate, buy/sell recommendation, risk level
- **Detailed mode** (`--detailed`): All exchange prices, fee breakdown, slippage estimates, historical spread context
- **Monitor mode**: Real-time updates with threshold alerts and trend indicators

See [`references/implementation.md`](references/implementation.md) for exchange fee tables and output format examples.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Rate limited | Too many API requests | Reduce polling frequency or add API key |
| Stale prices | Data older than 10s | Flagged with warning; retry |
| No spread | Efficient market pricing | Normal condition; try different pairs |
| Insufficient liquidity | Trade exceeds order book depth | Reduce trade size |

## Examples

**Quick ETH/USDC spread scan** - Find best buy/sell across all CEX exchanges:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py scan ETH USDC
```

Sample detection output:

```
  ARB OPPORTUNITY: ETH/USDC
  Buy:  Binance  @ $3,198.50  |  Sell: Coinbase @ $3,214.20
  Spread: 0.49%  |  Net Profit (after fees): 0.29% ($9.27 per ETH)
  Risk: LOW  |  Confidence: HIGH  |  Window: ~30s
```

**Triangular arb on Binance** - Discover circular paths with minimum 0.5% net profit:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py triangular binance --min-profit 0.5
```

**Cross-chain USDC opportunities** - Compare stablecoin prices across L1/L2 chains:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py cross-chain USDC --chains ethereum,polygon,arbitrum
```

**Calculate exact profit** - Detailed fee breakdown for a specific trade:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py calc \
  --buy-exchange binance --sell-exchange coinbase --pair ETH/USDC --amount 10  # 10 = trade size in ETH
```

## Resources

- [CoinGecko API](https://www.coingecko.com/en/api) - Free price data
- [CCXT Library](https://github.com/ccxt/ccxt) - Unified exchange API
- Uniswap Subgraph - DEX data
- [`references/implementation.md`](references/implementation.md) - Exchange fee tables, configuration, advanced arbitrage types, disclaimer
