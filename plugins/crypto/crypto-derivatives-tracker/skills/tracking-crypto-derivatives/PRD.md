# PRD: Crypto Derivatives Tracker

> Part of [Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)

## Summary

**One-liner**: Read-only research on crypto perpetuals, dated futures and options from live public exchange data.
**Domain**: Cryptocurrency market research
**Users**: Traders and analysts who want cross-venue derivatives data with sources, without API keys

## Problem Statement

Derivatives data is spread across many venues, each with its own units: funding paid hourly on some venues and every 8 hours on others, open interest counted in contracts, coins, USD, one side or both. Comparing venues by hand means reading each API's documentation and converting units. Free aggregators hide their sources; paid ones cost a subscription.

Version 1.x of this skill did not solve the problem: it generated its numbers at random. Version 2.0.0 replaces that with live public data.

## Users

- **Active trader**: checks funding and open interest across venues before acting on their own judgment.
- **Researcher or writer**: needs sourced figures and a reproducible method.
- **Developer**: wants JSON in one envelope to feed their own analysis.

## Requirements

### Must

1. Every figure comes from a public, keyless endpoint and carries its source URL and fetch time.
2. No mock, random or hard-coded market data by default. Recorded data only behind `--demo`, marked on every line.
3. A venue that fails is named with a plain reason (region block, rate limit, not listed, timeout); the remaining venues still report; no value is substituted.
4. Funding normalized to an 8-hour equivalent; open interest normalized to one side, in coins and USD.
5. No order, account, withdrawal or signing code. A test enforces it.
6. Every report ends with: "Research output only. Not financial advice. This tool places no trades."
7. Standard library only; Python 3.9+.

### Should

1. JSON output in one envelope (`skill`, `version`, `command`, `generated_at`, `mode`, `sources`, `failures`, `data`, `disclaimer`).
2. Offline tests that replay recorded real responses.
3. Output describes conditions and does not recommend trades.

### Will not

- Liquidation heatmaps (vendor model estimates, not reproducible from public data).
- Simulated options flow.
- Trading, alerts that tell the user to act, or account access.

## Success criteria

- Live run returns data from at least five venues for BTC from a US network (seven did on 2026-10-25: OKX, Deribit, Hyperliquid, Kraken, KuCoin, Gate, dYdX; Binance and Bybit refused).
- From a network Binance and Bybit serve, all nine venues return (verified 2026-10-25 from France).
- `python3 -m unittest discover -s tests` passes offline.
