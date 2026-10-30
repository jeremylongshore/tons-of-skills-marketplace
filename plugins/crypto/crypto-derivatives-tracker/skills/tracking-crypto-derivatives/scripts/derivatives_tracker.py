#!/usr/bin/env python3
"""
Crypto Derivatives Tracker: read-only research from public exchange data.

Commands:
    funding SYMBOL [SYMBOL ...]   Funding rates per venue, 8h-equivalent and annualized
    oi SYMBOL                     Open interest per venue, 24h change, account long share
    options SYMBOL                Deribit put/call ratios, max pain, ATM IV, DVOL rank
    basis SYMBOL                  Dated-futures basis (term structure), Deribit and OKX
    liquidations SYMBOL           OKX filled liquidations over the last N hours
    dashboard SYMBOL [SYMBOL ...] Funding, open interest and basis in one view
    venues                        What each venue provides

Every figure comes from a public, keyless endpoint and is labelled with its
source. A venue that fails is named with the reason; no value is invented.
`--demo` replays a bundled recording of real responses and marks every line.

Usage:
    python derivatives_tracker.py funding BTC ETH
    python derivatives_tracker.py oi BTC --format json
    python derivatives_tracker.py options BTC --expiry 27NOV26 --large-trades 1000000
    python derivatives_tracker.py basis ETH
    python derivatives_tracker.py liquidations BTC --hours 12
    python derivatives_tracker.py dashboard BTC ETH SOL
    python derivatives_tracker.py funding BTC --demo
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

import basis_data
import liquidations
import options_data
import perps
from http_client import FetchError, Http, Recording

VERSION = "2.0.0"
SKILL = "tracking-crypto-derivatives"
DISCLAIMER = "Research output only. Not financial advice. This tool places no trades."
DEMO_RECORDING = Path(__file__).resolve().parent.parent / "assets" / "demo-recording.json"


class Output:
    """Console writer that marks every line in demo mode."""

    def __init__(self, demo: bool, recorded_at: Optional[datetime] = None):
        self.demo = demo
        self.recorded_at = recorded_at

    def line(self, text: str = "") -> None:
        prefix = "[DEMO] " if self.demo else ""
        for part in text.split("\n"):
            print(f"{prefix}{part}".rstrip())

    def header(self, title: str, http: Http) -> None:
        self.line("=" * 72)
        self.line(f" {title}")
        when = http.now().strftime("%Y-%m-%d %H:%M UTC")
        if self.demo:
            self.line(f" Recorded data from {when}, not live. Run without --demo for live data.")
        else:
            self.line(f" Live public data fetched {when}")
        self.line("=" * 72)

    def failures(self, failures) -> None:
        if not failures:
            return
        self.line("")
        self.line("Unavailable:")
        for f in failures:
            self.line(f"  {f.venue}: {f.reason}")

    def footer(self, sources: List[str]) -> None:
        self.line("")
        self.line("Sources:")
        for s in dict.fromkeys(sources):
            self.line(f"  {s}")
        self.line("")
        self.line(DISCLAIMER)


def envelope(http: Http, command: str, symbols: List[str], data, sources, failures) -> str:
    doc = {
        "skill": SKILL,
        "version": VERSION,
        "command": command,
        "symbols": symbols,
        "generated_at": http.now().isoformat().replace("+00:00", "Z"),
        "mode": "demo" if http.is_replay else "live",
        "sources": list(dict.fromkeys(sources)),
        "failures": [{"venue": f.venue, "reason": f.reason} for f in failures],
        "data": data,
        "disclaimer": DISCLAIMER,
    }
    if http.is_replay:
        doc["demo_note"] = "Replayed recording of real responses; not live data."
    return json.dumps(doc, indent=2, default=str)


def pct(value: Optional[float], digits: int = 4, sign: bool = True) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.{digits}f}%" if sign else f"{value:.{digits}f}%"


def ratio(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def usd(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    for unit, size in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(value) >= size:
            return f"${value / size:,.2f}{unit}"
    return f"${value:,.2f}"


def until(target: Optional[datetime], now: datetime) -> str:
    if target is None:
        return "continuous"
    minutes = int((target - now).total_seconds() // 60)
    if minutes < 0:
        return "due"
    return f"{minutes // 60}h {minutes % 60:02d}m"


def snapshot_dict(s: perps.PerpSnapshot) -> dict:
    return {
        "venue": s.venue,
        "instrument": s.instrument,
        "funding_rate": s.funding_rate,
        "interval_hours": s.interval_hours,
        "rate_8h": s.rate_8h,
        "annualized_pct": s.annualized_pct,
        "next_funding": s.next_funding,
        "mark_price": s.mark_price,
        "index_price": s.index_price,
        "open_interest_base": s.oi_base,
        "open_interest_usd": s.oi_usd,
        "source": s.source,
    }


def venues_arg(args) -> Optional[List[str]]:
    if not getattr(args, "venues", None):
        return None
    names = [v.strip().lower() for v in args.venues.split(",") if v.strip()]
    unknown = [v for v in names if v not in perps.VENUES]
    if unknown:
        raise SystemExit(f"Unknown venue(s): {', '.join(unknown)}. Known: {', '.join(perps.VENUES)}")
    return names


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_funding(args, http: Http, out: Output) -> int:
    payload, sources, all_failures = [], [], []
    for symbol in args.symbols:
        snaps, failures = perps.fetch_all(http, symbol, venues_arg(args))
        all_failures += [perps.VenueFailure(f"{symbol} {f.venue}", f.reason) for f in failures]
        sources += [s.source for s in snaps]
        if not snaps:
            payload.append({"symbol": symbol, "venues": [], "summary": None})
            continue
        summary = perps.summarize_funding(snaps)
        payload.append(
            {
                "symbol": symbol,
                "venues": [snapshot_dict(s) for s in snaps],
                "summary": {
                    "venues": summary.venues,
                    "mean_rate_8h": summary.mean_8h,
                    "median_rate_8h": summary.median_8h,
                    "oi_weighted_rate_8h": summary.oi_weighted_8h,
                    "highest": summary.highest.venue,
                    "lowest": summary.lowest.venue,
                    "spread_8h": summary.spread_8h,
                    "notes": summary.notes,
                },
            }
        )
        if args.format == "console":
            out.line("")
            out.line(f"{symbol} perpetual funding")
            out.line(
                f"{'Venue':<12} {'Instrument':<20} {'Rate':>10} {'Every':>6} {'8h equiv':>10} {'Annual':>9} {'Next':>11}"
            )
            out.line("-" * 84)
            for s in sorted(snaps, key=lambda s: s.rate_8h, reverse=True):
                out.line(
                    f"{s.venue:<12} {s.instrument:<20} {pct(s.funding_rate * 100):>10} "
                    f"{s.interval_hours:>5.0f}h {pct(s.rate_8h * 100):>10} {pct(s.annualized_pct, 2):>9} "
                    f"{until(s.next_funding, http.now()):>11}"
                )
            out.line("-" * 84)
            out.line(f"Mean 8h equivalent: {pct(summary.mean_8h * 100)}   Median: {pct(summary.median_8h * 100)}")
            if summary.oi_weighted_8h is not None:
                out.line(f"Weighted by open interest: {pct(summary.oi_weighted_8h * 100)}")
            out.line(
                f"Highest: {summary.highest.venue} {pct(summary.highest.rate_8h * 100)}   "
                f"Lowest: {summary.lowest.venue} {pct(summary.lowest.rate_8h * 100)}   "
                f"Spread: {pct(summary.spread_8h * 100, sign=False)}"
            )
            for note in summary.notes:
                out.line(note)

    if args.format == "json":
        print(envelope(http, "funding", args.symbols, payload, sources, all_failures))
    else:
        out.failures(all_failures)
        out.line("")
        out.line("Positive funding: longs pay shorts. Annual figures are simple (rate x periods per year).")
        out.footer(sources)
    return 0 if any(p["venues"] for p in payload) else 2


def cmd_oi(args, http: Http, out: Output) -> int:
    symbol = args.symbol
    snaps, failures = perps.fetch_all(http, symbol, venues_arg(args))
    names = [s.venue for s in snaps] + [f.venue for f in failures]
    changes, ratios, pos_failures = perps.fetch_positioning(http, symbol, names)
    with_oi = [s for s in snaps if s.oi_usd]
    total = sum(s.oi_usd for s in with_oi)
    sources = [s.source for s in snaps] + [c.source for c in changes] + [r.source for r in ratios]
    failures = failures + pos_failures
    change_by = {c.venue: c for c in changes}
    ratio_by = {r.venue: r for r in ratios}

    if args.format == "json":
        data = {
            "total_open_interest_usd": total,
            "venues": [
                {
                    **snapshot_dict(s),
                    "share_pct": s.oi_usd / total * 100 if total else None,
                    "change_24h_pct": change_by[s.venue].change_pct if s.venue in change_by else None,
                    "long_accounts_pct": ratio_by[s.venue].long_accounts_pct if s.venue in ratio_by else None,
                }
                for s in with_oi
            ],
        }
        print(envelope(http, "oi", [symbol], data, sources, failures))
        return 0 if with_oi else 2

    out.line("")
    out.line(f"{symbol} perpetual open interest (one side)")
    out.line(f"{'Venue':<12} {'Coins':>14} {'USD':>12} {'Share':>7} {'24h chg':>9} {'Accts long':>11}")
    out.line("-" * 70)
    for s in sorted(with_oi, key=lambda s: s.oi_usd, reverse=True):
        change = change_by.get(s.venue)
        ratio = ratio_by.get(s.venue)
        out.line(
            f"{s.venue:<12} {s.oi_base:>14,.2f} {usd(s.oi_usd):>12} {s.oi_usd / total * 100:>6.1f}% "
            f"{pct(change.change_pct, 2) if change else 'n/a':>9} "
            f"{pct(ratio.long_accounts_pct, 1, sign=False) if ratio else 'n/a':>11}"
        )
    out.line("-" * 70)
    out.line(f"Total across {len(with_oi)} venues: {usd(total)}")
    out.line("24h change is measured in coins, so price moves do not count. n/a: the venue")
    out.line("publishes no hourly history (or account ratio) for this instrument.")
    out.failures(failures)
    out.footer(sources)
    return 0 if with_oi else 2


def cmd_options(args, http: Http, out: Output) -> int:
    report = options_data.build_report(
        http,
        args.symbol,
        expiry_code=args.expiry,
        max_expiries=args.expiries,
        trades_min_usd=args.large_trades,
    )
    failures = [perps.VenueFailure("deribit", f) for f in report.failures]
    if args.format == "json":
        data = {
            "currency": report.currency,
            "put_call_ratio_oi_all_expiries": report.pcr_oi,
            "total_call_oi": report.total_call_oi,
            "total_put_oi": report.total_put_oi,
            "dvol": None
            if report.dvol is None
            else {
                "current": report.dvol.current,
                "low_365d": report.dvol.low_365d,
                "high_365d": report.dvol.high_365d,
                "rank_365d": report.dvol.rank_365d,
                "percentile_365d": report.dvol.percentile_365d,
            },
            "expiries": [
                {
                    "expiry": e.expiry_code,
                    "expiry_time": e.expiry,
                    "underlying_price": e.underlying_price,
                    "call_oi": e.call_oi,
                    "put_oi": e.put_oi,
                    "put_call_ratio_oi": e.pcr_oi,
                    "put_call_ratio_volume": e.pcr_volume,
                    "atm_strike": e.atm_strike,
                    "atm_iv": e.atm_iv,
                    "max_pain": e.max_pain,
                    "max_pain_distance_pct": e.max_pain_distance_pct,
                }
                for e in report.expiries
            ],
            "large_trades": [t.__dict__ for t in report.trades],
        }
        print(envelope(http, "options", [report.currency], data, report.sources, failures))
        return 0

    out.line("")
    out.line(f"{report.currency} options on Deribit (open interest and volume in {report.currency})")
    out.line(
        f"{'Expiry':<9} {'Underlying':>11} {'Call OI':>10} {'Put OI':>10} {'P/C OI':>7} {'P/C vol':>8} {'ATM IV':>7} {'Max pain':>10} {'vs und.':>8}"
    )
    out.line("-" * 88)
    for e in report.expiries:
        out.line(
            f"{e.expiry_code:<9} {e.underlying_price:>11,.0f} {e.call_oi:>10,.1f} {e.put_oi:>10,.1f} "
            f"{ratio(e.pcr_oi):>7} {ratio(e.pcr_volume):>8} "
            f"{(f'{e.atm_iv:.1f}%') if e.atm_iv else 'n/a':>7} {e.max_pain:>10,.0f} {pct(e.max_pain_distance_pct, 1):>8}"
        )
    out.line("-" * 88)
    if report.pcr_oi is not None:
        out.line(f"Put/call ratio by open interest, all live expiries: {report.pcr_oi:.2f}")
    if report.dvol:
        d = report.dvol
        out.line(
            f"DVOL (30-day implied volatility index): {d.current:.1f}   365-day range {d.low_365d:.1f}-{d.high_365d:.1f}   "
            f"rank {d.rank_365d:.0f}   percentile {d.percentile_365d:.0f}"
        )
    out.line("Max pain: the settlement price at which option holders' total intrinsic value is smallest.")
    if args.large_trades is not None:
        out.line("")
        out.line(f"Largest option trades among Deribit's last 1000, notional >= {usd(args.large_trades)}")
        if not report.trades:
            out.line("  none above the threshold")
        for t in report.trades:
            out.line(
                f"  {t.time:%m-%d %H:%M} {t.instrument:<22} taker {t.direction:<4} {t.amount:>8,.1f} "
                f"notional {usd(t.notional_usd):>10} premium {usd(t.premium_usd):>10} "
                f"IV {t.iv if t.iv is not None else 'n/a'}{'  block' if t.block else ''}"
            )
    out.failures(failures)
    out.footer(report.sources)
    return 0


def cmd_basis(args, http: Http, out: Output) -> int:
    points, failures = basis_data.fetch_all(http, args.symbol)
    sources = [p.source for p in points]
    if args.format == "json":
        data = {
            "description": basis_data.describe_curve(points),
            "points": [
                {
                    "venue": p.venue,
                    "instrument": p.instrument,
                    "expiry": p.expiry,
                    "days_to_expiry": p.days_to_expiry,
                    "futures_price": p.futures_price,
                    "index_price": p.index_price,
                    "basis_pct": p.basis_pct,
                    "annualized_pct": p.annualized_pct,
                }
                for p in points
            ],
        }
        print(envelope(http, "basis", [args.symbol], data, sources, failures))
        return 0 if points else 2

    out.line("")
    out.line(f"{args.symbol} dated-futures basis against each venue's index")
    out.line(f"{'Venue':<9} {'Instrument':<16} {'Days':>6} {'Futures':>12} {'Index':>12} {'Basis':>9} {'Annual':>9}")
    out.line("-" * 78)
    for p in points:
        out.line(
            f"{p.venue:<9} {p.instrument:<16} {p.days_to_expiry:>6.1f} {p.futures_price:>12,.2f} "
            f"{p.index_price:>12,.2f} {pct(p.basis_pct, 3):>9} {pct(p.annualized_pct, 2):>9}"
        )
    out.line("-" * 78)
    out.line(basis_data.describe_curve(points))
    out.line("Annual figures scale the basis by days to expiry (simple, not compounded).")
    out.line("Expiries less than 12 hours away are left out.")
    out.failures(failures)
    out.footer(sources)
    return 0 if points else 2


def cmd_liquidations(args, http: Http, out: Output) -> int:
    report = liquidations.fetch(http, args.symbol, hours=args.hours)
    data = {
        "instrument": report.instrument,
        "window_start": report.window_start,
        "window_end": report.window_end,
        "long": {"count": report.count("long"), "value_usd": report.total("long")},
        "short": {"count": report.count("short"), "value_usd": report.total("short")},
        "largest": [o.__dict__ | {"value_usd": o.value_usd} for o in report.largest()],
        "notes": report.notes,
    }
    if args.format == "json":
        print(envelope(http, "liquidations", [args.symbol], data, [report.source], []))
        return 0
    out.line("")
    out.line(f"{report.instrument} filled liquidations on OKX")
    out.line(f"Window: {report.window_start:%Y-%m-%d %H:%M} to {report.window_end:%Y-%m-%d %H:%M} UTC")
    out.line(f"  Longs liquidated:  {report.count('long'):>5} orders  {usd(report.total('long')):>12}")
    out.line(f"  Shorts liquidated: {report.count('short'):>5} orders  {usd(report.total('short')):>12}")
    out.line("")
    out.line("Largest:")
    for o in report.largest():
        out.line(
            f"  {o.time:%m-%d %H:%M}  {o.side:<5}  {o.size_base:>10,.4f} @ {o.price:>12,.2f}  {usd(o.value_usd):>10}"
        )
    for note in report.notes:
        out.line(note)
    out.line("")
    out.line("OKX only: it is the venue here with a public liquidation feed. Other venues'")
    out.line("liquidations are not included, so this is a partial view of the market.")
    out.footer([report.source])
    return 0


def cmd_dashboard(args, http: Http, out: Output) -> int:
    payload, sources, failures = [], [], []
    for symbol in args.symbols:
        snaps, f1 = perps.fetch_all(http, symbol)
        points, f2 = basis_data.fetch_all(http, symbol)
        failures += [perps.VenueFailure(f"{symbol} {f.venue}", f.reason) for f in f1 + f2]
        sources += [s.source for s in snaps] + [p.source for p in points]
        entry = {
            "symbol": symbol,
            "funding": None,
            "open_interest_usd": None,
            "basis": basis_data.describe_curve(points),
        }
        if snaps:
            summary = perps.summarize_funding(snaps)
            total = sum(s.oi_usd for s in snaps if s.oi_usd)
            entry["funding"] = {
                "mean_rate_8h": summary.mean_8h,
                "oi_weighted_rate_8h": summary.oi_weighted_8h,
                "venues": summary.venues,
                "notes": summary.notes,
            }
            entry["open_interest_usd"] = total
            nearest = next((p for p in points if p.days_to_expiry >= 25), points[-1] if points else None)
            entry["reference_basis"] = (
                None
                if nearest is None
                else {
                    "instrument": nearest.instrument,
                    "venue": nearest.venue,
                    "annualized_pct": nearest.annualized_pct,
                }
            )
            if args.format == "console":
                out.line("")
                out.line(f"--- {symbol} ---")
                out.line(
                    f"Funding (8h equiv): mean {pct(summary.mean_8h * 100)}, weighted by open interest "
                    f"{pct(None if summary.oi_weighted_8h is None else summary.oi_weighted_8h * 100)} "
                    f"across {summary.venues} venues"
                )
                for note in summary.notes:
                    out.line(f"  {note}")
                out.line(f"Open interest (one side): {usd(total)} across {sum(1 for s in snaps if s.oi_usd)} venues")
                if nearest:
                    out.line(
                        f"Basis: {nearest.instrument} ({nearest.venue}, {nearest.days_to_expiry:.0f} days) "
                        f"{pct(nearest.annualized_pct, 2)} annualized. {basis_data.describe_curve(points)}"
                    )
                else:
                    out.line("Basis: no dated futures listed")
        payload.append(entry)
    if args.format == "json":
        print(envelope(http, "dashboard", args.symbols, payload, sources, failures))
    else:
        out.failures(failures)
        out.footer(sources)
    return 0 if any(p["funding"] for p in payload) else 2


def cmd_venues(args, http: Http, out: Output) -> int:
    rows = [
        ("okx", "funding, open interest, 24h OI change, account ratio, basis, liquidations"),
        ("deribit", "funding (8h figure), open interest, basis, options (BTC, ETH)"),
        ("hyperliquid", "funding (hourly), open interest"),
        ("kraken", "funding (hourly), open interest"),
        ("kucoin", "funding, open interest"),
        ("gate", "funding, open interest"),
        ("dydx", "funding (hourly), open interest"),
        ("binance", "funding, open interest, 24h OI change, account ratio (refuses US networks)"),
        ("bybit", "funding, open interest, 24h OI change, account ratio (refuses US networks)"),
    ]
    out.line("Venues (all public endpoints, no API key):")
    for name, what in rows:
        out.line(f"  {name:<12} {what}")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--format", choices=["console", "json"], default="console", help="Output format")
    common.add_argument("--demo", action="store_true", help="Replay bundled recorded data (marked, not live)")
    common.add_argument("--record", metavar="PATH", help="Save every raw response to PATH (for demo data or tests)")
    common.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout in seconds")

    parser = argparse.ArgumentParser(
        description="Read-only crypto derivatives research from public exchange data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=DISCLAIMER,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("funding", parents=[common], help="Funding rates per venue")
    p.add_argument("symbols", nargs="+", type=str.upper, help="Coins, e.g. BTC ETH SOL")
    p.add_argument("--venues", help=f"Comma-separated subset of: {','.join(perps.VENUES)}")

    p = sub.add_parser("oi", parents=[common], help="Open interest per venue")
    p.add_argument("symbol", type=str.upper)
    p.add_argument("--venues", help=f"Comma-separated subset of: {','.join(perps.VENUES)}")

    p = sub.add_parser("options", parents=[common], help="Deribit options summary")
    p.add_argument("symbol", type=str.upper, choices=options_data.OPTION_CURRENCIES)
    p.add_argument("--expiry", help="One expiry code, e.g. 27NOV26")
    p.add_argument("--expiries", type=int, default=6, help="Number of nearest expiries to show (default 6)")
    p.add_argument(
        "--large-trades", type=float, metavar="USD", help="Also list recent trades at or above this notional"
    )

    p = sub.add_parser("basis", parents=[common], help="Dated-futures basis")
    p.add_argument("symbol", type=str.upper)

    p = sub.add_parser("liquidations", parents=[common], help="OKX filled liquidations")
    p.add_argument("symbol", type=str.upper)
    p.add_argument("--hours", type=int, default=24, help="Look-back window (default 24)")

    p = sub.add_parser("dashboard", parents=[common], help="Funding, open interest and basis together")
    p.add_argument("symbols", nargs="+", type=str.upper)

    sub.add_parser("venues", parents=[common], help="List venues and what each provides")
    return parser


COMMANDS: dict[str, Callable] = {
    "funding": cmd_funding,
    "oi": cmd_oi,
    "options": cmd_options,
    "basis": cmd_basis,
    "liquidations": cmd_liquidations,
    "dashboard": cmd_dashboard,
    "venues": cmd_venues,
}


def main(argv: Optional[List[str]] = None, http: Optional[Http] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1
    if args.demo and args.record:
        parser.error("--demo and --record cannot be combined")

    if args.demo:
        symbols = getattr(args, "symbols", None) or [getattr(args, "symbol", "BTC")]
        if any(s != "BTC" for s in symbols):
            print(
                "Error: the bundled demo recording covers BTC only. Run without --demo for live data.", file=sys.stderr
            )
            return 2
    if http is None:
        replay = Recording.load(DEMO_RECORDING) if args.demo else None
        http = Http(timeout=args.timeout, replay=replay, record_path=args.record)
    out = Output(demo=http.is_replay)
    if args.format == "console":
        out.header(
            f"{args.command.upper()} {' '.join(getattr(args, 'symbols', None) or [getattr(args, 'symbol', '')])}".strip(),
            http,
        )

    try:
        code = COMMANDS[args.command](args, http, out)
    except FetchError as exc:
        print(f"Error: {exc.reason}", file=sys.stderr)
        code = 2
    except KeyboardInterrupt:
        code = 130
    if args.record:
        http.write_recording(note=f"recorded by {SKILL} {VERSION}: {' '.join(argv or sys.argv[1:])}")
    return code


if __name__ == "__main__":
    sys.exit(main())
