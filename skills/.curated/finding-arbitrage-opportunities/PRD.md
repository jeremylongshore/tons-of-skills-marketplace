# PRD: Arbitrage Opportunity Finder

> Part of [Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)

## Summary

**One-liner**: Compare live best bid and ask for one crypto pair across exchanges and show every spread, gross and net of stated fees.
**Domain**: Cryptocurrency market research
**Users**: Traders and analysts checking whether price gaps between venues survive fees

## Problem Statement

Price gaps between exchanges are small and short-lived, and most of them disappear once fees are counted. Checking means opening several exchange pages, matching the exact pair (USD, USDT and USDC markets differ), and knowing each venue's fee. Version 1.x of this skill did not help: it read every price from a hard-coded table, even in "live" mode.

## Users

- **Trader**: wants to see quickly whether any venue pair stays positive after fees, before doing their own checks.
- **Researcher**: wants sourced, reproducible spread measurements.
- **Developer**: wants JSON to feed their own analysis.

## Requirements

### Must

1. Prices come from public, keyless order-book endpoints, with source URLs and fetch time.
2. Only identical pairs are compared.
3. Every spread is shown gross and net; each fee assumption names its source. A venue whose fee cannot be confirmed shows `n/a` net until the user sets it.
4. A failing venue is named with a plain reason; no price is substituted.
5. No mock prices by default; recorded data only behind `--demo`, marked on every line.
6. No order, account, withdrawal or signing code; a test enforces it.
7. Every report lists what is not included (withdrawal fees, transfer time, price moves, depth) and ends with "Research output only. Not financial advice. This tool places no trades."
8. Standard library only; Python 3.9+.

### Should

1. Size available at the best prices for each spread.
2. Triangular search on venues that publish full ticker lists, with a volume floor.
3. Offline tests replaying recorded real responses.

### Will not

- Execute trades, simulate executions, or use flash loans.
- DEX or cross-chain prices (no reliable keyless source).

## Success criteria

- From a US network, at least five venues quote BTC/USDT (seven did on 2026-10-25); from a network Binance and Bybit serve, all nine (verified from France).
- `python3 -m unittest discover -s tests` passes offline.
