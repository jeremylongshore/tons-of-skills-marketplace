#!/usr/bin/env python3
"""Decide whether a release-health session query may be called fine.

RL08: the sessions stats API returns at most 10,000 datapoints.
A 90-day window grouped by release is at most floor(10000/91) = 109 releases.
session.duration stopped being recorded on 2023-01-12.

health_fine is true only when the API was actually read, the query is scoped
to one project + one environment + one release, the datapoint estimate is under
the cap, and session.duration is not a requested field.

Read-only. Does not record a deploy.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_LIB = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if _LIB.is_dir() and str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from sentry_readonly import SentryReadOnlyError, client_from_env  # noqa: E402

CAP = 10_000
DURATION_STOPPED = "2023-01-12"
PERIOD_RE = re.compile(r"^(\d+)([dhm])$")


def _period_to_days(period: str) -> float | None:
    match = PERIOD_RE.match(period.strip())
    if not match:
        return None
    n = int(match.group(1))
    unit = match.group(2)
    if unit == "d":
        return float(n)
    if unit == "h":
        return n / 24.0
    return n / (24.0 * 60.0)


def _interval_to_days(interval: str) -> float | None:
    return _period_to_days(interval)


def assess(payload: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    query = payload.get("query") if isinstance(payload.get("query"), dict) else payload
    api_read = bool(payload.get("api_read") is True)
    if not api_read:
        reasons.append("health API was not read (api_read is not true). Do not mark release health fine.")

    fields = query.get("fields") or query.get("field") or []
    if isinstance(fields, str):
        fields = [fields]
    if not isinstance(fields, list):
        fields = []
    duration = any(isinstance(f, str) and "session.duration" in f for f in fields)
    if duration:
        reasons.append(
            f"session.duration stopped being recorded on {DURATION_STOPPED}. "
            "Do not alert on it. The API may still list the aggregate and warn data is incomplete."
        )

    group_by = query.get("groupBy") or query.get("groupby") or []
    if isinstance(group_by, str):
        group_by = [group_by]
    if not isinstance(group_by, list):
        group_by = []

    stats_period = str(query.get("statsPeriod") or query.get("stats_period") or "")
    interval = str(query.get("interval") or "1d")
    window_days = _period_to_days(stats_period) if stats_period else None
    interval_days = _interval_to_days(interval)
    buckets = None
    max_groups = None
    if window_days and interval_days and interval_days > 0:
        # Inclusive day count matches the docs' 90d -> 91 example when interval is 1d.
        # Use the documented formula when it is 90d/1d; otherwise ceil(window/interval)+?
        # Docs: 90-day window grouped by release returns at most floor(10000/91)=109.
        if stats_period == "90d" and interval in ("1d", "1 day"):
            buckets = 91
        else:
            buckets = int(window_days / interval_days) + 1
        if buckets > 0:
            max_groups = CAP // buckets
        if buckets >= CAP:
            reasons.append(
                f"interval buckets ({buckets}) already meet the {CAP} datapoint cap before groupBy multiplies them."
            )

    project = query.get("project") or query.get("projects")
    environment = query.get("environment")
    release = query.get("release")
    scoped = bool(project) and bool(environment) and bool(release)
    broad_group = ("release" in group_by) and not project
    if broad_group:
        reasons.append(
            "groupBy includes release without a project filter. An org-wide crash-free number is not one number."
        )
    if not scoped:
        reasons.append("Not scoped to one project + one environment + one release. Do not call the series fine.")
    # Cap warning applies when the query can return many release groups,
    # not when it is already pinned to a single release (datapoints ~= buckets).
    if max_groups is not None and not release and "release" in group_by:
        reasons.append(
            f"Query can hit the {CAP} datapoint cap: about {buckets} buckets, "
            f"so at most {max_groups} release groups. A missing noisy release is a false pass. "
            "Narrow to one project, one environment, and the release you just shipped."
        )
    if buckets is not None and buckets > CAP:
        reasons.append(f"interval buckets ({buckets}) exceed the {CAP} datapoint cap.")

    if stats_period == "90d" and "release" in group_by:
        reasons.append(
            "90-day groupBy=release is the documented 10k datapoint cap "
            "(floor(10000/91)=109 releases). Do not mark health fine on that query shape."
        )
    groups_returned = payload.get("groups_returned")
    if isinstance(groups_returned, int) and max_groups is not None and groups_returned >= max_groups and not release:
        reasons.append(
            f"groups_returned ({groups_returned}) is at the estimated cap ({max_groups}). "
            "The series is truncated. Not fine."
        )

    # Drop duplicate cap sentences if both the early and late checks fired.
    dedup: list[str] = []
    for reason in reasons:
        if reason not in dedup:
            dedup.append(reason)
    reasons = dedup

    health_fine = bool(
        api_read
        and scoped
        and not duration
        and not any("cap" in r or "truncated" in r or "stopped being recorded" in r or "not read" in r for r in reasons)
    )

    return {
        "ok": True,
        "wrote": False,
        "health_fine": bool(health_fine),
        "api_read": api_read,
        "cap": CAP,
        "duration_metric_stopped": DURATION_STOPPED,
        "stats_period": stats_period or None,
        "interval": interval,
        "estimated_buckets": buckets,
        "max_groups_under_cap": max_groups,
        "scoped_to_project_environment_release": scoped,
        "fields": fields,
        "group_by": group_by,
        "reasons": reasons,
        "note": ("Recommend only. This script does not record a deploy and does not call a Sentry write API."),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", required=True, help="Pasted query/response JSON path, or '-'.")
    parser.add_argument("--mark-fine", action="store_true", help="Exit 2 unless health_fine is true.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    client = client_from_env()
    if args.apply:
        try:
            client.refuse_write("record deploy / set release health")
        except SentryReadOnlyError as exc:
            print(json.dumps({"ok": False, "wrote": False, "health_fine": False, "error": str(exc)}))
            return 2
    raw = sys.stdin.read() if args.json == "-" else Path(args.json).read_text()
    try:
        # Reuse the shared parser. Sessions JSON is not project settings, but it
        # is still an object. fetch_project_settings(pasted=) validates JSON objects.
        data = client.fetch_project_settings("session-stats", pasted=raw)
    except SentryReadOnlyError as exc:
        print(json.dumps({"ok": False, "health_fine": False, "error": str(exc)}))
        return 2
    report = assess(data)
    print(json.dumps(report, indent=2))
    if args.mark_fine and not report["health_fine"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
