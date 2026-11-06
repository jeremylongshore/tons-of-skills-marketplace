#!/usr/bin/env python3
"""Rank supplied GPU usage/cost findings without claiming telemetry is an invoice.

Offline arithmetic over supplied data. Confirmed amounts require a billing evidence reference;
usage times a supplied rate is an estimate. Rows may overlap, so no additive savings
headline is emitted. The CLI validates the entire input before writing a report.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import html
from datetime import date
import sys

UNCONFIRMED = ("estimated", "at-risk")


def norm_kind(val: object) -> str:
    """Lowercase + strip a confidence tier so case/whitespace never silently drops a
    row from a sum (e.g. "Confirmed" / " AT-RISK " -> "confirmed"/"at-risk")."""
    return str(val or "").strip().lower()


def parse_usd(val: object) -> float:
    """Accept finite, non-negative numeric inputs; never turn missing data into zero."""
    if isinstance(val, bool) or val is None:
        raise ValueError("numeric value is missing or boolean")
    text = str(val).strip()
    if not re.fullmatch(r"\$?(?:[0-9]+(?:\.[0-9]*)?|[0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]*)?)(?:[eE][+-]?[0-9]+)?", text):
        raise ValueError("invalid numeric representation")
    try:
        value = float(text.replace("$", "").replace(",", ""))
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid numeric value") from exc
    if not math.isfinite(value) or value < 0:
        raise ValueError("numeric values must be finite and non-negative")
    return value


def waste_30d(leak: dict) -> float:
    """Calculate a supplied 30-day scenario; preserve estimate/billing distinctions."""
    if not isinstance(leak, dict):
        raise ValueError("each finding must be an object")
    direct = leak.get("waste_30d_usd") is not None
    reprice = leak.get("reprice_rate_usd_per_gpu_hour") is not None
    discount = leak.get("discount_frac") is not None
    if (reprice and discount) or (direct and (reprice or discount)):
        raise ValueError("amount and scenario modifiers are mutually exclusive")
    if direct:
        result = parse_usd(leak["waste_30d_usd"])
    else:
        hours = parse_usd(leak.get("usage_gpu_hours"))
        rate = parse_usd(leak.get("rate_usd_per_gpu_hour"))
        if reprice:
            result = hours * max(0, rate - parse_usd(leak["reprice_rate_usd_per_gpu_hour"]))
        elif discount:
            fraction = parse_usd(leak["discount_frac"])
            if fraction > 1:
                raise ValueError("discount_frac must be between 0 and 1")
            result = hours * rate * fraction
        else:
            result = hours * rate
    if not math.isfinite(result) or not math.isfinite(to_monthly(result)):
        raise ValueError("calculated amount exceeds finite range")
    return result


def to_monthly(w30: float) -> float:
    """30-day window -> calendar-month figure (365/12 days per month)."""
    return w30 * (365.0 / 12.0) / 30.0


def fmt_money_full(n: float) -> str:
    """Full-digit dollars, no decimals: 12000 -> $12,000."""
    return f"${round(n):,}"


def fmt_money_k(n: float) -> str:
    """K-abbreviated annualized dollars: 264000 -> $264K."""
    return f"${round(n / 1000):,}K"


def _cell(value: object) -> str:
    return html.escape(str(value), quote=False).replace("|", "&#124;").replace("\n", " ").replace("\r", " ")


def build_report(leaks: list[dict], monthly_spend: float | None, window_end: str | None) -> str:
    if not isinstance(leaks, list):
        raise ValueError("findings must be an array")
    if window_end:
        date.fromisoformat(window_end)
    if monthly_spend is not None:
        monthly_spend = parse_usd(monthly_spend)
    ranked = []
    for finding in leaks:
        amount = waste_30d(finding)
        kind = norm_kind(finding.get("kind")) or "estimated"
        if kind not in ("confirmed", *UNCONFIRMED):
            raise ValueError("kind must be confirmed, estimated, or at-risk")
        if not all(isinstance(finding.get(k), str) and finding[k].strip() for k in ("category", "root_cause", "fix")):
            raise ValueError("category, root_cause and fix must be non-empty strings")
        if kind == "confirmed":
            evidence = finding.get("billing_evidence")
            if not isinstance(evidence, str) or not evidence.strip() or finding.get("waste_30d_usd") is None:
                raise ValueError("confirmed findings need a supplied billed amount and billing_evidence reference")
        ranked.append({**finding, "kind": kind, "monthly": to_monthly(amount)})
    ranked.sort(key=lambda item: item["monthly"], reverse=True)
    window = f"30-day input window ending {window_end}" if window_end else "30-day input window (end not supplied)"
    lines = [
        "# GPU usage and cost review",
        "",
        window + ".",
        "Monthly equivalents use 365/12 days. These are scenarios, not an invoice or guaranteed savings.",
        "Rows may overlap: do not add them together. No automatic capacity or contract change is authorized.",
        "",
    ]
    if monthly_spend is not None:
        lines += [
            f"Owner-supplied monthly spend context: {fmt_money_full(monthly_spend)} (not independently verified).",
            "",
        ]
    if not ranked:
        lines += ["No findings supplied. This does not establish that usage, access, or billing is healthy.", ""]
    for kind, label in (
        ("confirmed", "Billing-backed supplied amounts"),
        ("estimated", "Telemetry and pricing estimates"),
        ("at-risk", "Contract-dependent scenarios"),
    ):
        rows = [row for row in ranked if row["kind"] == kind]
        if not rows:
            continue
        lines += [
            f"## {label}",
            "",
            "| Finding | Monthly equivalent | Evidence / assumptions | Proposed review |",
            "|---|---:|---|---|",
        ]
        for row in rows:
            evidence = (
                row.get("billing_evidence")
                or row.get("evidence")
                or "Source, rate, coverage and capacity plan need review"
            )
            lines.append(
                f"| {_cell(row['category'])}: {_cell(row['root_cause'])} | {fmt_money_full(row['monthly'])} | {_cell(evidence)} | {_cell(row['fix'])} |"
            )
        lines.append("")
    lines += [
        "## Interpretation",
        "",
        "Usage multiplied by a supplied rate estimates exposure; it does not establish avoidable or recoverable spend.",
        "Check reservation terms, Flex holding/usage rates, taxes, credits, sampling coverage, checkpoint periods and overlap.",
        "CoreWeave provides cost/usage monitoring and Mission Control MCP billing tools; reconcile eligible billing records when available.",
        "A billing reference is supplied evidence, not independent verification by this offline script.",
        "",
    ]
    return "\n".join(lines)


def _load(raw: str) -> list[dict]:
    data = json.loads(raw)
    if isinstance(data, dict):
        if "leaks" in data:
            data = data["leaks"]
        elif "categories" in data:
            data = data["categories"]
        else:
            raise ValueError("object must contain a findings array")
    if not isinstance(data, list):
        raise ValueError("input must be an array or an object containing a leaks/categories array")
    return data


def self_test() -> int:
    sample = {
        "category": "Idle allocation",
        "root_cause": "review workload phase",
        "fix": "owner review",
        "usage_gpu_hours": 100,
        "rate_usd_per_gpu_hour": 2,
    }
    assert waste_30d(sample) == 200
    assert waste_30d({**sample, "discount_frac": 0.4}) == 80
    assert waste_30d({**sample, "reprice_rate_usd_per_gpu_hour": 1}) == 100
    report = build_report([sample], 1000, "2026-11-05")
    assert "Telemetry and pricing estimates" in report and "not an invoice" in report
    assert "Billing-backed supplied amounts" not in report
    for value in [None, True, -1, "NaN", "Infinity", "unknown"]:
        try:
            parse_usd(value)
        except ValueError:
            continue
        raise AssertionError(f"accepted invalid numeric input: {value!r}")
    print("SELF-TEST PASSED: arithmetic, estimate default, billing boundary and numeric refusal")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", default="-")
    ap.add_argument("--out", dest="outfile")
    ap.add_argument("--monthly-spend", type=float, default=None)
    ap.add_argument("--window-end", dest="window_end", default=None)
    ap.add_argument("--self-test", action="store_true", help="run the built-in self-test and exit")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.outfile:
        print("error: --out is required (or pass --self-test)", file=sys.stderr)
        return 1

    if args.infile == "-":
        if sys.stdin.isatty():
            print("error: no input on stdin (pipe JSON in, or pass --in <file>)", file=sys.stderr)
            ap.print_help(sys.stderr)
            return 1
        raw = sys.stdin.read()
    else:
        with open(args.infile, encoding="utf-8") as fh:
            raw = fh.read()

    try:
        leaks = _load(raw)
        report = build_report(leaks, args.monthly_spend, args.window_end)
    except (json.JSONDecodeError, ValueError) as exc:
        detail = "empty input" if not raw.strip() else str(exc)
        print(f"error: could not parse input ({detail})", file=sys.stderr)
        return 1

    with open(args.outfile, "w", encoding="utf-8") as fh:
        fh.write(report)
    print(f"wrote {args.outfile} ({len(leaks)} leaks ranked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
