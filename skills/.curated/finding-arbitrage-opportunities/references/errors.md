# Errors and Fixes

The finder never fills a gap with made-up prices. When a request fails, the venue appears under **Unavailable** with one of the reasons below and the remaining venues are still compared. The exit code is 2 when no venue returned a quote.

| Reason shown | Meaning | What to do |
|--------------|---------|------------|
| `refused from this network (HTTP 451, region restriction)` | Binance blocks your country or network | Expected from the US; other venues still report. |
| `refused from this network (HTTP 403, likely a region restriction)` | Bybit blocks your region or VPN exit | As above. |
| `{symbol} not listed` | That venue has no market for the exact pair | Try another quote asset: many venues list USDT but not USD, or the reverse. |
| `{symbol} book looks crossed or empty` | The venue returned a bid above its ask, or zero | Transient; retry. The venue is left out rather than trusted. |
| `rate limited (HTTP 429); wait and retry` | Too many requests | Wait a minute; use a longer `--interval` with `monitor`. |
| `timed out after Ns` | The venue did not answer in time | Retry or raise `--timeout`. |
| `network error: ...` | DNS, TLS or connection failure | Check your connection or proxy. |
| `unexpected response shape (...)` | The venue changed its API | Report it; that venue's adapter needs an update. |
| `no confirmed fee for kucoin; pass --fee kucoin=PERCENT` | Triangular search on a venue whose fee is unknown | Give your fee. |
| `could not read Gate's fee` | Gate's pair listing did not answer | Pass `--fee gate=PERCENT`. |
| `--fee okx=25 looks wrong` | A fee outside 0-5% | Give a percent such as `0.1`, not basis points. |
| `--interval must be at least 5 seconds` | `monitor` polling too fast | Public endpoints rate-limit; use 5 seconds or more. |
| `the bundled demo recording covers ...` | `--demo` with a pair or venue not recorded | Run without `--demo`. |
| `monitor needs live data` | `monitor --demo` | The recording is a single moment; run live. |

## Net shows n/a

The net column is `n/a` when either venue's fee is unknown (KuCoin and Coinbase by default). Pass `--fee kucoin=0.1` (or your actual rate) to fill it in.

## Checking a venue by hand

Every source URL is printed under **Sources** (console) or in `sources` (JSON):

```bash
curl -s "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT"
```
