---
name: tracking-crypto-derivatives
description: 'Research crypto perpetual swaps, dated futures and options from live public
  exchange data: funding rates, open interest, basis, liquidations, put/call ratios
  and max pain. Read-only, no API keys.

  Use when checking funding across exchanges, comparing open interest, reading the
  futures term structure, reviewing recent liquidations, or summarizing the options
  market for BTC or ETH.

  Trigger with phrases like "funding rate", "open interest", "perpetual swap", "futures
  basis", "liquidations", "put call ratio", "max pain", "derivatives analysis", or
  "BTC perps".

  '
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py:*)
argument-hint: "<funding|oi|basis|liquidations|options|dashboard> <SYMBOL>"
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- derivatives
- futures
compatibility: Designed for Claude Code
---
# Tracking Crypto Derivatives

## Overview

Pull funding rates, open interest, dated-futures basis, liquidations and options data from public, keyless exchange endpoints, normalize them to common units, and report each figure with its source. When a venue fails, it is named with the reason; no value is ever invented.

| Data | Venues |
|------|--------|
| Funding, open interest | OKX, Deribit, Hyperliquid, Kraken Futures, KuCoin Futures, Gate, dYdX, Binance, Bybit |
| 24h open interest change, account long share | OKX, Binance, Bybit |
| Dated-futures basis | Deribit, OKX |
| Filled liquidations | OKX |
| Options (put/call, max pain, ATM IV, DVOL, large trades) | Deribit (BTC, ETH) |

Binance and Bybit refuse connections from US networks (HTTP 451/403). The tracker reports that and carries on with the other venues.

## Prerequisites

- Python 3.9 or newer. Standard library only: no packages to install, no API keys.
- Network access to the exchanges' public endpoints.

## Instructions

All commands run `python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py`. Every command accepts `--format json`, `--demo` (replays bundled recorded BTC data, marked on every line) and `--timeout SECONDS`.

1. **Funding rates** per venue, scaled to an 8-hour equivalent and a simple annual rate:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py funding BTC ETH
   python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py funding SOL --venues okx,hyperliquid,kraken
   ```

   Positive funding means longs pay shorts. Hourly venues (Hyperliquid, Kraken, dYdX) are multiplied by 8 so they compare with 8-hourly venues.

2. **Open interest** per venue, counted on one side, with 24-hour change in coins where the venue publishes hourly history:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py oi BTC
   ```

3. **Basis** for every dated future against the same venue's index:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py basis BTC
   ```

4. **Liquidations** filled on OKX over a look-back window (default 24 hours):

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py liquidations BTC --hours 12
   ```

5. **Options** on Deribit: per-expiry put/call ratios, max pain and ATM IV, DVOL rank, and optionally large recent trades:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py options BTC
   python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py options ETH --expiry 27NOV26 --large-trades 1000000  # 1000000 = minimum trade notional in USD
   ```

6. **Dashboard** with funding, open interest and a reference basis for several coins:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py dashboard BTC ETH SOL
   ```

7. **List venues** and what each provides: `derivatives_tracker.py venues`.

When summarizing results for the user, describe the data (for example "funding is positive on 6 of 7 venues") and keep the source and fetch time. Do not turn the figures into buy, sell or hold advice.

## Output

Console tables by default, ending with the sources used and the line "Research output only. Not financial advice. This tool places no trades." With `--format json`, every command returns one envelope:

```json
{"skill": "tracking-crypto-derivatives", "version": "2.0.0", "command": "funding",
 "symbols": ["BTC"], "generated_at": "2026-10-25T16:11:51Z", "mode": "live",
 "sources": ["https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP", "..."],
 "failures": [{"venue": "binance", "reason": "refused from this network (HTTP 451, region restriction)"}],
 "data": [...], "disclaimer": "Research output only. Not financial advice. This tool places no trades."}
```

See [`references/implementation.md`](references/implementation.md) for units, formulas and per-venue field mapping, and [`references/examples.md`](references/examples.md) for real output.

## Error Handling

| Message | Cause | What to do |
|---------|-------|------------|
| `refused from this network (HTTP 451/403 ...)` | The venue blocks your region (Binance, Bybit from the US) | Nothing; the other venues still report. Use `--venues` to skip it. |
| `rate limited (HTTP 429)` | Too many requests | Wait a minute and retry |
| `... not listed` | The venue has no market for that coin | Expected for smaller coins |
| `timed out after Ns` | Slow network or venue | Retry, or raise `--timeout` |
| `the bundled demo recording covers BTC only` | `--demo` with another coin | Run without `--demo` |
| Exit code 2 | No venue returned data | Check the "Unavailable" list |

More in [`references/errors.md`](references/errors.md).

## Examples

**Cross-venue funding check** (an excerpt of captured live output; full runs with their capture time are in `references/examples.md`, and live figures change every minute):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py funding BTC
```

```
kraken       PF_XBTUSD              +0.0015%     1h   +0.0119%   +13.08%      0h 49m
kucoin       XBTUSDTM               +0.0100%     8h   +0.0100%   +10.95%      7h 49m
okx          BTC-USDT-SWAP          +0.0054%     8h   +0.0054%    +5.97%      7h 49m
deribit      BTC-PERPETUAL          +0.0035%     8h   +0.0035%    +3.84%  continuous
dydx         BTC-USD                -0.0001%     1h   -0.0006%    -0.60%      0h 49m
Of 7 venues, funding is positive on 6, negative on 1.
```

**Term structure as JSON for further analysis:**

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py basis ETH --format json
```

**Try it offline:**

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/derivatives_tracker.py dashboard BTC --demo
```

## Resources

- [`references/implementation.md`](references/implementation.md): endpoints, units, formulas, what is not covered
- [`references/examples.md`](references/examples.md): real output for every command
- [`references/errors.md`](references/errors.md): error messages and fixes
- Tests: `python3 -m unittest discover -s tests -v` (offline, replays recorded responses)
- Refresh the demo recording: `python3 scripts/record_demo.py`
