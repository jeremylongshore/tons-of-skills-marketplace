#!/usr/bin/env python3
"""
Spread arithmetic on live quotes: cross-venue spreads and same-venue triangles.

Cross-venue: buying at venue A's best ask and selling at venue B's best bid.

    gross % = (bid_B / ask_A - 1) x 100
    net %   = (bid_B x (1 - fee_B) / (ask_A x (1 + fee_A)) - 1) x 100

Both legs are assumed to be taker orders. Not included, and stated in every
report: withdrawal and network fees, the time to move funds between venues,
price movement while you do, and depth beyond the best bid and ask.

Triangular: three trades on one venue that start and end in the same asset,
using each pair's best bid or ask and the venue's taker fee on every leg.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Dict, List, Optional, Tuple

from http_client import FetchError, Http
from spot_venues import Quote


@dataclass
class CrossSpread:
    buy: Quote
    sell: Quote

    @property
    def gross_pct(self) -> float:
        return (self.sell.bid / self.buy.ask - 1.0) * 100.0

    @property
    def net_pct(self) -> Optional[float]:
        if self.buy.taker_fee_pct is None or self.sell.taker_fee_pct is None:
            return None
        cost = self.buy.ask * (1 + self.buy.taker_fee_pct / 100)
        proceeds = self.sell.bid * (1 - self.sell.taker_fee_pct / 100)
        return (proceeds / cost - 1.0) * 100.0

    @property
    def top_size(self) -> Optional[float]:
        """Base units available at both best prices (the smaller side)."""
        if self.buy.ask_size is None or self.sell.bid_size is None:
            return None
        return min(self.buy.ask_size, self.sell.bid_size)


def cross_spreads(quotes: List[Quote]) -> List[CrossSpread]:
    """Every ordered venue pair, best gross spread first."""
    pairs = [CrossSpread(a, b) for a, b in permutations(quotes, 2)]
    return sorted(pairs, key=lambda s: s.gross_pct, reverse=True)


def describe(spreads: List[CrossSpread]) -> List[str]:
    """Plain statements about the spreads; no recommendation."""
    if not spreads:
        return ["Fewer than two venues returned a quote; no spread to compare."]
    best = spreads[0]
    notes = []
    if best.gross_pct <= 0:
        notes.append("No venue's best bid is above another venue's best ask: books overlap.")
    else:
        notes.append(
            f"Widest gross spread: buy {best.buy.venue} at {best.buy.ask:,.6g}, "
            f"sell {best.sell.venue} at {best.sell.bid:,.6g} ({best.gross_pct:+.4f}%)."
        )
    with_net = [s for s in spreads if s.net_pct is not None]
    positive = [s for s in with_net if s.net_pct > 0]
    if with_net:
        if positive:
            notes.append(
                f"{len(positive)} venue pair(s) stay positive after assumed taker fees, "
                "before withdrawal fees and transfer time."
            )
        else:
            notes.append("No venue pair stays positive after assumed taker fees.")
    return notes


# ---------------------------------------------------------------------------
# Triangular (one venue)
# ---------------------------------------------------------------------------


@dataclass
class Book:
    base: str
    quote: str
    bid: float
    ask: float
    quote_volume: float


@dataclass
class Triangle:
    path: Tuple[str, str, str, str]  # e.g. ("USDT", "BTC", "ETH", "USDT")
    legs: List[str]  # human-readable legs
    gross_pct: float
    net_pct: float


def _load_okx(http: Http):
    url = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
    rows = http.get_json(url)["data"]
    books = []
    for t in rows:
        if not t.get("bidPx") or not t.get("askPx"):
            continue
        base, quote = t["instId"].split("-")
        books.append(Book(base, quote, float(t["bidPx"]), float(t["askPx"]), float(t.get("volCcy24h") or 0)))
    return books, url


def _load_kucoin(http: Http):
    url = "https://api.kucoin.com/api/v1/market/allTickers"
    rows = http.get_json(url)["data"]["ticker"]
    books = []
    for t in rows:
        if not t.get("buy") or not t.get("sell"):
            continue
        base, quote = t["symbol"].split("-")
        books.append(Book(base, quote, float(t["buy"]), float(t["sell"]), float(t.get("volValue") or 0)))
    return books, url


def _load_gate(http: Http):
    url = "https://api.gateio.ws/api/v4/spot/tickers"
    rows = http.get_json(url)
    books = []
    for t in rows:
        if not t.get("highest_bid") or not t.get("lowest_ask"):
            continue
        base, quote = t["currency_pair"].split("_", 1)
        books.append(
            Book(base, quote, float(t["highest_bid"]), float(t["lowest_ask"]), float(t.get("quote_volume") or 0))
        )
    return books, url


TRIANGLE_VENUES = {"okx": _load_okx, "kucoin": _load_kucoin, "gate": _load_gate}


def _usd_volume(book: Book, usd_price: Dict[str, float]) -> float:
    price = usd_price.get(book.quote)
    return book.quote_volume * price if price else 0.0


def find_triangles(
    http: Http,
    venue: str,
    start: str,
    fee_pct: float,
    min_volume_usd: float,
    top: int,
) -> Tuple[List[Triangle], int, str]:
    """Return the best `top` triangles, how many were evaluated, and the source URL."""
    if venue not in TRIANGLE_VENUES:
        raise FetchError(f"triangular search supports {', '.join(TRIANGLE_VENUES)}")
    books, url = TRIANGLE_VENUES[venue](http)
    stable = {"USDT", "USDC", "USD"}
    usd_price: Dict[str, float] = {s: 1.0 for s in stable}
    for b in books:
        if b.quote == "USDT" and b.base not in usd_price and b.bid > 0:
            usd_price[b.base] = (b.bid + b.ask) / 2
    liquid = [b for b in books if b.bid > 0 and b.ask >= b.bid and _usd_volume(b, usd_price) >= min_volume_usd]

    # rate[(x, y)] = units of y received for one unit of x, at the best price, before fees
    rate: Dict[Tuple[str, str], float] = {}
    label: Dict[Tuple[str, str], str] = {}
    for b in liquid:
        rate[(b.base, b.quote)] = b.bid  # sell base for quote at the bid
        label[(b.base, b.quote)] = f"sell {b.base}/{b.quote} at {b.bid:.8g}"
        rate[(b.quote, b.base)] = 1.0 / b.ask  # buy base with quote at the ask
        label[(b.quote, b.base)] = f"buy {b.base}/{b.quote} at {b.ask:.8g}"

    neighbours: Dict[str, List[str]] = {}
    for x, y in rate:
        neighbours.setdefault(x, []).append(y)

    fee_factor = (1 - fee_pct / 100) ** 3
    found: List[Triangle] = []
    evaluated = 0
    for a in neighbours.get(start, []):
        for b in neighbours.get(a, []):
            if b == start or (b, start) not in rate:
                continue
            evaluated += 1
            gross = rate[(start, a)] * rate[(a, b)] * rate[(b, start)]
            found.append(
                Triangle(
                    path=(start, a, b, start),
                    legs=[label[(start, a)], label[(a, b)], label[(b, start)]],
                    gross_pct=(gross - 1) * 100,
                    net_pct=(gross * fee_factor - 1) * 100,
                )
            )
    found.sort(key=lambda t: t.net_pct, reverse=True)
    return found[:top], evaluated, url
