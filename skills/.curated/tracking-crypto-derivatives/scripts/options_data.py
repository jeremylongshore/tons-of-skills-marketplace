#!/usr/bin/env python3
"""
Options market data from Deribit's public API.

Everything here is computed from Deribit's published instrument summaries,
volatility index (DVOL) and recent trades; nothing is estimated or simulated.

- Put/call ratios by open interest and by 24-hour volume, per expiry.
- Max pain: the settlement price at which option holders' total intrinsic
  value would be smallest, computed from open interest by strike.
- At-the-money implied volatility: Deribit's mark IV at the strike nearest the
  expiry's underlying price.
- DVOL rank and percentile over the trailing 365 days.
- Large recent trades above a notional threshold.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from http_client import FetchError, Http

DERIBIT = "https://www.deribit.com/api/v2/public"
OPTION_CURRENCIES = ("BTC", "ETH")


@dataclass
class OptionRow:
    expiry: datetime
    expiry_code: str
    strike: float
    kind: str  # "C" or "P"
    open_interest: float  # coins
    volume: float  # coins, 24h
    mark_iv: Optional[float]
    underlying_price: float


@dataclass
class ExpirySummary:
    expiry: datetime
    expiry_code: str
    underlying_price: float
    call_oi: float
    put_oi: float
    call_volume: float
    put_volume: float
    atm_strike: float
    atm_iv: Optional[float]
    max_pain: float

    @property
    def pcr_oi(self) -> Optional[float]:
        return self.put_oi / self.call_oi if self.call_oi else None

    @property
    def pcr_volume(self) -> Optional[float]:
        return self.put_volume / self.call_volume if self.call_volume else None

    @property
    def max_pain_distance_pct(self) -> float:
        return (self.max_pain / self.underlying_price - 1.0) * 100.0


@dataclass
class DvolStats:
    current: float
    low_365d: float
    high_365d: float
    percentile_365d: float  # share of days with a lower close, in percent

    @property
    def rank_365d(self) -> float:
        span = self.high_365d - self.low_365d
        return (self.current - self.low_365d) / span * 100.0 if span else 50.0


@dataclass
class LargeTrade:
    time: datetime
    instrument: str
    direction: str  # taker side: "buy" or "sell"
    amount: float  # contracts, in coins
    notional_usd: float
    premium_usd: float
    iv: Optional[float]
    block: bool


@dataclass
class OptionsReport:
    currency: str
    expiries: List[ExpirySummary]
    total_call_oi: float
    total_put_oi: float
    dvol: Optional[DvolStats]
    trades: List[LargeTrade] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)

    @property
    def pcr_oi(self) -> Optional[float]:
        return self.total_put_oi / self.total_call_oi if self.total_call_oi else None


def parse_instrument(name: str):
    """BTC-27NOV26-80000-C -> (expiry datetime 08:00 UTC, code, strike, kind)."""
    _, code, strike, kind = name.split("-")
    expiry = datetime.strptime(code, "%d%b%y").replace(hour=8, tzinfo=timezone.utc)
    return expiry, code, float(strike.replace("d", ".")), kind


def max_pain(rows: List[OptionRow]) -> float:
    """Strike at which the total intrinsic value owed to option holders is smallest."""
    calls: Dict[float, float] = defaultdict(float)
    puts: Dict[float, float] = defaultdict(float)
    for r in rows:
        (calls if r.kind == "C" else puts)[r.strike] += r.open_interest
    strikes = sorted(set(calls) | set(puts))

    def payout(settle: float) -> float:
        owed_calls = sum(oi * (settle - k) for k, oi in calls.items() if settle > k)
        owed_puts = sum(oi * (k - settle) for k, oi in puts.items() if settle < k)
        return owed_calls + owed_puts

    return min(strikes, key=payout)


def summarize_expiry(rows: List[OptionRow]) -> ExpirySummary:
    underlying = rows[0].underlying_price
    atm_strike = min({r.strike for r in rows}, key=lambda k: abs(k - underlying))
    atm_ivs = [r.mark_iv for r in rows if r.strike == atm_strike and r.mark_iv]
    return ExpirySummary(
        expiry=rows[0].expiry,
        expiry_code=rows[0].expiry_code,
        underlying_price=underlying,
        call_oi=sum(r.open_interest for r in rows if r.kind == "C"),
        put_oi=sum(r.open_interest for r in rows if r.kind == "P"),
        call_volume=sum(r.volume for r in rows if r.kind == "C"),
        put_volume=sum(r.volume for r in rows if r.kind == "P"),
        atm_strike=atm_strike,
        atm_iv=sum(atm_ivs) / len(atm_ivs) if atm_ivs else None,
        max_pain=max_pain(rows),
    )


def fetch_rows(http: Http, currency: str) -> List[OptionRow]:
    url = f"{DERIBIT}/get_book_summary_by_currency?currency={currency}&kind=option"
    result = http.get_json(url).get("result") or []
    rows = []
    for item in result:
        try:
            expiry, code, strike, kind = parse_instrument(item["instrument_name"])
        except (ValueError, KeyError):
            continue
        rows.append(
            OptionRow(
                expiry=expiry,
                expiry_code=code,
                strike=strike,
                kind=kind,
                open_interest=float(item.get("open_interest") or 0),
                volume=float(item.get("volume") or 0),
                mark_iv=item.get("mark_iv"),
                underlying_price=float(item["underlying_price"]),
            )
        )
    return rows


def fetch_dvol(http: Http, currency: str) -> DvolStats:
    end = http.now()
    start = end - timedelta(days=365)
    url = (
        f"{DERIBIT}/get_volatility_index_data?currency={currency}&resolution=1D"
        f"&start_timestamp={int(start.timestamp()) // 86400 * 86400 * 1000}"
        f"&end_timestamp={int(end.timestamp()) // 3600 * 3600 * 1000}"
    )
    data = http.get_json(url)["result"]["data"]  # [ts, open, high, low, close]
    if len(data) < 30:
        raise FetchError("not enough DVOL history")
    closes = [row[4] for row in data]
    current = closes[-1]
    return DvolStats(
        current=current,
        low_365d=min(closes),
        high_365d=max(closes),
        percentile_365d=sum(1 for c in closes[:-1] if c < current) / (len(closes) - 1) * 100.0,
    )


def fetch_large_trades(http: Http, currency: str, min_notional_usd: float, limit: int = 10) -> List[LargeTrade]:
    url = f"{DERIBIT}/get_last_trades_by_currency?currency={currency}&kind=option&count=1000"
    trades = http.get_json(url)["result"]["trades"]
    out = []
    for t in trades:
        index = float(t["index_price"])
        notional = float(t["amount"]) * index
        if notional < min_notional_usd:
            continue
        out.append(
            LargeTrade(
                time=datetime.fromtimestamp(t["timestamp"] / 1000, tz=timezone.utc),
                instrument=t["instrument_name"],
                direction=t["direction"],
                amount=float(t["amount"]),
                notional_usd=notional,
                premium_usd=float(t["price"]) * float(t["amount"]) * index,
                iv=t.get("iv"),
                block="block_trade_id" in t,
            )
        )
    out.sort(key=lambda x: x.notional_usd, reverse=True)
    return out[:limit]


def build_report(
    http: Http,
    currency: str,
    expiry_code: Optional[str] = None,
    max_expiries: int = 6,
    trades_min_usd: Optional[float] = None,
) -> OptionsReport:
    currency = currency.upper()
    if currency not in OPTION_CURRENCIES:
        raise FetchError(f"Deribit lists options for {', '.join(OPTION_CURRENCIES)} only")
    rows = fetch_rows(http, currency)
    if not rows:
        raise FetchError("Deribit returned no option instruments")
    now = http.now()
    by_expiry: Dict[str, List[OptionRow]] = defaultdict(list)
    for r in rows:
        if r.expiry > now:
            by_expiry[r.expiry_code].append(r)
    if expiry_code:
        wanted = expiry_code.upper()
        if wanted not in by_expiry:
            listed = ", ".join(sorted(by_expiry, key=lambda c: by_expiry[c][0].expiry))
            raise FetchError(f"expiry {wanted} not listed; listed expiries: {listed}")
        codes = [wanted]
    else:
        codes = sorted(by_expiry, key=lambda c: by_expiry[c][0].expiry)[:max_expiries]

    report = OptionsReport(
        currency=currency,
        expiries=[summarize_expiry(by_expiry[c]) for c in codes],
        total_call_oi=sum(r.open_interest for r in rows if r.kind == "C" and r.expiry > now),
        total_put_oi=sum(r.open_interest for r in rows if r.kind == "P" and r.expiry > now),
        dvol=None,
        sources=[f"{DERIBIT}/get_book_summary_by_currency?currency={currency}&kind=option"],
    )
    try:
        report.dvol = fetch_dvol(http, currency)
        report.sources.append(f"{DERIBIT}/get_volatility_index_data ({currency} DVOL, daily)")
    except FetchError as exc:
        report.failures.append(f"deribit DVOL: {exc.reason}")
    if trades_min_usd is not None:
        try:
            report.trades = fetch_large_trades(http, currency, trades_min_usd)
            report.sources.append(f"{DERIBIT}/get_last_trades_by_currency ({currency} options, last 1000)")
        except FetchError as exc:
            report.failures.append(f"deribit trades: {exc.reason}")
    return report
