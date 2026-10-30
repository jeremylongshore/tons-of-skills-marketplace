# Errors and Fixes

The tracker never fills a gap with made-up numbers. When a request fails, the venue appears under **Unavailable** with one of the reasons below, and the remaining venues are still reported. The exit code is 2 only when no venue returned data.

| Reason shown | Meaning | What to do |
|--------------|---------|------------|
| `refused from this network (HTTP 451, region restriction)` | Binance blocks your country or network | Expected from the US. Other venues cover the market; add `--venues` to skip it. |
| `refused from this network (HTTP 403, likely a region restriction)` | Bybit (and some others) block your region or a VPN exit | As above. |
| `rate limited (HTTP 429); wait and retry` | Too many requests in a short time | Wait a minute. Avoid running the dashboard in a tight loop. |
| `not found (HTTP 404); the symbol may not be listed here` | The URL or market does not exist | Check the coin symbol (`BTC`, not `BTCUSDT`). |
| `{instrument} not listed` | The venue has no perpetual or future for that coin | Normal for smaller coins. |
| `no dated {COIN} futures listed` | Neither Deribit nor OKX lists dated futures for the coin | Basis is available for BTC and ETH. |
| `timed out after Ns` | The venue did not answer in time | Retry, or raise `--timeout`. |
| `network error: ...` | DNS, TLS or connection failure | Check your connection or proxy. |
| `exchange error (HTTP 5xx)` | The venue is having problems | Try again later. |
| `unexpected response shape (...)` | The venue changed its response format | Report it; the parser for that venue needs an update. Other venues are unaffected. |
| `less than 24 hours of history` | A venue returned too few hourly points | The 24h change shows `n/a`. |
| `OKX returned no filled liquidations in the last N hours` | Quiet market or wrong symbol | Widen `--hours`, or check the coin. |
| `expiry XXX not listed; listed expiries: ...` | `--expiry` code not live on Deribit | Pick one from the list. |
| `the bundled demo recording covers BTC only` | `--demo` with another coin | Run without `--demo` for live data. |
| `not in the recorded demo data` | A `--demo` run asked for something the recording does not contain (for example `--venues` with an option the recording skipped) | Run without `--demo`. |

## Checking a venue by hand

Every source URL is printed under **Sources** (console) or in `sources` (JSON). Open one with `curl` to see the raw response:

```bash
curl -s "https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP"
```
