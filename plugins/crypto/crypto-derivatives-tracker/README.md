# Crypto Derivatives Tracker Plugin

Read-only research on crypto perpetual swaps, dated futures and options, from live public exchange data. No API keys, no third-party packages, no trading.

## What it reports

| Command | What you get | Venues |
|---------|--------------|--------|
| `funding` | Funding per venue, 8-hour equivalent, simple annual rate, next payment | OKX, Deribit, Hyperliquid, Kraken Futures, KuCoin Futures, Gate, dYdX, Binance, Bybit |
| `oi` | One-sided open interest in coins and USD, share, 24h change, account long share | Same nine; history and ratios from OKX, Binance, Bybit |
| `basis` | Every dated future against its venue's index, annualized | Deribit, OKX |
| `liquidations` | Filled liquidations over a look-back window, by side, largest orders | OKX |
| `options` | Put/call ratios, max pain, ATM IV per expiry, DVOL rank, large trades | Deribit (BTC, ETH) |
| `dashboard` | Funding, open interest and a reference basis for several coins | All of the above |

Every figure is labelled with its source URL and fetch time. If a venue fails (Binance and Bybit refuse US networks, for example), it is listed with the reason and the rest still report. Nothing is estimated or simulated.

## Installation

```bash
/plugin install crypto-derivatives-tracker@claude-code-plugins-plus
```

Requires Python 3.9 or newer.

## Usage

Ask Claude about funding rates, open interest, futures basis, liquidations or BTC/ETH options, or run the script directly:

```bash
python3 skills/tracking-crypto-derivatives/scripts/derivatives_tracker.py funding BTC ETH
python3 skills/tracking-crypto-derivatives/scripts/derivatives_tracker.py oi BTC --format json
python3 skills/tracking-crypto-derivatives/scripts/derivatives_tracker.py options BTC --large-trades 1000000
python3 skills/tracking-crypto-derivatives/scripts/derivatives_tracker.py dashboard BTC --demo
```

`--demo` replays a bundled recording of real BTC responses for offline use; every line it prints starts with `[DEMO]`.

## Components

- **Skill** `tracking-crypto-derivatives`: the command-line tool, references and offline tests
- **Agent** `derivatives-agent`: runs the tool and summarizes results with sources

## Limits

- Liquidations cover OKX only. No liquidation heatmaps: those are vendor model estimates that public data cannot reproduce.
- Options cover Deribit BTC and ETH.
- Output describes market conditions. It is not financial advice and does not recommend trades.

## Changes in 2.0.0

Version 1.x generated funding rates, open interest, liquidations and options figures at random (`ExchangeClient(use_mock=True)`), and its live mode raised `NotImplementedError`. Version 2.0.0 replaces all of it with live public data, removes BitMEX (it refuses US and EU networks), removes the liquidation heatmap and simulated options flow, and drops documented flags that never existed.

## License

MIT
