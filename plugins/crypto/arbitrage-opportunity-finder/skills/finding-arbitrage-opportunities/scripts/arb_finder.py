#!/usr/bin/env python3
"""
Arbitrage spread finder: read-only, from live public order-book data.

Commands:
    scan BASE QUOTE        Best bid and ask per venue for one exact pair, and every
                           cross-venue spread, gross and net of assumed taker fees
    triangular VENUE       Three-trade cycles within one venue (okx, kucoin, gate)
    monitor BASE QUOTE     Repeat the scan every N seconds and print the widest spread
    venues                 Venues and the fee each one is assumed to charge

Figures come from public, keyless endpoints and carry their source. A venue that
fails is named with the reason. Nothing here places orders.

Usage:
    python arb_finder.py scan BTC USDT
    python arb_finder.py scan ETH USD --venues kraken,coinbase,bitfinex --fee coinbase=0.6
    python arb_finder.py scan SOL USDT --amount 25 --format json
    python arb_finder.py triangular kucoin --fee kucoin=0.1 --min-volume-usd 500000
    python arb_finder.py monitor BTC USDT --interval 15 --count 8
    python arb_finder.py scan BTC USDT --demo
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import spot_venues
import spreads
from http_client import FetchError, Http, Recording

VERSION = "2.0.0"
SKILL = "finding-arbitrage-opportunities"
DISCLAIMER = "Research output only. Not financial advice. This tool places no trades."
CAVEAT = (
    "Not included: withdrawal and network fees, time to move funds between venues, "
    "price moves meanwhile, and depth beyond the best bid and ask."
)
DEMO_RECORDING = Path(__file__).resolve().parent.parent / "assets" / "demo-recording.json"
DEMO_PAIRS = {("BTC", "USDT"), ("ETH", "USD")}


class Output:
    def __init__(self, demo: bool):
        self.demo = demo

    def line(self, text: str = "") -> None:
        prefix = "[DEMO] " if self.demo else ""
        for part in text.split("\n"):
            print(f"{prefix}{part}".rstrip())

    def header(self, title: str, http: Http) -> None:
        self.line("=" * 76)
        self.line(f" {title}")
        when = http.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        if self.demo:
            self.line(f" Recorded data from {when}, not live. Run without --demo for live data.")
        else:
            self.line(f" Live public data fetched {when}")
        self.line("=" * 76)

    def failures(self, failures) -> None:
        if failures:
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


def envelope(http: Http, command: str, subject: List[str], data, sources, failures) -> str:
    doc = {
        "skill": SKILL,
        "version": VERSION,
        "command": command,
        "subject": subject,
        "generated_at": http.now().isoformat().replace("+00:00", "Z"),
        "mode": "demo" if http.is_replay else "live",
        "sources": list(dict.fromkeys(sources)),
        "failures": [{"venue": f.venue, "reason": f.reason} for f in failures],
        "data": data,
        "not_included": CAVEAT,
        "disclaimer": DISCLAIMER,
    }
    if http.is_replay:
        doc["demo_note"] = "Replayed recording of real responses; not live data."
    return json.dumps(doc, indent=2, default=str)


def pct(value: Optional[float], digits: int = 4) -> str:
    return "n/a" if value is None else f"{value:+.{digits}f}%"


def fee(value: Optional[float]) -> str:
    return "unknown" if value is None else f"{value:.2f}%"


def parse_fees(items: Optional[List[str]]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for item in items or []:
        for part in item.split(","):
            if not part.strip():
                continue
            if "=" not in part:
                raise SystemExit(f"--fee expects VENUE=PERCENT, got {part!r}")
            venue, value = part.split("=", 1)
            venue = venue.strip().lower()
            if venue not in spot_venues.ADAPTERS:
                raise SystemExit(f"Unknown venue in --fee: {venue}. Known: {', '.join(spot_venues.ADAPTERS)}")
            number = float(value.strip().rstrip("%"))
            if not 0 <= number < 5:
                raise SystemExit(f"--fee {venue}={number} looks wrong; give a percent such as 0.1")
            out[venue] = number
    return out


def parse_venues(value: Optional[str]) -> Optional[List[str]]:
    if not value:
        return None
    names = [v.strip().lower() for v in value.split(",") if v.strip()]
    unknown = [v for v in names if v not in spot_venues.ADAPTERS]
    if unknown:
        raise SystemExit(f"Unknown venue(s): {', '.join(unknown)}. Known: {', '.join(spot_venues.ADAPTERS)}")
    return names


def quote_dict(q: spot_venues.Quote) -> dict:
    return {
        "venue": q.venue,
        "symbol": q.symbol,
        "bid": q.bid,
        "ask": q.ask,
        "bid_size": q.bid_size,
        "ask_size": q.ask_size,
        "book_spread_pct": q.spread_pct,
        "taker_fee_pct": q.taker_fee_pct,
        "fee_source": q.fee_source,
        "latency_ms": round(q.latency_ms),
        "source": q.source,
    }


def spread_dict(s: spreads.CrossSpread, amount: Optional[float]) -> dict:
    d = {
        "buy_venue": s.buy.venue,
        "buy_ask": s.buy.ask,
        "sell_venue": s.sell.venue,
        "sell_bid": s.sell.bid,
        "gross_pct": s.gross_pct,
        "net_pct": s.net_pct,
        "size_at_best_prices": s.top_size,
    }
    if amount is not None and s.net_pct is not None:
        d["amount"] = amount
        d["net_quote_amount"] = amount * s.buy.ask * s.net_pct / 100
    return d


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_scan(args, http: Http, out: Output) -> int:
    base, quote = args.base, args.quote
    quotes, failures = spot_venues.fetch_quotes(http, base, quote, parse_venues(args.venues), parse_fees(args.fee))
    all_spreads = spreads.cross_spreads(quotes)
    sources = [q.source for q in quotes]
    shown = all_spreads[: args.top]
    if args.format == "json":
        data = {
            "pair": f"{base}/{quote}",
            "quotes": [quote_dict(q) for q in sorted(quotes, key=lambda q: q.mid)],
            "spreads": [spread_dict(s, args.amount) for s in shown],
            "notes": spreads.describe(all_spreads),
        }
        print(envelope(http, "scan", [base, quote], data, sources, failures))
        return 0 if quotes else 2

    out.line("")
    out.line(f"{base}/{quote} best bid and ask by venue")
    out.line(f"{'Venue':<10} {'Symbol':<12} {'Bid':>14} {'Ask':>14} {'Book spread':>12} {'Taker fee':>10}")
    out.line("-" * 76)
    for q in sorted(quotes, key=lambda q: q.mid):
        out.line(
            f"{q.venue:<10} {q.symbol:<12} {q.bid:>14,.6g} {q.ask:>14,.6g} {q.spread_pct:>11.4f}% {fee(q.taker_fee_pct):>10}"
        )
    if len(quotes) >= 2:
        out.line("")
        out.line(f"Cross-venue spreads (buy at ask, sell at bid), top {len(shown)} by gross")
        out.line(f"{'Buy':<10} {'Sell':<10} {'Gross':>10} {'Net of fees':>12} {'Size at best':>14}")
        out.line("-" * 60)
        for s in shown:
            size = "n/a" if s.top_size is None else f"{s.top_size:,.6g} {base}"
            out.line(f"{s.buy.venue:<10} {s.sell.venue:<10} {pct(s.gross_pct):>10} {pct(s.net_pct):>12} {size:>14}")
        if args.amount is not None:
            best_net = next((s for s in all_spreads if s.net_pct is not None), None)
            if best_net:
                value = args.amount * best_net.buy.ask * best_net.net_pct / 100
                out.line(
                    f"\nFor {args.amount:g} {base} on {best_net.buy.venue} -> {best_net.sell.venue}: "
                    f"net {value:+,.2f} {quote} after assumed taker fees (before transfer costs)."
                )
    out.line("")
    for note in spreads.describe(all_spreads):
        out.line(note)
    out.line("Net uses each venue's assumed taker fee (`venues` lists them); n/a means the fee is unknown,")
    out.line("set it with --fee VENUE=PERCENT. " + CAVEAT)
    out.failures(failures)
    out.footer(sources)
    return 0 if quotes else 2


def cmd_triangular(args, http: Http, out: Output) -> int:
    venue = args.venue
    overrides = parse_fees(args.fee)
    if venue in overrides:
        fee_pct, fee_source = overrides[venue], "set with --fee"
    elif spot_venues.FEES[venue].taker_pct is not None:
        fee_pct, fee_source = spot_venues.FEES[venue].taker_pct, spot_venues.FEES[venue].source
    elif venue == "gate":
        fee_pct = spot_venues.gate_fee(http, "BTC", "USDT")
        fee_source = "Gate pair listing (BTC_USDT fee field)"
        if fee_pct is None:
            raise FetchError("could not read Gate's fee; pass --fee gate=PERCENT")
    else:
        raise FetchError(f"no confirmed fee for {venue}; pass --fee {venue}=PERCENT")
    found, evaluated, url = spreads.find_triangles(http, venue, args.start, fee_pct, args.min_volume_usd, args.top)
    data = {
        "venue": venue,
        "start": args.start,
        "taker_fee_pct_per_leg": fee_pct,
        "fee_source": fee_source,
        "min_volume_usd": args.min_volume_usd,
        "triangles_evaluated": evaluated,
        "best": [t.__dict__ for t in found],
    }
    if args.format == "json":
        print(envelope(http, "triangular", [venue, args.start], data, [url], []))
        return 0
    out.line("")
    out.line(f"Triangles on {venue} starting and ending in {args.start}")
    out.line(
        f"Pairs with at least ${args.min_volume_usd:,.0f} of 24h volume; taker fee {fee_pct:.2f}% per leg ({fee_source})"
    )
    out.line(f"Evaluated {evaluated} triangles.")
    if not found:
        out.line("No triangle could be formed from pairs above the volume floor; lower --min-volume-usd to widen it.")
    else:
        out.line("")
        out.line(f"{'Path':<30} {'Gross':>10} {'Net of fees':>12}")
        out.line("-" * 54)
        for t in found:
            out.line(f"{' -> '.join(t.path):<30} {pct(t.gross_pct):>10} {pct(t.net_pct):>12}")
        positive = [t for t in found if t.net_pct > 0]
        out.line("")
        if positive:
            out.line(f"{len(positive)} triangle(s) stay positive after fees at the best prices shown.")
            out.line("Legs of the best one:")
            for leg in found[0].legs:
                out.line(f"  {leg}")
        else:
            out.line("No triangle stays positive after three taker fees.")
    out.line("Uses the best bid and ask of each pair at one moment; depth and latency are not included.")
    out.footer([url])
    return 0


def cmd_monitor(args, http: Http, out: Output) -> int:
    if http.is_replay:
        raise FetchError("monitor needs live data; it cannot run with --demo")
    venues, overrides = parse_venues(args.venues), parse_fees(args.fee)
    out.line(f"Scanning {args.base}/{args.quote} every {args.interval:g}s, {args.count} times")
    out.line(
        f"{'Time (UTC)':<10} {'Venues':>6}  {'Widest gross (buy > sell)':<34} {'Best net (buy > sell)':<34} {'Flag':<5}"
    )
    for i in range(args.count):
        now = time.strftime("%H:%M:%S", time.gmtime())
        quotes, _ = spot_venues.fetch_quotes(Http(timeout=args.timeout), args.base, args.quote, venues, overrides)
        ranked = spreads.cross_spreads(quotes)
        if ranked:
            top = ranked[0]
            with_net = [s for s in ranked if s.net_pct is not None]
            best_net = max(with_net, key=lambda s: s.net_pct) if with_net else None
            gross_txt = f"{pct(top.gross_pct)} {top.buy.venue} > {top.sell.venue}"
            net_txt = (
                f"{pct(best_net.net_pct)} {best_net.buy.venue} > {best_net.sell.venue}"
                if best_net
                else "n/a (fees unknown)"
            )
            flag = ""
            if args.threshold is not None and best_net is not None and best_net.net_pct >= args.threshold:
                flag = "ABOVE"
            out.line(f"{now:<10} {len(quotes):>6}  {gross_txt:<34} {net_txt:<34} {flag:<5}")
        else:
            out.line(f"{now:<10} {len(quotes):>6}  fewer than two venues answered")
        if i < args.count - 1:
            time.sleep(args.interval)
    out.line("")
    if args.threshold is not None:
        out.line(f"ABOVE marks a net spread at or above {args.threshold}% after assumed taker fees.")
    out.line(CAVEAT)
    out.line(DISCLAIMER)
    return 0


def cmd_venues(args, http: Http, out: Output) -> int:
    out.line(f"Spot venues and assumed base-tier taker fees (checked {spot_venues.FEES_CHECKED}):")
    for name in spot_venues.ADAPTERS:
        a = spot_venues.FEES[name]
        value = "live from API" if name == "gate" else fee(a.taker_pct)
        out.line(f"  {name:<10} {value:>13}  {a.source}")
    out.line("")
    out.line("Your real fee depends on your tier, region and token discounts; set it with --fee VENUE=PERCENT.")
    out.line("Binance and Bybit refuse US networks. Triangular search supports okx, kucoin and gate.")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--format", choices=["console", "json"], default="console")
    common.add_argument("--demo", action="store_true", help="Replay bundled recorded data (marked, not live)")
    common.add_argument("--record", metavar="PATH", help="Save every raw response to PATH")
    common.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout in seconds")
    common.add_argument(
        "--fee", action="append", metavar="VENUE=PCT", help="Your taker fee for a venue, in percent; repeatable"
    )

    parser = argparse.ArgumentParser(
        description="Read-only crypto arbitrage spreads from public order-book data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=DISCLAIMER,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("scan", parents=[common], help="Cross-venue spreads for one pair")
    p.add_argument("base", type=str.upper, help="Base asset, e.g. BTC")
    p.add_argument("quote", type=str.upper, help="Quote asset, e.g. USDT, USD, USDC")
    p.add_argument("--venues", help=f"Comma-separated subset of: {','.join(spot_venues.ADAPTERS)}")
    p.add_argument("--top", type=int, default=10, help="Spreads to show (default 10)")
    p.add_argument("--amount", type=float, help="Base units, to express the best net spread in quote currency")

    p = sub.add_parser("triangular", parents=[common], help="Three-trade cycles on one venue")
    p.add_argument("venue", choices=sorted(spreads.TRIANGLE_VENUES))
    p.add_argument("--start", type=str.upper, default="USDT", help="Asset to start and end in (default USDT)")
    p.add_argument(
        "--min-volume-usd", type=float, default=1_000_000, help="Ignore pairs below this 24h volume (default 1,000,000)"
    )
    p.add_argument("--top", type=int, default=10)

    p = sub.add_parser("monitor", parents=[common], help="Repeat a scan on an interval")
    p.add_argument("base", type=str.upper)
    p.add_argument("quote", type=str.upper)
    p.add_argument("--venues")
    p.add_argument("--interval", type=float, default=10.0, help="Seconds between scans (minimum 5)")
    p.add_argument("--count", type=int, default=6, help="Number of scans (default 6)")
    p.add_argument("--threshold", type=float, help="Mark scans whose best net spread is at or above this percent")

    sub.add_parser("venues", parents=[common], help="Venues and assumed fees")
    return parser


COMMANDS = {"scan": cmd_scan, "triangular": cmd_triangular, "monitor": cmd_monitor, "venues": cmd_venues}


def main(argv: Optional[List[str]] = None, http: Optional[Http] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1
    if args.demo and args.record:
        parser.error("--demo and --record cannot be combined")
    if args.command == "monitor" and args.interval < 5:
        parser.error("--interval must be at least 5 seconds; public endpoints rate-limit fast polling")
    if args.demo:
        covered = (args.command == "scan" and (args.base, args.quote) in DEMO_PAIRS) or (
            args.command == "triangular" and args.venue == "okx"
        )
        if not covered and args.command != "venues":
            print(
                "Error: the bundled demo recording covers scan BTC USDT, scan ETH USD and triangular okx. "
                "Run without --demo for live data.",
                file=sys.stderr,
            )
            return 2
    if http is None:
        replay = Recording.load(DEMO_RECORDING) if args.demo else None
        http = Http(timeout=args.timeout, replay=replay, record_path=args.record)
    out = Output(demo=http.is_replay)
    if args.format == "console" and args.command != "monitor":
        subject = " ".join(str(getattr(args, k)) for k in ("base", "quote", "venue") if getattr(args, k, None))
        out.header(f"{args.command.upper()} {subject}".strip(), http)
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
