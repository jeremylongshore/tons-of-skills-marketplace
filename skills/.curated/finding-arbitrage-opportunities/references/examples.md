# Examples

Real output, captured live from a US network on 2026-10-25 16:33 UTC. Binance and Bybit refuse US connections, so they appear under **Unavailable**; from other regions they appear in the tables. Prices change by the second; these show the format, not current values.

## `arb_finder.py scan BTC USDT --amount 0.5`

```text
============================================================================
 SCAN BTC USDT
 Live public data fetched 2026-10-25 16:33:55 UTC
============================================================================

BTC/USDT best bid and ask by venue
Venue      Symbol                  Bid            Ask  Book spread  Taker fee
----------------------------------------------------------------------------
bitfinex   tBTCUST              80,589         80,600      0.0136%      0.00%
kraken     XBTUSDT            80,597.6       80,598.8      0.0015%      0.80%
okx        BTC-USDT           80,599.9         80,600      0.0001%      0.35%
cryptocom  BTC_USDT             80,600         80,600      0.0000%      0.50%
gate       BTC_USDT           80,602.5       80,602.6      0.0001%      0.20%
kucoin     BTC-USDT           80,603.4       80,603.5      0.0001%    unknown
coinbase   BTC-USDT           80,599.5       80,608.8      0.0116%    unknown

Cross-venue spreads (buy at ask, sell at bid), top 10 by gross
Buy        Sell            Gross  Net of fees   Size at best
------------------------------------------------------------
kraken     kucoin       +0.0057%          n/a   0.219994 BTC
kraken     gate         +0.0046%     -0.9875%          1 BTC
okx        kucoin       +0.0042%          n/a   0.219994 BTC
bitfinex   kucoin       +0.0042%          n/a   0.219994 BTC
cryptocom  kucoin       +0.0042%          n/a     0.0552 BTC
okx        gate         +0.0031%     -0.5450%   0.658508 BTC
bitfinex   gate         +0.0031%     -0.1969%    1.89121 BTC
cryptocom  gate         +0.0031%     -0.6934%     0.0552 BTC
kraken     cryptocom    +0.0015%     -1.2882%    0.31215 BTC
kraken     okx          +0.0014%     -1.1395%   0.572447 BTC

For 0.5 BTC on kraken -> gate: net -397.96 USDT after assumed taker fees (before transfer costs).

Widest gross spread: buy kraken at 80,598.8, sell kucoin at 80,603.4 (+0.0057%).
No venue pair stays positive after assumed taker fees.
Net uses each venue's assumed taker fee (`venues` lists them); n/a means the fee is unknown,
set it with --fee VENUE=PERCENT. Not included: withdrawal and network fees, time to move funds between venues, price moves meanwhile, and depth beyond the best bid and ask.

Unavailable:
  binance: refused from this network (HTTP 451, region restriction)
  bybit: refused from this network (HTTP 403, likely a region restriction)

Sources:
  https://api.kraken.com/0/public/Ticker?pair=XBTUSDT
  https://api.exchange.coinbase.com/products/BTC-USDT/book?level=1
  https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=BTC-USDT
  https://api.gateio.ws/api/v4/spot/tickers?currency_pair=BTC_USDT
  https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT
  https://api-pub.bitfinex.com/v2/ticker/tBTCUST
  https://api.crypto.com/exchange/v1/public/get-book?instrument_name=BTC_USDT&depth=1

Research output only. Not financial advice. This tool places no trades.
```

## `arb_finder.py scan ETH USD --fee coinbase=0.6 --top 5`

```text
============================================================================
 SCAN ETH USD
 Live public data fetched 2026-10-25 16:34:07 UTC
============================================================================

ETH/USD best bid and ask by venue
Venue      Symbol                  Bid            Ask  Book spread  Taker fee
----------------------------------------------------------------------------
coinbase   ETH-USD             2,342.4       2,342.41      0.0004%      0.60%
kraken     ETHUSD             2,342.59        2,342.6      0.0004%      0.80%
gate       ETH_USD            2,343.04       2,343.06      0.0009%      0.20%
cryptocom  ETH_USD            2,343.34       2,343.35      0.0004%      0.50%
bitfinex   tETHUSD             2,344.6        2,344.9      0.0128%      0.00%

Cross-venue spreads (buy at ask, sell at bid), top 5 by gross
Buy        Sell            Gross  Net of fees   Size at best
------------------------------------------------------------
coinbase   bitfinex     +0.0935%     -0.5035% 0.00013437 ETH
kraken     bitfinex     +0.0854%     -0.7090%         26 ETH
gate       bitfinex     +0.0657%     -0.1340%    39.6125 ETH
cryptocom  bitfinex     +0.0533%     -0.4444%     0.7508 ETH
coinbase   cryptocom    +0.0397%     -1.0542% 0.00013437 ETH

Widest gross spread: buy coinbase at 2,342.41, sell bitfinex at 2,344.6 (+0.0935%).
No venue pair stays positive after assumed taker fees.
Net uses each venue's assumed taker fee (`venues` lists them); n/a means the fee is unknown,
set it with --fee VENUE=PERCENT. Not included: withdrawal and network fees, time to move funds between venues, price moves meanwhile, and depth beyond the best bid and ask.

Unavailable:
  kucoin: ETH-USD not listed
  okx: ETH-USD not listed
  binance: refused from this network (HTTP 451, region restriction)
  bybit: refused from this network (HTTP 403, likely a region restriction)

Sources:
  https://api.kraken.com/0/public/Ticker?pair=ETHUSD
  https://api.exchange.coinbase.com/products/ETH-USD/book?level=1
  https://api.gateio.ws/api/v4/spot/tickers?currency_pair=ETH_USD
  https://api-pub.bitfinex.com/v2/ticker/tETHUSD
  https://api.crypto.com/exchange/v1/public/get-book?instrument_name=ETH_USD&depth=1

Research output only. Not financial advice. This tool places no trades.
```

## `arb_finder.py triangular okx`

```text
============================================================================
 TRIANGULAR okx
 Live public data fetched 2026-10-25 16:34:09 UTC
============================================================================

Triangles on okx starting and ending in USDT
Pairs with at least $1,000,000 of 24h volume; taker fee 0.35% per leg (https://www.okx.com/fees (Regular user, as served to a US network))
Evaluated 16 triangles.

Path                                Gross  Net of fees
------------------------------------------------------
USDT -> USDC -> HYPE -> USDT     +0.0120%     -1.0345%
USDT -> ETH -> USDC -> USDT      +0.0072%     -1.0392%
USDT -> BTC -> USDC -> USDT      +0.0053%     -1.0411%
USDT -> USDC -> BTC -> USDT      -0.0066%     -1.0528%
USDT -> USDC -> ETH -> USDT      -0.0090%     -1.0553%
USDT -> USDC -> XRP -> USDT      -0.0139%     -1.0600%
USDT -> SOL -> USDC -> USDT      -0.0152%     -1.0614%
USDT -> USDC -> SOL -> USDT      -0.0154%     -1.0615%
USDT -> HYPE -> USDC -> USDT     -0.0168%     -1.0630%
USDT -> USDC -> ZEC -> USDT      -0.0174%     -1.0635%

No triangle stays positive after three taker fees.
Uses the best bid and ask of each pair at one moment; depth and latency are not included.

Sources:
  https://www.okx.com/api/v5/market/tickers?instType=SPOT

Research output only. Not financial advice. This tool places no trades.
```

## `arb_finder.py triangular kucoin --fee kucoin=0.1 --min-volume-usd 250000 --top 5`

```text
============================================================================
 TRIANGULAR kucoin
 Live public data fetched 2026-10-25 16:34:09 UTC
============================================================================

Triangles on kucoin starting and ending in USDT
Pairs with at least $250,000 of 24h volume; taker fee 0.10% per leg (set with --fee)
Evaluated 26 triangles.

Path                                Gross  Net of fees
------------------------------------------------------
USDT -> BTC -> USDC -> USDT      +0.0193%     -0.2805%
USDT -> ETH -> USDC -> USDT      +0.0177%     -0.2820%
USDT -> XRP -> USDC -> USDT      +0.0084%     -0.2913%
USDT -> SOL -> USDC -> USDT      +0.0018%     -0.2979%
USDT -> XMR -> USDC -> USDT      -0.0019%     -0.3016%

No triangle stays positive after three taker fees.
Uses the best bid and ask of each pair at one moment; depth and latency are not included.

Sources:
  https://api.kucoin.com/api/v1/market/allTickers

Research output only. Not financial advice. This tool places no trades.
```

## `arb_finder.py venues`

```text
============================================================================
 VENUES
 Live public data fetched 2026-10-25 16:34:10 UTC
============================================================================
Spot venues and assumed base-tier taker fees (checked 2026-10-25):
  kraken             0.80%  https://www.kraken.com/features/fee-schedule (Tier 1, $0+ 30-day volume)
  coinbase         unknown  not confirmed: Coinbase's schedule needs a login; pass --fee coinbase=PCT
  kucoin           unknown  not confirmed: KuCoin's base tier is not shown without login; pass --fee kucoin=PCT
  gate       live from API  https://api.gateio.ws/api/v4/spot/currency_pairs/{pair} (fee field, read live)
  okx                0.35%  https://www.okx.com/fees (Regular user, as served to a US network)
  bitfinex           0.00%  https://www.bitfinex.com/fees (spot taker: zero)
  cryptocom          0.50%  https://crypto.com/exchange/document/fees-limits (Level 1, no CRO balance)
  binance            0.10%  https://www.binance.com/en/fee/schedule (VIP 0, no BNB discount)
  bybit              0.10%  https://www.bybit.com/en/fee/spot (Regular user, crypto pairs)

Your real fee depends on your tier, region and token discounts; set it with --fee VENUE=PERCENT.
Binance and Bybit refuse US networks. Triangular search supports okx, kucoin and gate.
```

## `arb_finder.py monitor BTC USDT --interval 10 --count 3 --threshold 0`

```text
Scanning BTC/USDT every 10s, 3 times
Time (UTC) Venues  Widest gross (buy > sell)          Best net (buy > sell)              Flag
16:34:10        7  +0.0217% bitfinex > okx            -0.1790% bitfinex > gate
16:34:22        7  +0.0128% kucoin > cryptocom        -0.1960% bitfinex > gate
16:34:37        7  +0.0050% cryptocom > okx           -0.2010% bitfinex > gate

ABOVE marks a net spread at or above 0.0% after assumed taker fees.
Not included: withdrawal and network fees, time to move funds between venues, price moves meanwhile, and depth beyond the best bid and ask.
Research output only. Not financial advice. This tool places no trades.
```

## JSON output

```bash
arb_finder.py scan BTC USDT --format json --top 2
```

```json
{
  "skill": "finding-arbitrage-opportunities",
  "version": "2.0.0",
  "command": "scan",
  "subject": [
    "BTC",
    "USDT"
  ],
  "generated_at": "2026-10-25T16:34:47.655100Z",
  "mode": "live",
  "sources": [
    "https://api.kraken.com/0/public/Ticker?pair=XBTUSDT",
    "https://api.exchange.coinbase.com/products/BTC-USDT/book?level=1",
    "..."
  ],
  "failures": [
    {
      "venue": "binance",
      "reason": "refused from this network (HTTP 451, region restriction)"
    },
    {
      "venue": "bybit",
      "reason": "refused from this network (HTTP 403, likely a region restriction)"
    }
  ],
  "data": {
    "pair": "BTC/USDT",
    "quotes": [
      {
        "venue": "kucoin",
        "symbol": "BTC-USDT",
        "bid": 80627.9,
        "ask": 80628.0,
        "bid_size": 1.11068018,
        "ask_size": 0.49358235,
        "book_spread_pct": 0.0001240264697363889,
        "taker_fee_pct": null,
        "fee_source": "not confirmed: KuCoin's base tier is not shown without login; pass --fee kucoin=PCT",
        "latency_ms": 472,
        "source": "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=BTC-USDT"
      },
      {
        "venue": "gate",
        "symbol": "BTC_USDT",
        "bid": 80629.2,
        "ask": 80629.3,
        "bid_size": 3.743787,
        "ask_size": 3.092296,
        "book_spread_pct": 0.00012402447003515569,
        "taker_fee_pct": 0.2,
        "fee_source": "https://api.gateio.ws/api/v4/spot/currency_pairs/BTC_USDT (fee field, read live)",
        "latency_ms": 1323,
        "source": "https://api.gateio.ws/api/v4/spot/tickers?currency_pair=BTC_USDT"
      },
      "... one object per venue ..."
    ],
    "spreads": [
      {
        "buy_venue": "kucoin",
        "buy_ask": 80628.0,
        "sell_venue": "okx",
        "sell_bid": 80635.0,
        "gross_pct": 0.008681847497138406,
        "net_pct": null,
        "size_at_best_prices": 0.49358235
      },
      {
        "buy_venue": "gate",
        "buy_ask": 80629.3,
        "sell_venue": "okx",
        "sell_bid": 80635.0,
        "gross_pct": 0.007069390407710152,
        "net_pct": -0.5418716092402298,
        "size_at_best_prices": 1.5662543
      }
    ],
    "notes": [
      "Widest gross spread: buy kucoin at 80,628, sell okx at 80,635 (+0.0087%).",
      "No venue pair stays positive after assumed taker fees."
    ]
  },
  "not_included": "Not included: withdrawal and network fees, time to move funds between venues, price moves meanwhile, and depth beyond the best bid and ask.",
  "disclaimer": "Research output only. Not financial advice. This tool places no trades."
}
```
