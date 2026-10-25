---
name: finding-arbitrage-opportunities
description: 'Compare live best bid and ask for one crypto pair across exchanges and
  report every cross-venue spread, gross and net of stated taker fees; search
  three-trade cycles within one exchange. Read-only, no API keys.

  Use when checking whether a coin trades at different prices on different
  exchanges, sizing a spread against fees, or looking for triangular price gaps on
  OKX, KuCoin or Gate.

  Trigger with phrases like "find arbitrage", "scan for arb", "price spread",
  "exchange price difference", "triangular arb", or "cross-exchange spread".

  '
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py:*)
argument-hint: "<scan BASE QUOTE | triangular VENUE | monitor BASE QUOTE>"
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- arbitrage
- order-book
compatibility: Designed for Claude Code
---
# Finding Arbitrage Opportunities

## Overview

Compare one exact pair's best bid and ask across nine exchanges and compute every cross-venue spread, gross and net of stated taker fees. A triangular search checks three-trade cycles inside one venue.

Venues: Kraken, Coinbase, KuCoin, Gate, OKX, Bitfinex, Crypto.com, Binance, Bybit. Binance and Bybit refuse US networks (HTTP 451/403); the tool names them and carries on.

Pairs with different quote assets are never compared: BTC/USD against BTC/USDT measures the USDT/USD rate, not an arbitrage.

## Prerequisites

- Python 3.9 or newer. Standard library only: no packages, no API keys.
- Network access to the exchanges' public endpoints.

## Instructions

All commands run `python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py`. Every command accepts `--format json`, `--fee VENUE=PERCENT` (the actual account taker fee), `--demo` (bundled recorded data, marked on every line) and `--timeout SECONDS`.

1. **Scan one pair across venues:**

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py scan BTC USDT
   python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py scan ETH USD --venues kraken,coinbase,bitfinex,gate
   ```

2. **Set actual account fees** (fees vary by tier, region and token discounts):

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py scan BTC USDT --fee coinbase=0.6 --fee kucoin=0.1
   ```

3. **Express the best net spread in money** for a trade size in base units:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py scan SOL USDT --amount 25  # 25 = trade size in SOL
   ```

4. **Search triangles on one venue** (okx, kucoin, gate), using pairs above a 24-hour volume floor:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py triangular okx
   python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py triangular kucoin --fee kucoin=0.1 --min-volume-usd 250000  # 250000 = USD volume floor
   ```

5. **Watch a pair** for a few minutes (minimum interval 5 seconds):

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py monitor BTC USDT --interval 15 --count 8 --threshold 0
   ```

6. **See fee assumptions and their sources:** `arb_finder.py venues`.

When reporting, give the spreads with the fee assumptions and the "not included" list below. Describe what the data shows; never recommend a trade.

## Output

Console tables end with sources and the line "Research output only. Not financial advice. This tool places no trades." JSON output is one envelope with `skill`, `version`, `command`, `generated_at`, `mode` (`live` or `demo`), `sources`, `failures`, `data`, `not_included` and `disclaimer`.

Every spread excludes withdrawal and network fees, the time to move funds between venues, price moves in that time, and depth beyond the best bid and ask. A positive net spread at the top of the book is not a collectable amount.

Fee assumptions are base-tier spot taker fees taken from each venue's published schedule (dates and sources in `arb_finder.py venues`). Gate's is read live from its API. KuCoin and Coinbase do not show a base-tier fee without a login, so their net column reads `n/a` until `--fee` sets it. Details: [`references/implementation.md`](references/implementation.md).

## Error Handling

| Message | Cause | What to do |
|---------|-------|------------|
| `refused from this network (HTTP 451/403 ...)` | Binance or Bybit blocks the region | Nothing; other venues still report |
| `BTC-USD not listed` (or similar) | The venue has no market for that exact pair | Try another quote asset (USD, USDT, USDC) |
| `no confirmed fee for kucoin` | Triangular search needs a fee | Pass `--fee kucoin=PERCENT` |
| `rate limited (HTTP 429)` | Too many requests | Raise `--interval`, wait a minute |
| `the bundled demo recording covers ...` | `--demo` with something not recorded | Run without `--demo` |
| Exit code 2 | No venue returned data | Read the "Unavailable" list |

More in [`references/errors.md`](references/errors.md).

## Examples

**Cross-venue BTC/USDT check** (an excerpt of captured live output; full runs with their capture time are in `references/examples.md`, and live figures change every minute):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py scan BTC USDT --top 3
```

```
Buy        Sell            Gross  Net of fees   Size at best
bitfinex   okx          +0.0293%     -0.3208%    1.35507 BTC
bitfinex   coinbase     +0.0291%          n/a     0.0109 BTC
bitfinex   cryptocom    +0.0258%     -0.4743%     0.3817 BTC
No venue pair stays positive after assumed taker fees.
```

**Triangles on OKX as JSON:**

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py triangular okx --format json
```

**Try it offline:**

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/arb_finder.py scan BTC USDT --demo
```

## Resources

- [`references/implementation.md`](references/implementation.md): endpoints, formulas, fee sources, what is not covered
- [`references/examples.md`](references/examples.md): real output for every command
- [`references/errors.md`](references/errors.md): error messages and fixes
- Tests: `python3 -m unittest discover -s tests -v` (offline)
- Refresh the demo recording: `python3 scripts/record_demo.py`
