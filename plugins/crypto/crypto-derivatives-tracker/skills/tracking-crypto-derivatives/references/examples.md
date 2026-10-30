# Examples

Real output, captured live from a US network on 2026-10-25 16:14 UTC. Binance and Bybit refuse US connections, so they appear under **Unavailable**; from other regions they appear in the tables. Figures change every minute; these are a record of format, not current values.

## `derivatives_tracker.py funding BTC`

```text
========================================================================
 FUNDING BTC
 Live public data fetched 2026-10-25 16:14 UTC
========================================================================

BTC perpetual funding
Venue        Instrument                 Rate  Every   8h equiv    Annual        Next
------------------------------------------------------------------------------------
kraken       PF_XBTUSD              +0.0015%     1h   +0.0119%   +13.08%      0h 45m
kucoin       XBTUSDTM               +0.0100%     8h   +0.0100%   +10.95%      7h 45m
gate         BTC_USDT               +0.0068%     8h   +0.0068%    +7.45%      7h 45m
hyperliquid  BTC                    +0.0008%     1h   +0.0068%    +7.43%      0h 45m
okx          BTC-USDT-SWAP          +0.0055%     8h   +0.0055%    +5.99%      7h 45m
deribit      BTC-PERPETUAL          +0.0035%     8h   +0.0035%    +3.85%  continuous
dydx         BTC-USD                -0.0000%     1h   -0.0004%    -0.40%      0h 45m
------------------------------------------------------------------------------------
Mean 8h equivalent: +0.0063%   Median: +0.0068%
Weighted by open interest: +0.0066%
Highest: kraken +0.0119%   Lowest: dydx -0.0004%   Spread: 0.0123%
Of 7 venues, funding is positive on 6, negative on 1.

Unavailable:
  BTC binance: refused from this network (HTTP 451, region restriction)
  BTC bybit: refused from this network (HTTP 403, likely a region restriction)

Positive funding: longs pay shorts. Annual figures are simple (rate x periods per year).

Sources:
  https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP
  https://www.deribit.com/api/v2/public/ticker?instrument_name=BTC-PERPETUAL
  https://api.hyperliquid.xyz/info metaAndAssetCtxs
  https://futures.kraken.com/derivatives/api/v3/tickers/PF_XBTUSD
  https://api-futures.kucoin.com/api/v1/contracts/XBTUSDTM
  https://api.gateio.ws/api/v4/futures/usdt/contracts/BTC_USDT
  https://indexer.dydx.trade/v4/perpetualMarkets?ticker=BTC-USD

Research output only. Not financial advice. This tool places no trades.
```

## `derivatives_tracker.py oi BTC`

```text
========================================================================
 OI BTC
 Live public data fetched 2026-10-25 16:15 UTC
========================================================================

BTC perpetual open interest (one side)
Venue                 Coins          USD   Share   24h chg  Accts long
----------------------------------------------------------------------
hyperliquid       42,229.99       $3.40B   34.2%       n/a         n/a
okx               30,080.47       $2.42B   24.3%    -1.30%       67.2%
gate              27,817.61       $2.24B   22.5%       n/a         n/a
deribit           10,454.78     $841.90M    8.5%       n/a         n/a
kucoin            10,151.41     $818.14M    8.2%       n/a         n/a
kraken             2,610.71     $210.18M    2.1%       n/a         n/a
dydx                 209.95      $16.91M    0.2%       n/a         n/a
----------------------------------------------------------------------
Total across 7 venues: $9.95B
24h change is measured in coins, so price moves do not count. n/a: the venue
publishes no hourly history (or account ratio) for this instrument.

Unavailable:
  binance: refused from this network (HTTP 451, region restriction)
  bybit: refused from this network (HTTP 403, likely a region restriction)
  binance (24h history): refused from this network (HTTP 451, region restriction)
  bybit (24h history): refused from this network (HTTP 403, likely a region restriction)
  binance (account ratio): refused from this network (HTTP 451, region restriction)
  bybit (account ratio): refused from this network (HTTP 403, likely a region restriction)

Sources:
  https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP
  https://www.deribit.com/api/v2/public/ticker?instrument_name=BTC-PERPETUAL
  https://api.hyperliquid.xyz/info metaAndAssetCtxs
  https://futures.kraken.com/derivatives/api/v3/tickers/PF_XBTUSD
  https://api-futures.kucoin.com/api/v1/contracts/XBTUSDTM
  https://api.gateio.ws/api/v4/futures/usdt/contracts/BTC_USDT
  https://indexer.dydx.trade/v4/perpetualMarkets?ticker=BTC-USD
  https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-history?instId=BTC-USDT-SWAP&period=1H&limit=25
  https://www.okx.com/api/v5/rubik/stat/contracts/long-short-account-ratio-contract?instId=BTC-USDT-SWAP&period=1H&limit=1

Research output only. Not financial advice. This tool places no trades.
```

## `derivatives_tracker.py basis ETH`

```text
========================================================================
 BASIS ETH
 Live public data fetched 2026-10-25 16:15 UTC
========================================================================

ETH dated-futures basis against each venue's index
Venue     Instrument         Days      Futures        Index     Basis    Annual
------------------------------------------------------------------------------
deribit   ETH-26OCT26         0.7     2,343.21     2,343.68   -0.020%   -11.15%
deribit   ETH-27OCT26         1.7     2,343.51     2,343.68   -0.007%    -1.60%
deribit   ETH-28OCT26         2.7     2,343.87     2,343.68   +0.008%    +1.11%
deribit   ETH-29OCT26         3.7     2,344.11     2,343.68   +0.018%    +1.83%
deribit   ETH-30OCT26         4.7     2,344.26     2,343.68   +0.025%    +1.94%
okx       ETH-USD-261030      4.7     2,344.03     2,343.45   +0.025%    +1.94%
deribit   ETH-6NOV26         11.7     2,345.55     2,343.68   +0.080%    +2.50%
deribit   ETH-13NOV26        18.7     2,346.87     2,343.68   +0.136%    +2.66%
deribit   ETH-27NOV26        32.7     2,349.78     2,343.68   +0.260%    +2.91%
okx       ETH-USD-261127     32.7     2,350.74     2,343.45   +0.311%    +3.48%
deribit   ETH-25DEC26        60.7     2,358.42     2,343.68   +0.629%    +3.78%
okx       ETH-USD-261225     60.7     2,358.88     2,343.45   +0.658%    +3.96%
deribit   ETH-26MAR27       151.7     2,384.55     2,343.68   +1.744%    +4.20%
okx       ETH-USD-270326    151.7     2,385.34     2,343.45   +1.787%    +4.30%
deribit   ETH-25JUN27       242.7     2,414.94     2,343.68   +3.041%    +4.57%
okx       ETH-USD-270625    242.7     2,414.77     2,343.45   +3.044%    +4.58%
deribit   ETH-24SEP27       333.7     2,444.68     2,343.68   +4.309%    +4.71%
okx       ETH-USD-270924    333.7     2,442.85     2,343.45   +4.241%    +4.64%
------------------------------------------------------------------------------
16 of 18 dated futures trade above their index.
Annual figures scale the basis by days to expiry (simple, not compounded).
Expiries less than 12 hours away are left out.

Sources:
  https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=ETH&kind=future
  https://www.okx.com/api/v5/market/tickers?instType=FUTURES&uly=ETH-USD

Research output only. Not financial advice. This tool places no trades.
```

## `derivatives_tracker.py liquidations BTC`

```text
========================================================================
 LIQUIDATIONS BTC
 Live public data fetched 2026-10-25 16:15 UTC
========================================================================

BTC-USDT-SWAP filled liquidations on OKX
Window: 2026-10-24 16:16 to 2026-10-25 15:02 UTC
  Longs liquidated:    246 orders        $1.30M
  Shorts liquidated:   435 orders        $5.08M

Largest:
  10-24 16:50  short     10.0000 @    80,105.00    $801.05K
  10-24 16:49  short     10.0000 @    79,961.70    $799.62K
  10-24 23:31  short      5.6254 @    80,646.90    $453.67K
  10-24 23:32  short      3.8403 @    80,738.30    $310.06K
  10-25 09:13  long       3.7401 @    80,192.10    $299.93K

OKX only: it is the venue here with a public liquidation feed. Other venues'
liquidations are not included, so this is a partial view of the market.

Sources:
  https://www.okx.com/api/v5/public/liquidation-orders?instType=SWAP&uly=BTC-USDT&state=filled&limit=100

Research output only. Not financial advice. This tool places no trades.
```

## `derivatives_tracker.py options BTC --expiries 4 --large-trades 2000000`

```text
========================================================================
 OPTIONS BTC
 Live public data fetched 2026-10-25 16:15 UTC
========================================================================

BTC options on Deribit (open interest and volume in BTC)
Expiry     Underlying    Call OI     Put OI  P/C OI  P/C vol  ATM IV   Max pain  vs und.
----------------------------------------------------------------------------------------
26OCT26        80,508    1,459.4    1,600.0    1.10     1.65   32.7%     81,000    +0.6%
27OCT26        80,521      706.2      638.5    0.90     2.14   33.7%     81,000    +0.6%
28OCT26        80,543      394.2      361.3    0.92     0.97   33.5%     80,500    -0.1%
29OCT26        80,545      105.2      111.6    1.06     1.06   33.9%     80,500    -0.1%
----------------------------------------------------------------------------------------
Put/call ratio by open interest, all live expiries: 0.60
DVOL (30-day implied volatility index): 38.4   365-day range 33.6-82.6   rank 10   percentile 29
Max pain: the settlement price at which option holders' total intrinsic value is smallest.

Largest option trades among Deribit's last 1000, notional >= $2.00M
  10-25 14:23 BTC-27OCT26-79000-P    taker buy     200.0 notional    $16.05M premium    $72.21K IV 38.59  block
  10-25 14:22 BTC-26OCT26-79500-P    taker buy     200.0 notional    $16.04M premium    $54.55K IV 39.45  block
  10-25 14:04 BTC-26OCT26-83000-C    taker buy     100.0 notional     $8.02M premium     $2.41K IV 42.25
  10-25 10:10 BTC-6NOV26-70000-P     taker sell     75.0 notional     $6.02M premium    $15.65K IV 51.54  block
  10-25 13:59 BTC-26OCT26-77000-P    taker buy      70.0 notional     $5.62M premium     $1.69K IV 50.57
  10-25 11:56 BTC-27NOV26-67000-P    taker sell     50.0 notional     $4.03M premium    $24.55K IV 48.54  block
  10-25 10:03 BTC-30OCT26-80000-P    taker buy      50.0 notional     $4.01M premium    $56.96K IV 34.64  block
  10-25 10:03 BTC-27OCT26-80000-P    taker sell     50.0 notional     $4.01M premium    $32.49K IV 33.19  block
  10-25 10:10 BTC-6NOV26-77000-P     taker buy      37.5 notional     $3.01M premium    $37.62K IV 41.02  block
  10-25 15:09 BTC-27NOV26-64000-P    taker sell     30.0 notional     $2.42M premium     $9.19K IV 51.61

Sources:
  https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option
  https://www.deribit.com/api/v2/public/get_volatility_index_data (BTC DVOL, daily)
  https://www.deribit.com/api/v2/public/get_last_trades_by_currency (BTC options, last 1000)

Research output only. Not financial advice. This tool places no trades.
```

## `derivatives_tracker.py dashboard BTC ETH SOL`

```text
========================================================================
 DASHBOARD BTC ETH SOL
 Live public data fetched 2026-10-25 16:15 UTC
========================================================================

--- BTC ---
Funding (8h equiv): mean +0.0062%, weighted by open interest +0.0065% across 7 venues
  Of 7 venues, funding is positive on 6, negative on 1.
Open interest (one side): $9.95B across 7 venues
Basis: BTC-27NOV26 (deribit, 33 days) +5.27% annualized. Every dated future trades above its index (contango).

--- ETH ---
Funding (8h equiv): mean +0.0050%, weighted by open interest +0.0065% across 7 venues
  Of 7 venues, funding is positive on 5, negative on 0, zero on 2.
Open interest (one side): $5.68B across 7 venues
Basis: ETH-27NOV26 (deribit, 33 days) +2.94% annualized. 16 of 18 dated futures trade above their index.

--- SOL ---
Funding (8h equiv): mean +0.0050%, weighted by open interest +0.0022% across 7 venues
  Of 7 venues, funding is positive on 5, negative on 1, zero on 1.
Open interest (one side): $1.45B across 7 venues
Basis: no dated futures listed

Unavailable:
  BTC binance: refused from this network (HTTP 451, region restriction)
  BTC bybit: refused from this network (HTTP 403, likely a region restriction)
  ETH binance: refused from this network (HTTP 451, region restriction)
  ETH bybit: refused from this network (HTTP 403, likely a region restriction)
  SOL binance: refused from this network (HTTP 451, region restriction)
  SOL bybit: refused from this network (HTTP 403, likely a region restriction)
  SOL deribit: no dated SOL futures listed
  SOL okx: no dated SOL futures listed

Sources:
  https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP
  https://www.deribit.com/api/v2/public/ticker?instrument_name=BTC-PERPETUAL
  https://api.hyperliquid.xyz/info metaAndAssetCtxs
  https://futures.kraken.com/derivatives/api/v3/tickers/PF_XBTUSD
  https://api-futures.kucoin.com/api/v1/contracts/XBTUSDTM
  https://api.gateio.ws/api/v4/futures/usdt/contracts/BTC_USDT
  https://indexer.dydx.trade/v4/perpetualMarkets?ticker=BTC-USD
  https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=future
  https://www.okx.com/api/v5/market/tickers?instType=FUTURES&uly=BTC-USD
  https://www.okx.com/api/v5/public/funding-rate?instId=ETH-USDT-SWAP
  https://www.deribit.com/api/v2/public/ticker?instrument_name=ETH-PERPETUAL
  https://futures.kraken.com/derivatives/api/v3/tickers/PF_ETHUSD
  https://api-futures.kucoin.com/api/v1/contracts/ETHUSDTM
  https://api.gateio.ws/api/v4/futures/usdt/contracts/ETH_USDT
  https://indexer.dydx.trade/v4/perpetualMarkets?ticker=ETH-USD
  https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=ETH&kind=future
  https://www.okx.com/api/v5/market/tickers?instType=FUTURES&uly=ETH-USD
  https://www.okx.com/api/v5/public/funding-rate?instId=SOL-USDT-SWAP
  https://www.deribit.com/api/v2/public/ticker?instrument_name=SOL_USDC-PERPETUAL
  https://futures.kraken.com/derivatives/api/v3/tickers/PF_SOLUSD
  https://api-futures.kucoin.com/api/v1/contracts/SOLUSDTM
  https://api.gateio.ws/api/v4/futures/usdt/contracts/SOL_USDT
  https://indexer.dydx.trade/v4/perpetualMarkets?ticker=SOL-USD

Research output only. Not financial advice. This tool places no trades.
```

## JSON output

```bash
derivatives_tracker.py funding BTC --format json
```

```json
{
  "skill": "tracking-crypto-derivatives",
  "version": "2.0.0",
  "command": "funding",
  "symbols": [
    "BTC"
  ],
  "generated_at": "2026-10-25T16:15:21.383488Z",
  "mode": "live",
  "sources": [
    "https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP",
    "https://www.deribit.com/api/v2/public/ticker?instrument_name=BTC-PERPETUAL",
    "..."
  ],
  "failures": [
    {
      "venue": "BTC binance",
      "reason": "refused from this network (HTTP 451, region restriction)"
    },
    {
      "venue": "BTC bybit",
      "reason": "refused from this network (HTTP 403, likely a region restriction)"
    }
  ],
  "data": [
    {
      "symbol": "BTC",
      "venues": [
        {
          "venue": "okx",
          "instrument": "BTC-USDT-SWAP",
          "funding_rate": 5.48685337851e-05,
          "interval_hours": 8.0,
          "rate_8h": 5.48685337851e-05,
          "annualized_pct": 6.00810444946845,
          "next_funding": "2026-10-26 00:00:00+00:00",
          "mark_price": 80579.9,
          "index_price": null,
          "open_interest_base": 30080.454900000084,
          "open_interest_usd": 2423880047.7965164,
          "source": "https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP"
        },
        {
          "venue": "deribit",
          "instrument": "BTC-PERPETUAL",
          "funding_rate": 3.523e-05,
          "interval_hours": 8.0,
          "rate_8h": 3.523e-05,
          "annualized_pct": 3.8576850000000005,
          "next_funding": null,
          "mark_price": 80533.91,
          "index_price": 80508.03,
          "open_interest_base": 10453.606809851899,
          "open_interest_usd": 841869830.0,
          "source": "https://www.deribit.com/api/v2/public/ticker?instrument_name=BTC-PERPETUAL"
        },
        "... one object per venue ..."
      ],
      "summary": {
        "venues": 7,
        "mean_rate_8h": 6.241294768358534e-05,
        "median_rate_8h": 6.4e-05,
        "oi_weighted_rate_8h": 6.438732783227242e-05,
        "highest": "kraken",
        "lowest": "dydx",
        "spread_8h": 0.00012311263333333064,
        "notes": [
          "Of 7 venues, funding is positive on 6, negative on 1."
        ]
      }
    }
  ],
  "disclaimer": "Research output only. Not financial advice. This tool places no trades."
}
```

## Demo mode

```text
[DEMO] ========================================================================
[DEMO]  FUNDING BTC
[DEMO]  Recorded data from 2026-10-25 16:11 UTC, not live. Run without --demo for live data.
[DEMO] ========================================================================
[DEMO]
[DEMO] BTC perpetual funding
[DEMO] Venue        Instrument                 Rate  Every   8h equiv    Annual        Next
[DEMO] ------------------------------------------------------------------------------------
[DEMO] kraken       PF_XBTUSD              +0.0015%     1h   +0.0119%   +13.08%      0h 48m
[DEMO] kucoin       XBTUSDTM               +0.0100%     8h   +0.0100%   +10.95%      7h 48m
[DEMO] hyperliquid  BTC                    +0.0009%     1h   +0.0074%    +8.09%      0h 48m
[DEMO] gate         BTC_USDT               +0.0071%     8h   +0.0071%    +7.77%      7h 48m
...
```
