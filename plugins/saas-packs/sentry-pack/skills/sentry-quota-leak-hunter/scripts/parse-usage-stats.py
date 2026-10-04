#!/usr/bin/env python3
"""Parse Sentry org stats usage by category.

Outcomes stay separate. This script never sums accepted + filtered + dropped
into one "lost events" number (CQ08). It never invents a dollar figure.
Category fan-out is this script plus usage-auditor — it does not name
per-category spend agents.

Read-only. `--apply` calls sentry_readonly.refuse_write.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_LIB = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if _LIB.is_dir() and str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from sentry_readonly import (  # noqa: E402
    SentryReadOnlyError,
    client_from_env,
)

# Outcomes the usage API may return. Do not fold one into another.
KNOWN_OUTCOMES = (
    "accepted",
    "filtered",
    "dropped",
    "rate_limited",
    "invalid",
    "client_discard",
    "abuse",
    "cardinality_limited",
)

# Unofficial price keys. Presence is recorded and ignored.
UNOFFICIAL_PRICE_KEYS = (
    "per_event_usd",
    "third_party_per_event_usd",
    "overage_usd_unofficial",
    "danube_per_event_usd",
    "list_price_usd",
)


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    return None


def _blank() -> dict[str, int]:
    return {name: 0 for name in ("accepted", "filtered", "dropped")}


def _ensure(cats: dict[str, dict[str, int]], category: str) -> dict[str, int]:
    slot = cats.setdefault(category, {})
    return slot


def _add(cats: dict[str, dict[str, int]], category: str, outcome: str, qty: int) -> None:
    slot = _ensure(cats, category)
    slot[outcome] = slot.get(outcome, 0) + qty


def from_category_map(categories: dict[str, Any]) -> dict[str, dict[str, int]]:
    """Fixture shape: {categories: {error: {accepted, filtered, dropped}}}."""
    cats: dict[str, dict[str, int]] = {}
    for name, outcomes in categories.items():
        if not isinstance(outcomes, dict):
            raise SentryReadOnlyError(f"category {name!r} must be an object of outcomes, not {type(outcomes).__name__}")
        for outcome, qty in outcomes.items():
            n = _as_int(qty)
            if n is None:
                raise SentryReadOnlyError(f"category {name!r} outcome {outcome!r} is not a number")
            _add(cats, str(name), str(outcome), n)
    return cats


def from_outcome_maps(data: dict[str, Any]) -> dict[str, dict[str, int]] | None:
    """Fixture shape: {accepted: {error: N}, filtered: {...}, dropped: {...}}."""
    present = [k for k in KNOWN_OUTCOMES if isinstance(data.get(k), dict)]
    if not present:
        return None
    cats: dict[str, dict[str, int]] = {}
    for outcome in present:
        for category, qty in data[outcome].items():
            n = _as_int(qty)
            if n is None:
                raise SentryReadOnlyError(f"{outcome}.{category} is not a number")
            _add(cats, str(category), outcome, n)
    return cats


def _total_from_group(group: dict[str, Any]) -> int | None:
    totals = group.get("totals")
    if isinstance(totals, dict):
        for key in ("sum(quantity)", "quantity", "sum"):
            n = _as_int(totals.get(key))
            if n is not None:
                return n
    series = group.get("series")
    if isinstance(series, dict):
        for key in ("sum(quantity)", "quantity"):
            points = series.get(key)
            if (
                isinstance(points, list)
                and points
                and all(isinstance(p, (int, float)) and not isinstance(p, bool) for p in points)
            ):
                return int(sum(points))
    return None


def from_groups(groups: list[Any]) -> dict[str, dict[str, int]]:
    """Live-shaped usage payload: groups[].by.category + by.outcome + totals."""
    cats: dict[str, dict[str, int]] = {}
    for group in groups:
        if not isinstance(group, dict):
            raise SentryReadOnlyError("stats groups[] entries must be objects")
        by = group.get("by") or {}
        if not isinstance(by, dict):
            raise SentryReadOnlyError("stats group.by must be an object")
        category = by.get("category") or by.get("reason") or "unspecified"
        outcome = str(by.get("outcome") or "unspecified")
        qty = _total_from_group(group)
        if qty is None:
            raise SentryReadOnlyError(f"group category={category!r} outcome={outcome!r} has no numeric total")
        _add(cats, str(category), outcome, qty)
    return cats


def normalize(data: dict[str, Any]) -> dict[str, dict[str, int]]:
    categories = data.get("categories")
    if isinstance(categories, dict):
        return from_category_map(categories)
    outcome_maps = from_outcome_maps(data)
    if outcome_maps is not None:
        return outcome_maps
    groups = data.get("groups")
    if isinstance(groups, list):
        return from_groups(groups)
    raise SentryReadOnlyError("unrecognized stats JSON: expected categories{}, outcome maps, or groups[]")


def dollar_report(data: dict[str, Any]) -> dict[str, Any]:
    cited = data.get("subscription_screen_usd")
    unofficial = [k for k in UNOFFICIAL_PRICE_KEYS if k in data]
    # Any other *usd* / price key that is not the subscription screen is unofficial.
    for key in data:
        if key in ("subscription_screen_usd",):
            continue
        lowered = key.lower()
        if any(tok in lowered for tok in ("usd", "dollar", "price", "cost")):
            if key not in unofficial:
                unofficial.append(key)
    if cited is None:
        return {
            "dollars": None,
            "dollar_source": None,
            "ignored_unofficial_price_keys": unofficial,
            "dollar_note": (
                "No subscription_screen_usd in the payload. "
                "Do not invent a per-event dollar figure. "
                "The customer's subscription screen is the price."
            ),
        }
    return {
        "dollars": cited if isinstance(cited, (int, float)) and not isinstance(cited, bool) else None,
        "dollar_source": "customer_subscription_screen_field",
        "ignored_unofficial_price_keys": unofficial,
        "dollar_note": (
            "Only subscription_screen_usd is cited, and only because the payload "
            "carried it. Third-party per-event prices are ignored."
        ),
    }


def build_report(data: dict[str, Any], *, mode: str) -> dict[str, Any]:
    cats = normalize(data)
    # Stable key order: accepted, filtered, dropped, then any other outcome alpha.
    ordered: dict[str, dict[str, int]] = {}
    for name in sorted(cats):
        slot = cats[name]
        preferred = [o for o in ("accepted", "filtered", "dropped") if o in slot]
        rest = sorted(k for k in slot if k not in preferred)
        ordered[name] = {k: slot[k] for k in preferred + rest}

    highest = None
    highest_n = -1
    with_drops: list[str] = []
    with_filtered: list[str] = []
    for name, slot in ordered.items():
        acc = slot.get("accepted", 0)
        if acc > highest_n:
            highest_n = acc
            highest = name
        if slot.get("dropped", 0) or slot.get("rate_limited", 0):
            with_drops.append(name)
        if slot.get("filtered", 0):
            with_filtered.append(name)

    previous = data.get("previous_window")
    moved = None
    if isinstance(previous, dict):
        prev_cats = (
            normalize(previous)
            if (
                "categories" in previous
                or "groups" in previous
                or any(isinstance(previous.get(o), dict) for o in KNOWN_OUTCOMES)
            )
            else None
        )
        if prev_cats is not None:
            deltas = []
            for name, slot in ordered.items():
                prev = prev_cats.get(name, {}).get("accepted", 0)
                deltas.append((slot.get("accepted", 0) - prev, name))
            deltas.sort(reverse=True)
            if deltas:
                moved = {"category": deltas[0][1], "accepted_delta": deltas[0][0]}

    return {
        "mode": mode,
        "org": data.get("org"),
        "window": data.get("window") or data.get("statsPeriod"),
        "categories": ordered,
        "highest_accepted_category": highest,
        "categories_with_filtered": with_filtered,
        "categories_with_dropped_or_rate_limited": with_drops,
        "meter_that_moved": moved,
        "lost_events_total": None,
        "lost_events_reason": (
            "Refused. filtered, dropped, and rate_limited are different outcomes. "
            "accepted + filtered + dropped is not a number this script will print."
        ),
        "category_agents": [],
        "fanout": "script + usage-auditor only",
        **dollar_report(data),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        dest="json_path",
        help="Path to pasted stats JSON (advisory). Reads stdin when '-'.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Refused. This client does not write to Sentry.",
    )
    parser.add_argument(
        "--sum-lost",
        action="store_true",
        help="Refused. Asks for the forbidden accepted+filtered+dropped sum.",
    )
    args = parser.parse_args(argv)

    client = client_from_env()
    if args.apply:
        try:
            client.refuse_write("apply stats filter / discard / sample rate")
        except SentryReadOnlyError as exc:
            print(json.dumps({"ok": False, "error": str(exc), "wrote": False}))
            return 2

    if args.sum_lost:
        print(
            json.dumps(
                {
                    "ok": False,
                    "lost_events_total": None,
                    "error": ("refusing to sum accepted + filtered + dropped. Report each outcome on its own."),
                }
            )
        )
        return 2

    mode = "advisory"
    if args.json_path:
        raw = sys.stdin.read() if args.json_path == "-" else Path(args.json_path).read_text()
        try:
            data = client.fetch_org_stats_usage(pasted=raw)
        except SentryReadOnlyError as exc:
            print(json.dumps({"ok": False, "mode": "advisory", "error": str(exc)}))
            return 2
        mode = "advisory"
    else:
        try:
            data = client.fetch_org_stats_usage()
            mode = "live"
        except SentryReadOnlyError as exc:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "mode": "advisory",
                        "org_guessed": None,
                        "error": str(exc),
                        "hint": "Pass --json <file> with pasted stats. Do not guess an org slug.",
                    }
                )
            )
            return 2

    try:
        report = build_report(data, mode=mode)
    except SentryReadOnlyError as exc:
        print(json.dumps({"ok": False, "mode": mode, "error": str(exc)}))
        return 2
    report["ok"] = True
    report["wrote"] = False
    print(json.dumps(report, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
