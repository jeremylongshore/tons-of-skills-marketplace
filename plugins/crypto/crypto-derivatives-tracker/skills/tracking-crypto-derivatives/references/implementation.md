# Implementation Reference

## Design

- **Public data only.** Every request is an unauthenticated GET (plus Hyperliquid's public `info` POST). There is no order, account, withdrawal or signing code; `tests/` checks that.
- **No invented values.** A venue that errors, refuses the connection or does not list the coin appears under "Unavailable" with the reason. Summaries use only the venues that answered.
- **Standard library only.** `urllib` for HTTP, a thread pool to query venues in parallel.
- **Recorded data is labelled.** `--demo` replays `assets/demo-recording.json`, a recording of real responses, through the same parsers. Every console line starts with `[DEMO]` and JSON carries `"mode": "demo"`.

## Modules

| File | Role |
|------|------|
| `scripts/http_client.py` | Requests, plain-language failure reasons, recording and replay, one clock per run |
| `scripts/perps.py` | Per-venue funding and open interest adapters, 24h history, account ratios, funding summary |
| `scripts/basis_data.py` | Dated-futures basis from Deribit and OKX |
| `scripts/liquidations.py` | OKX filled liquidation orders, paged back over the look-back window |
| `scripts/options_data.py` | Deribit option summaries, max pain, ATM IV, DVOL, large trades |
| `scripts/derivatives_tracker.py` | Command line, console tables, JSON envelope |
| `scripts/record_demo.py` | Maintainer tool that refreshes the demo recording |

## Units and formulas

**Funding.** Each venue's `funding_rate` is the rate for one of its own funding intervals, as a fraction.

- 8-hour equivalent = `funding_rate × 8 / interval_hours`
- Simple annual rate = `funding_rate × (8760 / interval_hours) × 100`%
- Open-interest-weighted mean uses each venue's one-sided open interest in USD as the weight.

**Open interest** is counted on one side (the number of open contracts, not longs plus shorts), converted to coins, then to USD at the venue's mark or index price. The 24-hour change compares coin amounts an hour apart 24 hours back, so price moves do not affect it.

**Basis** = `(futures price / index - 1) × 100`%, using the same venue's index. Annualized = `basis × 365 / days to expiry` (simple). Futures within 12 hours of expiry are omitted because annualizing them amplifies noise.

**Max pain** for an expiry is the strike at which `Σ call OI × max(S − K, 0) + Σ put OI × max(K − S, 0)` is smallest.

**ATM IV** is Deribit's mark IV at the strike nearest the expiry's underlying price (call and put averaged).

**DVOL rank** = `(current − 365-day low) / (365-day high − 365-day low)`; **percentile** = share of the past 365 daily closes below the current value.

## Venue field mapping

| Venue | Instrument | Funding field, interval | Open interest field |
|-------|-----------|-------------------------|---------------------|
| OKX | `{COIN}-USDT-SWAP` | `fundingRate`, interval from `nextFundingTime − fundingTime` (8h) | `oiCcy` (coins) |
| Deribit | `BTC-PERPETUAL`, `ETH-PERPETUAL`, else `{COIN}_USDC-PERPETUAL` | `funding_8h` (accrues continuously) | `open_interest`: USD for inverse perpetuals, coins for USDC perpetuals |
| Hyperliquid | `{COIN}` | `funding`, hourly | `openInterest` (coins) |
| Kraken Futures | `PF_{COIN}USD` (BTC is `XBT`) | `relativeFundingRate`, hourly | `openInterest` (contract size one coin) |
| KuCoin Futures | `{COIN}USDTM` (BTC is `XBT`) | `fundingFeeRate`, `currentFundingRateGranularity` (8h) | `openInterest × multiplier` |
| Gate | `{COIN}_USDT` | `funding_rate`, `funding_interval` (8h) | `position_size × quanto_multiplier` (total long side) |
| dYdX | `{COIN}-USD` | `nextFundingRate`, hourly | `openInterest` (coins) |
| Binance | `{COIN}USDT` | `lastFundingRate`, interval from `fundingInfo` (8h default) | `openInterest` (coins) |
| Bybit | `{COIN}USDT` | `fundingRate`, `fundingIntervalHour` | `singleOpenInterest` (`openInterest` counts both sides) |

Hourly funding intervals for Hyperliquid, Kraken and dYdX were confirmed from each venue's funding-history timestamps on 2026-10-25.

## Not covered, on purpose

- **Liquidation heatmaps.** Vendors estimate where positions would be liquidated from models; public exchange data cannot reproduce that, so no heatmap is drawn.
- **Simulated options flow.** Only real recent trades (`--large-trades`) are shown.
- **Liquidations outside OKX.** Other venues in this set publish liquidations only over websockets or not at all. The report says it is OKX only.
- **BitMEX.** It refuses connections from both the US and the EU networks tested, so it was removed.
- **Interpretation as advice.** Output describes conditions; it does not recommend trades.

## Refreshing the demo recording

```bash
cd scripts && python3 record_demo.py
```

This runs every command for BTC through one recording client, trims the large Deribit payloads to the fields and expiries the demo displays, and rewrites `assets/demo-recording.json`. Run the tests afterwards.
