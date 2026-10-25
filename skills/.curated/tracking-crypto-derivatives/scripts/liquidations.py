#!/usr/bin/env python3
"""
Recent liquidations from OKX's public liquidation-orders endpoint.

OKX is the venue in this tracker that publishes filled liquidation orders over
a keyless REST endpoint. The result covers the most recent orders OKX returns
for the instrument family, so the time window varies; the report states it.
Liquidation "heatmaps" sold by data vendors are model estimates of where
positions would be closed; public data cannot reproduce them, so this tracker
does not draw one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List

from http_client import FetchError, Http

OKX = "https://www.okx.com"


@dataclass
class LiquidationOrder:
    time: datetime
    side: str  # position that was liquidated: "long" or "short"
    price: float
    size_base: float

    @property
    def value_usd(self) -> float:
        return self.price * self.size_base


@dataclass
class LiquidationReport:
    instrument: str
    orders: List[LiquidationOrder]
    source: str
    notes: List[str] = field(default_factory=list)

    @property
    def window_start(self) -> datetime:
        return min(o.time for o in self.orders)

    @property
    def window_end(self) -> datetime:
        return max(o.time for o in self.orders)

    def total(self, side: str) -> float:
        return sum(o.value_usd for o in self.orders if o.side == side)

    def count(self, side: str) -> int:
        return sum(1 for o in self.orders if o.side == side)

    def largest(self, n: int = 5) -> List[LiquidationOrder]:
        return sorted(self.orders, key=lambda o: o.value_usd, reverse=True)[:n]


def _liquidated_side(detail: dict) -> str:
    pos = detail.get("posSide")
    if pos in ("long", "short"):
        return pos
    # One-way mode: a forced sell closes a long, a forced buy closes a short.
    return "long" if detail.get("side") == "sell" else "short"


def fetch(http: Http, symbol: str, hours: int = 24, max_pages: int = 30) -> LiquidationReport:
    inst = f"{symbol}-USDT-SWAP"
    inst_url = f"{OKX}/api/v5/public/instruments?instType=SWAP&instId={inst}"
    inst_data = http.get_json(inst_url).get("data") or []
    if not inst_data:
        raise FetchError(f"{inst} not listed")
    contract_value = float(inst_data[0]["ctVal"])  # coins per contract
    url = f"{OKX}/api/v5/public/liquidation-orders?instType=SWAP&uly={symbol}-USDT&state=filled&limit=100"
    cutoff = http.now() - timedelta(hours=hours)
    orders: List[LiquidationOrder] = []
    seen = set()
    page_url = url
    for _ in range(max_pages):
        data = http.get_json(page_url).get("data") or []
        page = []
        for group in data:
            if group.get("instId") not in (None, inst):
                continue
            for d in group.get("details", []):
                page.append(
                    LiquidationOrder(
                        time=datetime.fromtimestamp(int(d["ts"]) / 1000, tz=timezone.utc),
                        side=_liquidated_side(d),
                        price=float(d["bkPx"]),
                        size_base=float(d["sz"]) * contract_value,
                    )
                )
        if not page:
            break
        for o in page:
            key = (o.time, o.side, o.price, o.size_base)
            if o.time >= cutoff and key not in seen:
                seen.add(key)
                orders.append(o)
        oldest = min(o.time for o in page)
        if oldest < cutoff:
            break
        page_url = f"{url}&after={int(oldest.timestamp() * 1000)}"
    if not orders:
        raise FetchError(f"OKX returned no filled liquidations in the last {hours} hours")
    report = LiquidationReport(instrument=inst, orders=orders, source=url)
    if report.window_start > cutoff + timedelta(minutes=30):
        report.notes.append(
            f"OKX history reached back to {report.window_start:%Y-%m-%d %H:%M} UTC, "
            f"short of the requested {hours} hours."
        )
    return report
