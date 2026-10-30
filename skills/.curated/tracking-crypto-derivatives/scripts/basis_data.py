#!/usr/bin/env python3
"""
Dated-futures basis (term structure) from public exchange endpoints.

Basis for each dated future = (futures price - the same venue's index) / index.
Annualized basis scales that to a 365-day year by days to expiry (simple, not
compounded). Venues: Deribit (BTC, ETH inverse futures) and OKX (coin-margined
USD futures).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Tuple

from http_client import FetchError, Http
from perps import VenueFailure

DERIBIT = "https://www.deribit.com/api/v2/public"
OKX = "https://www.okx.com"
OKX_DATED = re.compile(r"^[A-Z0-9]+-USD-(\d{6})$")


@dataclass
class BasisPoint:
    venue: str
    instrument: str
    expiry: datetime
    futures_price: float
    index_price: float
    days_to_expiry: float
    source: str

    @property
    def basis_pct(self) -> float:
        return (self.futures_price / self.index_price - 1.0) * 100.0

    @property
    def annualized_pct(self) -> float:
        return self.basis_pct * 365.0 / self.days_to_expiry


def fetch_deribit(http: Http, symbol: str) -> List[BasisPoint]:
    url = f"{DERIBIT}/get_book_summary_by_currency?currency={symbol}&kind=future"
    result = http.get_json(url).get("result") or []
    now = http.now()
    points = []
    for item in result:
        name = item["instrument_name"]
        if name.endswith("PERPETUAL"):
            continue
        expiry = datetime.strptime(name.split("-")[1], "%d%b%y").replace(hour=8, tzinfo=timezone.utc)
        days = (expiry - now).total_seconds() / 86400
        if days <= 0.5:  # basis this close to expiry annualizes into noise
            continue
        points.append(
            BasisPoint(
                venue="deribit",
                instrument=name,
                expiry=expiry,
                futures_price=float(item["mark_price"]),
                index_price=float(item["estimated_delivery_price"]),
                days_to_expiry=days,
                source=url,
            )
        )
    if not points:
        raise FetchError(f"no dated {symbol} futures listed")
    return points


def fetch_okx(http: Http, symbol: str) -> List[BasisPoint]:
    url = f"{OKX}/api/v5/market/tickers?instType=FUTURES&uly={symbol}-USD"
    tickers = http.get_json(url).get("data") or []
    index_data = http.get_json(f"{OKX}/api/v5/market/index-tickers?instId={symbol}-USD").get("data") or []
    if not index_data:
        raise FetchError(f"no {symbol}-USD index")
    index = float(index_data[0]["idxPx"])
    now = http.now()
    points = []
    for t in tickers:
        match = OKX_DATED.match(t["instId"])
        if not match or not t.get("bidPx") or not t.get("askPx"):
            continue
        expiry = datetime.strptime(match.group(1), "%y%m%d").replace(hour=8, tzinfo=timezone.utc)
        days = (expiry - now).total_seconds() / 86400
        if days <= 0.5:
            continue
        points.append(
            BasisPoint(
                venue="okx",
                instrument=t["instId"],
                expiry=expiry,
                futures_price=(float(t["bidPx"]) + float(t["askPx"])) / 2,
                index_price=index,
                days_to_expiry=days,
                source=url,
            )
        )
    if not points:
        raise FetchError(f"no dated {symbol} futures listed")
    return points


BASIS_VENUES = {"deribit": fetch_deribit, "okx": fetch_okx}


def fetch_all(http: Http, symbol: str) -> Tuple[List[BasisPoint], List[VenueFailure]]:
    points: List[BasisPoint] = []
    failures: List[VenueFailure] = []
    for name, fn in BASIS_VENUES.items():
        try:
            points.extend(fn(http, symbol))
        except FetchError as exc:
            failures.append(VenueFailure(name, exc.reason))
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            failures.append(VenueFailure(name, f"unexpected response shape ({type(exc).__name__})"))
    points.sort(key=lambda p: (p.expiry, p.venue))
    return points, failures


def describe_curve(points: List[BasisPoint]) -> str:
    """Plain description of the term structure; no recommendation."""
    if not points:
        return "No dated futures returned."
    positive = sum(1 for p in points if p.basis_pct > 0)
    if positive == len(points):
        shape = "Every dated future trades above its index (contango)."
    elif positive == 0:
        shape = "Every dated future trades below its index (backwardation)."
    else:
        shape = f"{positive} of {len(points)} dated futures trade above their index."
    return shape
