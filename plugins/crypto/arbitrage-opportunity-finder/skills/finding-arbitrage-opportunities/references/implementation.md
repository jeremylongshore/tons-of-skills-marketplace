# Implementation Reference

## Design

- **Public data only.** Unauthenticated GET requests to each exchange's order-book or ticker endpoint. No order, account, withdrawal or signing code; `tests/` checks that.
- **Like for like.** A scan compares one exact pair. BTC/USD and BTC/USDT are different markets: the gap between them is the USDT/USD rate.
- **No invented values.** A venue that fails, refuses the connection or does not list the pair is named with the reason. Spreads use only venues that answered.
- **Fees are stated, not hidden.** Every quote carries the fee assumed for it and where that number came from.
- **Standard library only.** `urllib` and a thread pool.
- **Recorded data is labelled.** `--demo` replays `assets/demo-recording.json` (real responses) through the same parsers; every console line starts with `[DEMO]`.

## Modules

| File | Role |
|------|------|
| `scripts/http_client.py` | Requests, failure reasons (with error bodies), recording and replay |
| `scripts/spot_venues.py` | Nine top-of-book adapters, fee assumptions with sources |
| `scripts/spreads.py` | Cross-venue spread arithmetic and the triangular search |
| `scripts/arb_finder.py` | Command line, console tables, JSON envelope |
| `scripts/record_demo.py` | Maintainer tool that refreshes the demo recording |

## Formulas

Cross-venue, buying at venue A's best ask and selling at venue B's best bid, with taker fees `fA`, `fB` as fractions:

```text
gross % = (bid_B / ask_A - 1) x 100
net %   = (bid_B x (1 - fB) / (ask_A x (1 + fA)) - 1) x 100
size    = min(ask size at A, bid size at B)          (base units)
```

Triangular, starting in asset S on one venue: for each pair X/Y the tool can sell X for Y at the bid, or buy X with Y at the ask (rate `1 / ask`). A cycle S → A → B → S multiplies the three rates; the net applies the taker fee to every leg, `× (1 − f)³`. Only pairs whose 24-hour volume, converted to USD through the venue's own USDT prices, is at least `--min-volume-usd` are used.

## Venue endpoints

| Venue | Endpoint | Symbol form |
|-------|----------|-------------|
| Kraken | `api.kraken.com/0/public/Ticker` | `XBTUSDT` (BTC is XBT) |
| Coinbase | `api.exchange.coinbase.com/products/{symbol}/book?level=1` | `BTC-USDT` |
| KuCoin | `api.kucoin.com/api/v1/market/orderbook/level1` | `BTC-USDT` |
| Gate | `api.gateio.ws/api/v4/spot/tickers` | `BTC_USDT` |
| OKX | `www.okx.com/api/v5/market/ticker` | `BTC-USDT` |
| Bitfinex | `api-pub.bitfinex.com/v2/ticker/{symbol}` | `tBTCUST` (USDT is UST, USDC is UDC) |
| Crypto.com | `api.crypto.com/exchange/v1/public/get-book?depth=1` | `BTC_USDT` |
| Binance | `api.binance.com/api/v3/ticker/bookTicker` | `BTCUSDT` |
| Bybit | `api.bybit.com/v5/market/tickers?category=spot` | `BTCUSDT` |

Triangular search reads full ticker lists: OKX `market/tickers?instType=SPOT`, KuCoin `market/allTickers`, Gate `spot/tickers`.

## Fee assumptions (checked 2026-10-25)

| Venue | Taker | Source |
|-------|-------|--------|
| Kraken | 0.80% | kraken.com/features/fee-schedule, Tier 1 ($0+ 30-day volume) |
| OKX | 0.35% | okx.com/fees, Regular user, as served to a US network; other regions may differ |
| Binance | 0.10% | binance.com/en/fee/schedule, VIP 0 without BNB discount |
| Bybit | 0.10% | bybit.com/en/fee/spot, Regular user, crypto pairs |
| Bitfinex | 0% | bitfinex.com/fees, spot taker "Zero" |
| Crypto.com | 0.50% | crypto.com/exchange/document/fees-limits, Level 1 without CRO balance |
| Gate | live | `fee` field of `api.gateio.ws/api/v4/spot/currency_pairs/{pair}` |
| KuCoin | unknown | base tier not shown without login; pass `--fee kucoin=PERCENT` |
| Coinbase | unknown | schedule needs a login; pass `--fee coinbase=PERCENT` |

Your fee depends on your tier, region and any token discount. Pass `--fee` for accurate net figures.

## Not covered, on purpose

- **Order execution of any kind.** The tool reads prices; it never trades.
- **DEX and cross-chain prices.** Reliable keyless DEX quotes need subgraph or RPC providers with keys; v1 listed them but returned a hard-coded table.
- **Withdrawal, network and transfer costs, transfer time, depth beyond the top of the book.** Stated in every report.

## Refreshing the demo recording

```bash
cd scripts && python3 record_demo.py
```

Records `scan BTC USDT`, `scan ETH USD` and `triangular okx` through one client and trims OKX's ticker list to assets with a liquid USDT market. Run the tests afterwards.
