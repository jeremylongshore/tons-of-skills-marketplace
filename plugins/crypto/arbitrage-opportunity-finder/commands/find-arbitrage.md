---
name: find-arbitrage
description: >
  Compare live crypto bid/ask across exchanges; spreads net of stated fees
shortcut: fa
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/skills/finding-arbitrage-opportunities/scripts/arb_finder.py:*)
---
# Find Arbitrage Spreads

Run the `finding-arbitrage-opportunities` skill's scanner and summarize the result. The scanner reads public order-book data only; it never places orders and needs no API keys.

## Usage

```text
/find-arbitrage BTC USDT
/find-arbitrage ETH USD --fee coinbase=0.6
/find-arbitrage triangular okx
```

## Steps

1. Run the scanner bundled with this plugin:

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/finding-arbitrage-opportunities/scripts/arb_finder.py scan BTC USDT
   ```

   - Pair given (`BTC USDT`): `scan BASE QUOTE` plus any `--fee`, `--venues`, `--amount` the user supplied.
   - `triangular VENUE`: `triangular VENUE` (okx, kucoin or gate).
   - No arguments: ask which pair, or run `scan BTC USDT`.

2. Report:
   - The widest gross spread and the best net spread, with the venues and the fee assumed for each.
   - Venues listed as unavailable, with the reason (Binance and Bybit refuse US networks).
   - What is not included: withdrawal and network fees, transfer time, price moves meanwhile, depth beyond the best bid and ask.
   - The fetch time and the closing line "Research output only. Not financial advice."

Describe the spreads; do not recommend trading them. If net figures show `n/a`, explain that the venue's fee is unknown and how to set it with `--fee VENUE=PERCENT`.
