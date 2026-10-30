# ARD: Crypto Derivatives Tracker

> Part of [Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)

## Architecture

```text
derivatives_tracker.py   command line, console tables, JSON envelope
  ├── perps.py           nine venue adapters → PerpSnapshot (funding, interval, one-sided OI)
  │                      24h OI history and account ratios (OKX, Binance, Bybit)
  ├── basis_data.py      dated futures vs index (Deribit, OKX)
  ├── liquidations.py    OKX filled liquidation orders, paged over the window
  ├── options_data.py    Deribit summaries → put/call, max pain, ATM IV; DVOL; large trades
  └── http_client.py     urllib requests, failure reasons, record/replay, one clock per run
```

## Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Data source | Exchange public REST endpoints, no keys | Buyers and free users can run it with nothing to configure; every figure is traceable to a URL |
| Default venues | Nine, including Binance and Bybit | They refuse US networks but serve most of the world; reporting the refusal is more honest than hiding them |
| HTTP | Standard library `urllib` + thread pool | No install step; parallel venue calls keep a run to a few seconds |
| Demo and tests | Replay recorded real responses through the same parsers | Offline runs exercise real parsing; random data would test nothing |
| Units | 8-hour funding equivalent; one-sided open interest | Venues differ (hourly vs 8-hourly; Bybit and Gate publish both-sides and one-side figures) |
| Failure handling | Per-venue `FetchError` with a plain reason; continue | One venue's outage or region block should not hide the others |
| Removed | Liquidation heatmap, simulated options flow, BitMEX | Not reproducible from public data; BitMEX refuses US and EU networks |

## Data flow

1. The command builds one `Http` client (live, recording, or replay).
2. Venue adapters run in parallel; each returns a normalized record or a failure.
3. Summaries are computed only from returned records.
4. Output: console table with sources and disclaimer, or one JSON envelope.

## Security

- Read-only: GET requests, plus Hyperliquid's public `info` POST.
- No credentials are read or accepted.
- `tests/test_derivatives_tracker.py::TestReadOnly` fails if any script references order, account, withdrawal, private or signing endpoints.

## Testing

`python3 -m unittest discover -s tests -v` replays `assets/demo-recording.json` (real BTC responses from a US network) and `tests/fixtures/binance-bybit-recording.json` (real responses recorded from a network those venues serve), plus hand-built payloads for unit conversions and max pain.
