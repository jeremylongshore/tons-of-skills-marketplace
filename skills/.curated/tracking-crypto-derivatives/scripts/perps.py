#!/usr/bin/env python3
"""
Perpetual swaps: funding rates and open interest from public exchange endpoints.

Each venue adapter reads one public, keyless endpoint set and returns a
`PerpSnapshot` in common units:

- `funding_rate` is the venue's own rate for one funding interval, as a fraction.
- `interval_hours` is that interval (OKX, Binance, Bybit, KuCoin and Gate pay
  every 8 hours by default; Hyperliquid, Kraken and dYdX pay hourly; Deribit
  accrues continuously and publishes an 8-hour figure).
- `oi_base` is open interest counted on one side, in the coin.

Comparisons always use the 8-hour equivalent (`rate_8h`) so hourly and
8-hourly venues line up.
"""

from __future__ import annotations

import statistics
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional, Tuple

from http_client import FetchError, Http

OKX = "https://www.okx.com"
DERIBIT = "https://www.deribit.com/api/v2/public"
HYPERLIQUID = "https://api.hyperliquid.xyz/info"
KRAKEN = "https://futures.kraken.com/derivatives/api/v3"
KUCOIN = "https://api-futures.kucoin.com/api/v1"
GATE = "https://api.gateio.ws/api/v4"
DYDX = "https://indexer.dydx.trade/v4"
BINANCE = "https://fapi.binance.com"
BYBIT = "https://api.bybit.com/v5"


@dataclass
class PerpSnapshot:
    """One venue's perpetual swap for one coin, in common units."""

    venue: str
    instrument: str
    funding_rate: float
    interval_hours: float
    next_funding: Optional[datetime]
    mark_price: Optional[float]
    index_price: Optional[float]
    oi_base: Optional[float]
    source: str

    @property
    def rate_8h(self) -> float:
        """Funding rate scaled to an 8-hour period."""
        return self.funding_rate * 8.0 / self.interval_hours

    @property
    def annualized_pct(self) -> float:
        """Simple (non-compounded) annual rate, in percent."""
        return self.funding_rate * (24.0 * 365.0 / self.interval_hours) * 100.0

    @property
    def price(self) -> Optional[float]:
        return self.mark_price or self.index_price

    @property
    def oi_usd(self) -> Optional[float]:
        if self.oi_base is None or self.price is None:
            return None
        return self.oi_base * self.price


@dataclass
class VenueFailure:
    venue: str
    reason: str


@dataclass
class OIChange:
    """Open interest change over 24 hours, measured in coins so price moves do not count."""

    venue: str
    oi_base_now: float
    oi_base_24h_ago: float
    source: str

    @property
    def change_pct(self) -> float:
        return (self.oi_base_now / self.oi_base_24h_ago - 1.0) * 100.0


@dataclass
class AccountRatio:
    """Share of the venue's accounts holding a net long position."""

    venue: str
    long_accounts_pct: float
    source: str


def _f(value) -> Optional[float]:
    if value in (None, ""):
        return None
    return float(value)


def _ms(value) -> Optional[datetime]:
    if value in (None, "", 0, "0"):
        return None
    return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)


def _next_hour(now: datetime) -> datetime:
    return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)


def _kraken_symbol(symbol: str) -> str:
    return "XBT" if symbol == "BTC" else symbol


# ---------------------------------------------------------------------------
# Venue adapters
# ---------------------------------------------------------------------------


def fetch_okx(http: Http, symbol: str) -> PerpSnapshot:
    inst = f"{symbol}-USDT-SWAP"
    url = f"{OKX}/api/v5/public/funding-rate?instId={inst}"
    fr = http.get_json(url)
    if fr.get("code") != "0" or not fr.get("data"):
        raise FetchError(f"{inst} not listed")
    row = fr["data"][0]
    oi = http.get_json(f"{OKX}/api/v5/public/open-interest?instType=SWAP&instId={inst}")["data"][0]
    mark = http.get_json(f"{OKX}/api/v5/public/mark-price?instType=SWAP&instId={inst}")["data"][0]
    this_time, next_time = int(row["fundingTime"]), int(row["nextFundingTime"])
    return PerpSnapshot(
        venue="okx",
        instrument=inst,
        funding_rate=float(row["fundingRate"]),
        interval_hours=(next_time - this_time) / 3_600_000 or 8.0,
        next_funding=_ms(this_time),
        mark_price=_f(mark["markPx"]),
        index_price=None,
        oi_base=_f(oi["oiCcy"]),
        source=url,
    )


def fetch_deribit(http: Http, symbol: str) -> PerpSnapshot:
    inverse = symbol in ("BTC", "ETH")
    inst = f"{symbol}-PERPETUAL" if inverse else f"{symbol}_USDC-PERPETUAL"
    url = f"{DERIBIT}/ticker?instrument_name={inst}"
    res = http.get_json(url).get("result")
    if not res:
        raise FetchError(f"{inst} not listed")
    mark = float(res["mark_price"])
    oi = float(res["open_interest"])
    return PerpSnapshot(
        venue="deribit",
        instrument=inst,
        funding_rate=float(res["funding_8h"]),
        interval_hours=8.0,
        next_funding=None,  # Deribit accrues funding continuously
        mark_price=mark,
        index_price=_f(res.get("index_price")),
        # Inverse perpetuals report open interest in USD; USDC perpetuals in coins.
        oi_base=oi / mark if inverse else oi,
        source=url,
    )


def fetch_hyperliquid(http: Http, symbol: str) -> PerpSnapshot:
    meta, ctxs = http.post_json(HYPERLIQUID, {"type": "metaAndAssetCtxs"})
    names = [u["name"] for u in meta["universe"]]
    if symbol not in names:
        raise FetchError(f"{symbol} not listed")
    ctx = ctxs[names.index(symbol)]
    return PerpSnapshot(
        venue="hyperliquid",
        instrument=symbol,
        funding_rate=float(ctx["funding"]),
        interval_hours=1.0,
        next_funding=_next_hour(http.now()),
        mark_price=_f(ctx["markPx"]),
        index_price=_f(ctx.get("oraclePx")),
        oi_base=_f(ctx["openInterest"]),
        source=f"{HYPERLIQUID} metaAndAssetCtxs",
    )


def fetch_kraken(http: Http, symbol: str) -> PerpSnapshot:
    inst = f"PF_{_kraken_symbol(symbol)}USD"
    url = f"{KRAKEN}/tickers/{inst}"
    body = http.get_json(url)
    tick = body.get("ticker")
    if body.get("result") != "success" or not tick or tick.get("relativeFundingRate") is None:
        raise FetchError(f"{inst} not listed")
    return PerpSnapshot(
        venue="kraken",
        instrument=inst,
        # relativeFundingRate is the hourly rate as a fraction of price.
        funding_rate=float(tick["relativeFundingRate"]),
        interval_hours=1.0,
        next_funding=_next_hour(http.now()),
        mark_price=_f(tick.get("markPrice")),
        index_price=_f(tick.get("indexPrice")),
        oi_base=_f(tick.get("openInterest")),  # contract size is one coin
        source=url,
    )


def fetch_kucoin(http: Http, symbol: str) -> PerpSnapshot:
    inst = f"{_kraken_symbol(symbol)}USDTM"
    url = f"{KUCOIN}/contracts/{inst}"
    data = http.get_json(url).get("data")
    if not data or data.get("status") != "Open":
        raise FetchError(f"{inst} not listed")
    return PerpSnapshot(
        venue="kucoin",
        instrument=inst,
        funding_rate=float(data["fundingFeeRate"]),
        interval_hours=float(data["currentFundingRateGranularity"]) / 3_600_000,
        next_funding=_ms(data.get("nextFundingRateDateTime")),
        mark_price=_f(data.get("markPrice")),
        index_price=_f(data.get("indexPrice")),
        oi_base=float(data["openInterest"]) * float(data["multiplier"]),
        source=url,
    )


def fetch_gate(http: Http, symbol: str) -> PerpSnapshot:
    inst = f"{symbol}_USDT"
    url = f"{GATE}/futures/usdt/contracts/{inst}"
    data = http.get_json(url)
    if not isinstance(data, dict) or "funding_rate" not in data:
        raise FetchError(f"{inst} not listed")
    next_apply = data.get("funding_next_apply")
    return PerpSnapshot(
        venue="gate",
        instrument=inst,
        funding_rate=float(data["funding_rate"]),
        interval_hours=float(data["funding_interval"]) / 3600,
        next_funding=datetime.fromtimestamp(int(next_apply), tz=timezone.utc) if next_apply else None,
        mark_price=_f(data.get("mark_price")),
        index_price=_f(data.get("index_price")),
        # position_size is the total long position in contracts (one side).
        oi_base=float(data["position_size"]) * float(data["quanto_multiplier"]),
        source=url,
    )


def fetch_dydx(http: Http, symbol: str) -> PerpSnapshot:
    inst = f"{symbol}-USD"
    url = f"{DYDX}/perpetualMarkets?ticker={inst}"
    market = http.get_json(url).get("markets", {}).get(inst)
    if not market or market.get("status") != "ACTIVE":
        raise FetchError(f"{inst} not listed")
    return PerpSnapshot(
        venue="dydx",
        instrument=inst,
        funding_rate=float(market["nextFundingRate"]),
        interval_hours=1.0,
        next_funding=_next_hour(http.now()),
        mark_price=None,
        index_price=_f(market.get("oraclePrice")),
        oi_base=_f(market.get("openInterest")),
        source=url,
    )


def fetch_binance(http: Http, symbol: str) -> PerpSnapshot:
    inst = f"{symbol}USDT"
    url = f"{BINANCE}/fapi/v1/premiumIndex?symbol={inst}"
    prem = http.get_json(url)
    if "lastFundingRate" not in prem:
        raise FetchError(f"{inst} not listed")
    oi = http.get_json(f"{BINANCE}/fapi/v1/openInterest?symbol={inst}")
    # fundingInfo lists only symbols whose interval differs from the 8-hour default.
    info = http.get_json(f"{BINANCE}/fapi/v1/fundingInfo")
    interval = next((float(i["fundingIntervalHours"]) for i in info if i.get("symbol") == inst), 8.0)
    return PerpSnapshot(
        venue="binance",
        instrument=inst,
        funding_rate=float(prem["lastFundingRate"]),
        interval_hours=interval,
        next_funding=_ms(prem.get("nextFundingTime")),
        mark_price=_f(prem.get("markPrice")),
        index_price=_f(prem.get("indexPrice")),
        oi_base=_f(oi.get("openInterest")),
        source=url,
    )


def fetch_bybit(http: Http, symbol: str) -> PerpSnapshot:
    inst = f"{symbol}USDT"
    url = f"{BYBIT}/market/tickers?category=linear&symbol={inst}"
    body = http.get_json(url)
    rows = body.get("result", {}).get("list") or []
    if body.get("retCode") != 0 or not rows:
        raise FetchError(f"{inst} not listed")
    row = rows[0]
    return PerpSnapshot(
        venue="bybit",
        instrument=inst,
        funding_rate=float(row["fundingRate"]),
        interval_hours=float(row.get("fundingIntervalHour") or 8),
        next_funding=_ms(row.get("nextFundingTime")),
        mark_price=_f(row.get("markPrice")),
        index_price=_f(row.get("indexPrice")),
        # openInterest counts both sides; singleOpenInterest is one side.
        oi_base=_f(row.get("singleOpenInterest")),
        source=url,
    )


VENUES: Dict[str, Callable[[Http, str], PerpSnapshot]] = {
    "okx": fetch_okx,
    "deribit": fetch_deribit,
    "hyperliquid": fetch_hyperliquid,
    "kraken": fetch_kraken,
    "kucoin": fetch_kucoin,
    "gate": fetch_gate,
    "dydx": fetch_dydx,
    "binance": fetch_binance,
    "bybit": fetch_bybit,
}


def fetch_all(
    http: Http, symbol: str, venues: Optional[List[str]] = None
) -> Tuple[List[PerpSnapshot], List[VenueFailure]]:
    """Fetch every venue in parallel; a failing venue is reported, never invented."""
    names = venues or list(VENUES)
    results: List[PerpSnapshot] = []
    failures: List[VenueFailure] = []

    def one(name: str):
        try:
            return VENUES[name](http, symbol), None
        except FetchError as exc:
            return None, VenueFailure(name, exc.reason)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            return None, VenueFailure(name, f"unexpected response shape ({type(exc).__name__}: {exc})")

    with ThreadPoolExecutor(max_workers=len(names)) as pool:
        for snap, failure in pool.map(one, names):
            if snap is not None:
                results.append(snap)
            if failure is not None:
                failures.append(failure)
    return results, failures


# ---------------------------------------------------------------------------
# History and positioning (venues that publish it for the same instrument)
# ---------------------------------------------------------------------------


def _oi_change_okx(http: Http, symbol: str) -> OIChange:
    inst = f"{symbol}-USDT-SWAP"
    url = f"{OKX}/api/v5/rubik/stat/contracts/open-interest-history?instId={inst}&period=1H&limit=25"
    rows = http.get_json(url)["data"]  # newest first: [ts, oi, oiCcy, oiUsd]
    if len(rows) < 25:
        raise FetchError("less than 24 hours of history")
    return OIChange("okx", float(rows[0][2]), float(rows[24][2]), url)


def _oi_change_bybit(http: Http, symbol: str) -> OIChange:
    url = f"{BYBIT}/market/open-interest?category=linear&symbol={symbol}USDT&intervalTime=1h&limit=25"
    rows = http.get_json(url)["result"]["list"]  # newest first
    if len(rows) < 25:
        raise FetchError("less than 24 hours of history")
    return OIChange("bybit", float(rows[0]["singleOpenInterest"]), float(rows[24]["singleOpenInterest"]), url)


def _oi_change_binance(http: Http, symbol: str) -> OIChange:
    url = f"{BINANCE}/futures/data/openInterestHist?symbol={symbol}USDT&period=1h&limit=25"
    rows = http.get_json(url)  # oldest first
    if len(rows) < 25:
        raise FetchError("less than 24 hours of history")
    return OIChange("binance", float(rows[-1]["sumOpenInterest"]), float(rows[0]["sumOpenInterest"]), url)


def _ratio_okx(http: Http, symbol: str) -> AccountRatio:
    url = f"{OKX}/api/v5/rubik/stat/contracts/long-short-account-ratio-contract?instId={symbol}-USDT-SWAP&period=1H&limit=1"
    ratio = float(http.get_json(url)["data"][0][1])  # longs / shorts
    return AccountRatio("okx", ratio / (1 + ratio) * 100, url)


def _ratio_bybit(http: Http, symbol: str) -> AccountRatio:
    url = f"{BYBIT}/market/account-ratio?category=linear&symbol={symbol}USDT&period=1h&limit=1"
    row = http.get_json(url)["result"]["list"][0]
    return AccountRatio("bybit", float(row["buyRatio"]) * 100, url)


def _ratio_binance(http: Http, symbol: str) -> AccountRatio:
    url = f"{BINANCE}/futures/data/globalLongShortAccountRatio?symbol={symbol}USDT&period=1h&limit=1"
    row = http.get_json(url)[0]
    return AccountRatio("binance", float(row["longAccount"]) * 100, url)


OI_HISTORY = {"okx": _oi_change_okx, "bybit": _oi_change_bybit, "binance": _oi_change_binance}
ACCOUNT_RATIOS = {"okx": _ratio_okx, "bybit": _ratio_bybit, "binance": _ratio_binance}


def fetch_positioning(
    http: Http, symbol: str, venues: List[str]
) -> Tuple[List[OIChange], List[AccountRatio], List[VenueFailure]]:
    """24-hour open interest change and account long share, where the venue publishes them."""
    changes: List[OIChange] = []
    ratios: List[AccountRatio] = []
    failures: List[VenueFailure] = []
    jobs = [("oi", v, OI_HISTORY[v]) for v in venues if v in OI_HISTORY]
    jobs += [("ratio", v, ACCOUNT_RATIOS[v]) for v in venues if v in ACCOUNT_RATIOS]

    def one(job):
        kind, venue, fn = job
        try:
            return kind, fn(http, symbol), None
        except FetchError as exc:
            return (
                kind,
                None,
                VenueFailure(f"{venue} ({'24h history' if kind == 'oi' else 'account ratio'})", exc.reason),
            )
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            return kind, None, VenueFailure(venue, f"unexpected response shape ({type(exc).__name__})")

    if not jobs:
        return changes, ratios, failures
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        for kind, value, failure in pool.map(one, jobs):
            if failure is not None:
                failures.append(failure)
            elif kind == "oi":
                changes.append(value)
            else:
                ratios.append(value)
    return changes, ratios, failures


# ---------------------------------------------------------------------------
# Summaries (descriptive only)
# ---------------------------------------------------------------------------


@dataclass
class FundingSummary:
    venues: int
    positive: int
    negative: int
    mean_8h: float
    median_8h: float
    oi_weighted_8h: Optional[float]
    highest: PerpSnapshot
    lowest: PerpSnapshot
    notes: List[str] = field(default_factory=list)

    @property
    def spread_8h(self) -> float:
        return self.highest.rate_8h - self.lowest.rate_8h


def summarize_funding(snaps: List[PerpSnapshot]) -> FundingSummary:
    if not snaps:
        raise ValueError("no venue returned data")
    rates = [s.rate_8h for s in snaps]
    weighted = [(s.rate_8h, s.oi_usd) for s in snaps if s.oi_usd]
    total_oi = sum(w for _, w in weighted)
    summary = FundingSummary(
        venues=len(snaps),
        positive=sum(1 for r in rates if r > 0),
        negative=sum(1 for r in rates if r < 0),
        mean_8h=statistics.fmean(rates),
        median_8h=statistics.median(rates),
        oi_weighted_8h=(sum(r * w for r, w in weighted) / total_oi) if total_oi else None,
        highest=max(snaps, key=lambda s: s.rate_8h),
        lowest=min(snaps, key=lambda s: s.rate_8h),
    )
    if summary.positive == summary.venues:
        summary.notes.append("Funding is positive on every venue: longs pay shorts.")
    elif summary.negative == summary.venues:
        summary.notes.append("Funding is negative on every venue: shorts pay longs.")
    else:
        zero = summary.venues - summary.positive - summary.negative
        parts = [f"positive on {summary.positive}", f"negative on {summary.negative}"]
        if zero:
            parts.append(f"zero on {zero}")
        summary.notes.append(f"Of {summary.venues} venues, funding is " + ", ".join(parts) + ".")
    return summary
