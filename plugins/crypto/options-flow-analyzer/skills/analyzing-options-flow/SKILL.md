---
name: analyzing-options-flow
description: 'Track crypto options flow to identify institutional positioning and
  market sentiment.

  Use when tracking institutional options flow.

  Trigger with phrases like "track options flow", "analyze derivatives", or "check
  institutional".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(crypto:options-*)
version: 1.30.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- analyzing-options
compatibility: Designed for Claude Code
---
# Analyzing Options Flow

## Overview

Track and analyze crypto options flow on centralized derivatives exchanges (Deribit, OKX, Bybit) to identify institutional positioning, gauge market sentiment, and detect unusual activity in BTC and ETH options markets.

## Prerequisites

- API credentials for at least one crypto derivatives exchange (Deribit API key recommended; OKX or Bybit as alternatives)
- Python 3.8+ with `requests` and `websocket-client` libraries installed
- Optional: `pandas` and `numpy` for advanced statistical analysis of flow data
- Understanding of options terminology: strike price, expiry, implied volatility, delta, gamma, open interest, and premium
- Network access to exchange WebSocket feeds for real-time flow monitoring

## Instructions

1. Load exchange API credentials from `${CLAUDE_SKILL_DIR}/config/crypto-apis.env` using the Read tool to authenticate against derivatives exchange endpoints.
2. Run `Bash(crypto:options-*)` to connect to the Deribit options data feed and pull the current options chain for BTC or ETH, including all active strikes and expiries.
3. Retrieve open interest data across all strike prices and expiration dates to build an open interest heatmap showing where positions are concentrated.
4. Calculate the aggregate put/call ratio by volume and by open interest to assess overall market sentiment (ratio above 1.0 indicates bearish bias; below 1.0 indicates bullish).
5. Filter for block trades exceeding a configurable notional threshold (e.g., $500K+) to isolate institutional-sized activity from retail noise.
6. Analyze the implied volatility term structure across expiry dates to detect vol compression (potential breakout ahead) or vol expansion (uncertainty increasing).
7. Track max pain levels for upcoming expiries by computing the strike price at which the most options expire worthless, indicating likely price magnetism near expiry.
8. Compare recent flow data against historical baselines (7-day and 30-day rolling averages) to flag statistically unusual positioning.
9. Generate a flow summary report with actionable signals: bullish large-block calls, bearish put sweeps, IV skew shifts, and OI buildup at key strikes.
10. Export results using `--format json` or `--format csv` for integration with trading dashboards or alerting systems.

See [`references/implementation.md`](references/implementation.md) for the full implementation workflow.

## Output

- Options chain tables showing strike, expiry, bid/ask, IV, delta, gamma, open interest, and volume for each contract
- Put/call ratio summary (by volume and open interest) with historical comparison
- Block trade log listing timestamp, direction (buy/sell), strike, expiry, size, premium, and implied volatility
- Open interest heatmap data mapping strike prices against expiration dates with position concentration
- Max pain calculation per expiry date with the optimal pain strike and dollar value at risk
- Implied volatility term structure curves across near-term and far-term expiries
- Unusual activity alerts flagging trades exceeding 2 standard deviations from the rolling average
- JSON or CSV export files for downstream analysis and dashboard integration

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `API Rate Limit Exceeded` | Too many requests to the derivatives exchange API | Implement request throttling with 100ms minimum between calls; use WebSocket feeds for real-time data instead of polling REST endpoints; upgrade API tier if needed |
| `Cannot connect to blockchain node or timeout` | RPC endpoint unreachable when resolving on-chain settlement data | Switch to a backup RPC endpoint; verify network connectivity; confirm the node is fully synced |
| `Invalid API key or signature mismatch` | Exchange API authentication failure | Regenerate API keys on the exchange; verify key permissions include read access to derivatives data; check system clock synchronization (HMAC signatures require accurate timestamps) |
| `No options data for instrument` | Queried an expired or non-existent options contract | Verify the instrument name matches exchange conventions (e.g., `BTC-28MAR25-100000-C` on Deribit); check that the expiry has not already passed |
| `WebSocket connection dropped` | Exchange feed disconnection due to inactivity or network issue | Implement automatic reconnection with exponential backoff; send periodic ping frames to maintain the connection |
| `Insufficient historical data` | Baseline period too short for statistical comparison | Extend the rolling window from 7 days to 30 days; ensure the data collection pipeline has been running long enough to accumulate history |

## Examples

### BTC Options Sentiment Snapshot

```bash
# Pull current BTC options chain and compute put/call ratios
python options_flow.py btc --summary
```

Returns the aggregate put/call ratio, top 5 strikes by open interest, max pain for the nearest expiry, and the current implied volatility at-the-money. A put/call ratio of 0.65 with heavy call OI at the $120K strike suggests bullish institutional positioning.

### Detect Institutional Block Trades

```bash
# Filter for block trades above $1M notional in the last 24 hours
python options_flow.py btc --blocks --min-notional 1000000 --period 24h  # 1000000 = 1M limit
```

Lists all block trades exceeding the threshold with direction inference (aggressor side), strike, expiry, premium paid, and IV at execution. Useful for spotting large directional bets before they move the underlying.

### ETH Implied Volatility Term Structure

```bash
# Generate IV term structure for ETH across all active expiries
python options_flow.py eth --iv-curve --format json > eth_iv_term.json
```

Exports the IV term structure as JSON. Flat or inverted term structures (near-term IV higher than far-term) often precede sharp directional moves, while steep upward-sloping curves indicate calm near-term expectations.

## Resources

- [Deribit API Documentation](https://docs.deribit.com/) -- primary exchange for crypto options data, WebSocket and REST endpoints
- [Laevitas Analytics](https://app.laevitas.ch/) -- crypto derivatives analytics dashboard with options flow visualization
- [Greeks.live](https://www.greeks.live/) -- real-time crypto options analytics and block trade tracking
- Amberdata Derivatives -- institutional-grade crypto derivatives data API
- [The Block Research](https://www.theblock.co/data/crypto-markets/options) -- aggregated crypto options market data and charts
