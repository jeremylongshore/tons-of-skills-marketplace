# Arbitrage Opportunity Finder Plugin

Read-only comparison of live crypto prices across exchanges: best bid and ask for one exact pair on nine venues, every cross-venue spread gross and net of stated taker fees, and three-trade cycles within one venue. No API keys, no third-party packages, no trading.

## What it reports

| Command | What you get |
|---------|--------------|
| `scan BASE QUOTE` | Best bid and ask per venue, book spread, assumed taker fee; every buy-here/sell-there spread, gross and net, with size at the best prices |
| `triangular VENUE` | Three-trade cycles on OKX, KuCoin or Gate using pairs above a 24h volume floor, gross and net of three taker fees |
| `monitor BASE QUOTE` | The widest gross and best net spread, repeated on an interval |
| `venues` | Each venue's assumed fee and its source |

Venues: Kraken, Coinbase, KuCoin, Gate, OKX, Bitfinex, Crypto.com, Binance, Bybit. Binance and Bybit refuse US networks; the report names them and carries on.

Only identical pairs are compared. BTC/USD against BTC/USDT measures the USDT/USD rate, not an arbitrage.

## Installation

```bash
/plugin install arbitrage-opportunity-finder@claude-code-plugins-plus
```

Requires Python 3.9 or newer.

## Usage

Use `/find-arbitrage BTC USDT`, ask Claude about price differences between exchanges, or run the script:

```bash
python3 skills/finding-arbitrage-opportunities/scripts/arb_finder.py scan BTC USDT
python3 skills/finding-arbitrage-opportunities/scripts/arb_finder.py scan ETH USD --fee coinbase=0.6
python3 skills/finding-arbitrage-opportunities/scripts/arb_finder.py triangular okx --format json
python3 skills/finding-arbitrage-opportunities/scripts/arb_finder.py scan BTC USDT --demo
```

## Fees

Net spreads use each venue's published base-tier spot taker fee, or Gate's live API value. KuCoin and Coinbase do not publish a base-tier fee without a login, so their net shows `n/a` until you set `--fee kucoin=PERCENT` or `--fee coinbase=PERCENT`. Your actual fee depends on your tier, region and discounts; pass it with `--fee` for accurate figures.

## What is not included

Withdrawal and network fees, the time to move funds between venues, price moves in that time, and depth beyond the best bid and ask. A positive net spread at the top of the book is not money you can collect. Output is research, not financial advice.

## Changes in 2.0.0

Version 1.x read every price from a hard-coded table (`MOCK_PRICES`), including in its "live" mode; triangular results came from the same table, the documented `cross-chain` command did not exist, and the `/find-arbitrage` command carried trade-execution and flash-loan code. Version 2.0.0 reads live public order books, compares like-for-like pairs only, states every fee assumption and its source, and removes DEX, cross-chain and execution content.

## License

MIT
