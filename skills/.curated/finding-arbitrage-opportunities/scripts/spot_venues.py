#!/usr/bin/env python3
"""
Spot venues: best bid and ask from public order-book endpoints, plus fee assumptions.

Every adapter returns a `Quote` for one exact pair (for example BTC/USDT). Pairs
with different quote assets are never mixed: BTC/USD and BTC/USDT differ by the
USDT/USD exchange rate, which is not an arbitrage spread.

Fee assumptions are each venue's published base-tier spot taker fee, checked on
the date in FEES_CHECKED against the source listed. Real fees depend on your
account tier, region and token discounts; override them with --fee.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from http_client import FetchError, Http

FEES_CHECKED = "2026-10-25"


@dataclass(frozen=True)
class FeeAssumption:
    taker_pct: Optional[float]  # None: no published base-tier fee could be confirmed
    source: str


# Base-tier spot taker fees. Gate's comes from its API per pair at run time.
FEES: Dict[str, FeeAssumption] = {
    "kraken": FeeAssumption(0.80, "https://www.kraken.com/features/fee-schedule (Tier 1, $0+ 30-day volume)"),
    "okx": FeeAssumption(0.35, "https://www.okx.com/fees (Regular user, as served to a US network)"),
    "binance": FeeAssumption(0.10, "https://www.binance.com/en/fee/schedule (VIP 0, no BNB discount)"),
    "bybit": FeeAssumption(0.10, "https://www.bybit.com/en/fee/spot (Regular user, crypto pairs)"),
    "bitfinex": FeeAssumption(0.0, "https://www.bitfinex.com/fees (spot taker: zero)"),
    "cryptocom": FeeAssumption(0.50, "https://crypto.com/exchange/document/fees-limits (Level 1, no CRO balance)"),
    "gate": FeeAssumption(None, "https://api.gateio.ws/api/v4/spot/currency_pairs/{pair} (fee field, read live)"),
    "kucoin": FeeAssumption(
        None, "not confirmed: KuCoin's base tier is not shown without login; pass --fee kucoin=PCT"
    ),
    "coinbase": FeeAssumption(None, "not confirmed: Coinbase's schedule needs a login; pass --fee coinbase=PCT"),
}


@dataclass
class Quote:
    venue: str
    pair: str  # e.g. "BTC/USDT"
    symbol: str  # the venue's own symbol
    bid: float
    ask: float
    bid_size: Optional[float]  # base units at the best bid
    ask_size: Optional[float]
    taker_fee_pct: Optional[float]
    fee_source: str
    latency_ms: float
    source: str

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def spread_pct(self) -> float:
        return (self.ask - self.bid) / self.mid * 100


@dataclass
class VenueFailure:
    venue: str
    reason: str


def _not_listed(symbol: str) -> FetchError:
    return FetchError(f"{symbol} not listed")


def _kraken_asset(asset: str) -> str:
    return "XBT" if asset == "BTC" else asset


def _bitfinex_symbol(base: str, quote: str) -> str:
    q = {"USDT": "UST", "USDC": "UDC"}.get(quote, quote)
    return f"t{base}:{q}" if len(base) > 3 or len(q) > 3 else f"t{base}{q}"


def _book_top(levels) -> Tuple[float, float]:
    return float(levels[0][0]), float(levels[0][1])


# Each adapter returns (bid, ask, bid_size, ask_size, venue symbol, source url).
def _kraken(http: Http, base: str, quote: str):
    symbol = f"{_kraken_asset(base)}{quote}"
    url = f"https://api.kraken.com/0/public/Ticker?pair={symbol}"
    body = http.get_json(url)
    if body.get("error") or not body.get("result"):
        raise _not_listed(symbol)
    t = next(iter(body["result"].values()))
    return float(t["b"][0]), float(t["a"][0]), float(t["b"][2]), float(t["a"][2]), symbol, url


def _coinbase(http: Http, base: str, quote: str):
    symbol = f"{base}-{quote}"
    url = f"https://api.exchange.coinbase.com/products/{symbol}/book?level=1"
    try:
        body = http.get_json(url)
    except FetchError as exc:
        if exc.status in (400, 404):
            raise _not_listed(symbol) from None
        raise
    if not body.get("bids") or not body.get("asks"):
        raise _not_listed(symbol)
    (bid, bsz), (ask, asz) = _book_top(body["bids"]), _book_top(body["asks"])
    return bid, ask, bsz, asz, symbol, url


def _kucoin(http: Http, base: str, quote: str):
    symbol = f"{base}-{quote}"
    url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}"
    d = http.get_json(url).get("data")
    if not d or not d.get("bestBid"):
        raise _not_listed(symbol)
    return float(d["bestBid"]), float(d["bestAsk"]), float(d["bestBidSize"]), float(d["bestAskSize"]), symbol, url


def _gate(http: Http, base: str, quote: str):
    symbol = f"{base}_{quote}"
    url = f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={symbol}"
    try:
        rows = http.get_json(url)
    except FetchError as exc:
        if exc.status == 400:
            raise _not_listed(symbol) from None
        raise
    if not rows or not rows[0].get("highest_bid"):
        raise _not_listed(symbol)
    t = rows[0]
    return (
        float(t["highest_bid"]),
        float(t["lowest_ask"]),
        float(t["highest_size"]) if t.get("highest_size") else None,
        float(t["lowest_size"]) if t.get("lowest_size") else None,
        symbol,
        url,
    )


def _okx(http: Http, base: str, quote: str):
    symbol = f"{base}-{quote}"
    url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}"
    body = http.get_json(url)
    if body.get("code") != "0" or not body.get("data"):
        raise _not_listed(symbol)
    t = body["data"][0]
    return float(t["bidPx"]), float(t["askPx"]), float(t["bidSz"]), float(t["askSz"]), symbol, url


def _bitfinex(http: Http, base: str, quote: str):
    symbol = _bitfinex_symbol(base, quote)
    url = f"https://api-pub.bitfinex.com/v2/ticker/{symbol}"
    try:
        t = http.get_json(url)
    except FetchError as exc:
        if isinstance(exc.body, list) and exc.body[:1] == ["error"]:
            raise _not_listed(symbol) from None
        raise
    if not isinstance(t, list) or len(t) < 4:
        raise _not_listed(symbol)
    return float(t[0]), float(t[2]), float(t[1]), float(t[3]), symbol, url


def _cryptocom(http: Http, base: str, quote: str):
    symbol = f"{base}_{quote}"
    url = f"https://api.crypto.com/exchange/v1/public/get-book?instrument_name={symbol}&depth=1"
    try:
        body = http.get_json(url)
    except FetchError as exc:
        if exc.status == 400:
            raise _not_listed(symbol) from None
        raise
    data = (body.get("result") or {}).get("data") or []
    if body.get("code") != 0 or not data or not data[0].get("bids") or not data[0].get("asks"):
        raise _not_listed(symbol)
    (bid, bsz), (ask, asz) = _book_top(data[0]["bids"]), _book_top(data[0]["asks"])
    return bid, ask, bsz, asz, symbol, url


def _binance(http: Http, base: str, quote: str):
    symbol = f"{base}{quote}"
    url = f"https://api.binance.com/api/v3/ticker/bookTicker?symbol={symbol}"
    try:
        t = http.get_json(url)
    except FetchError as exc:
        if exc.status == 400:
            raise _not_listed(symbol) from None
        raise
    return float(t["bidPrice"]), float(t["askPrice"]), float(t["bidQty"]), float(t["askQty"]), symbol, url


def _bybit(http: Http, base: str, quote: str):
    symbol = f"{base}{quote}"
    url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
    body = http.get_json(url)
    rows = (body.get("result") or {}).get("list") or []
    if body.get("retCode") != 0 or not rows or not rows[0].get("bid1Price"):
        raise _not_listed(symbol)
    t = rows[0]
    return float(t["bid1Price"]), float(t["ask1Price"]), float(t["bid1Size"]), float(t["ask1Size"]), symbol, url


ADAPTERS: Dict[str, Callable] = {
    "kraken": _kraken,
    "coinbase": _coinbase,
    "kucoin": _kucoin,
    "gate": _gate,
    "okx": _okx,
    "bitfinex": _bitfinex,
    "cryptocom": _cryptocom,
    "binance": _binance,
    "bybit": _bybit,
}


def gate_fee(http: Http, base: str, quote: str) -> Optional[float]:
    """Gate publishes each pair's fee (percent) in its public pair listing."""
    try:
        return float(http.get_json(f"https://api.gateio.ws/api/v4/spot/currency_pairs/{base}_{quote}")["fee"])
    except (FetchError, KeyError, TypeError, ValueError):
        return None


def fetch_quote(http: Http, venue: str, base: str, quote: str, fee_overrides: Dict[str, float]) -> Quote:
    started = time.monotonic()
    bid, ask, bsz, asz, symbol, url = ADAPTERS[venue](http, base, quote)
    latency = 0.0 if http.is_replay else (time.monotonic() - started) * 1000
    if bid <= 0 or ask <= 0 or ask < bid:
        raise FetchError(f"{symbol} book looks crossed or empty (bid {bid}, ask {ask})")
    if venue in fee_overrides:
        fee, fee_source = fee_overrides[venue], "set with --fee"
    elif venue == "gate":
        fee, fee_source = gate_fee(http, base, quote), FEES["gate"].source.replace("{pair}", symbol)
    else:
        fee, fee_source = FEES[venue].taker_pct, FEES[venue].source
    return Quote(venue, f"{base}/{quote}", symbol, bid, ask, bsz, asz, fee, fee_source, latency, url)


def fetch_quotes(
    http: Http,
    base: str,
    quote: str,
    venues: Optional[List[str]] = None,
    fee_overrides: Optional[Dict[str, float]] = None,
) -> Tuple[List[Quote], List[VenueFailure]]:
    names = venues or list(ADAPTERS)
    overrides = fee_overrides or {}
    quotes: List[Quote] = []
    failures: List[VenueFailure] = []

    def one(name: str):
        try:
            return fetch_quote(http, name, base, quote, overrides), None
        except FetchError as exc:
            return None, VenueFailure(name, exc.reason)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            return None, VenueFailure(name, f"unexpected response shape ({type(exc).__name__}: {exc})")

    with ThreadPoolExecutor(max_workers=len(names)) as pool:
        for q, f in pool.map(one, names):
            if q is not None:
                quotes.append(q)
            if f is not None:
                failures.append(f)
    return quotes, failures
