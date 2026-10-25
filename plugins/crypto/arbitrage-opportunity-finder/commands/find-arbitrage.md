---
name: find-arbitrage
description: >
  Compare live crypto bid/ask across exchanges; spreads net of stated fees
shortcut: fa
argument-hint: "<BASE> <QUOTE> [--fee VENUE=PCT] [--venues LIST] [--amount N] | triangular <VENUE>"
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

## Arguments

User-supplied arguments: $ARGUMENTS

## Steps

1. Decide the scanner command from the arguments above:
   - `BASE QUOTE [flags]` (for example `ETH USD --fee coinbase=0.6`): `scan BASE QUOTE` followed by the supported flags exactly as given (`--fee`, `--venues`, `--amount`, `--top`, `--format`).
   - `triangular VENUE [flags]`: `triangular VENUE` (okx, kucoin or gate) followed by `--fee`, `--min-volume-usd`, `--top` as given.
   - No arguments: ask the user which pair to scan before running anything.
   - Anything else: show the accepted forms above and ask again. Pass only these documented subcommands and flags, never other text.

2. Run the scanner bundled with this plugin, for example:

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/finding-arbitrage-opportunities/scripts/arb_finder.py scan ETH USD --fee coinbase=0.6
   ```

3. Report what the output shows, by mode:
   - **scan:** the widest gross spread and the best net spread, with their venues and the fee assumed for each; the size available at the best prices; and the venues listed under "Unavailable" with the reason the tool gives (which venues fail depends on the user's network).
   - **triangular:** the venue, the volume floor and the per-leg fee used, the number of triangles evaluated, and the best cycles with their gross and net results. Say plainly when no cycle stays positive after fees.
   - **Both:** what is not included (withdrawal and network fees, transfer time, price moves meanwhile, depth beyond the best bid and ask), the fetch time, and the closing line "Research output only. Not financial advice."

Describe the results; do not recommend trading them. If net figures show `n/a`, explain that the venue's fee is unknown and how to set it with `--fee VENUE=PERCENT`. For repeated scans over time, point the user to the skill's `monitor` subcommand.
