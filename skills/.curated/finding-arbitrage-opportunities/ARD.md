# ARD: Arbitrage Opportunity Finder

> Part of [Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)

## Architecture

```text
arb_finder.py        command line, console tables, JSON envelope
  ├── spot_venues.py nine top-of-book adapters → Quote (bid, ask, sizes, fee + source)
  ├── spreads.py     cross-venue spread arithmetic; triangular search on one venue
  └── http_client.py urllib requests, failure reasons with error bodies, record/replay
```

## Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Data source | Public order-book and ticker endpoints, no keys | Traceable to a URL; nothing to configure |
| Pair matching | Exact pair only | USD, USDT and USDC markets differ by stablecoin rates, which are not arbitrage |
| Fees | Published base-tier taker fee per venue with source; Gate read live; unknown left unknown | A guessed fee would make the net column look precise when it is not |
| Size | Smaller of ask size and bid size at the best prices | A spread on 0.0002 BTC is not the same finding as one on 1 BTC |
| Not-listed detection | Read error bodies (Bitfinex returns 500, Gate and Binance 400 for unknown symbols) | Distinguishes "no market" from "exchange down" |
| HTTP | Standard library + thread pool | No install step; a scan takes about a second |
| Demo and tests | Replay recorded real responses through the same parsers | Exercises real parsing offline |
| Removed | DEX, cross-chain, execution code, flash loans, `MOCK_PRICES` | No keyless source for DEX quotes; execution is out of scope for a research tool |

## Security

- Read-only GET requests; no credentials accepted.
- `tests/test_arb_finder.py::TestReadOnly` fails if any script references order, account, withdrawal, private or signing endpoints, or makes a POST request.

## Testing

`python3 -m unittest discover -s tests -v` replays `assets/demo-recording.json` (real responses from a US network) and `tests/fixtures/binance-bybit-recording.json` (real Binance and Bybit responses recorded from a network they serve), plus hand-built quotes for the spread and triangle arithmetic.
