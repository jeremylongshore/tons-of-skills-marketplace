#!/usr/bin/env python3
"""Assess expected event-name/count signals in a supplied GA4 realtime receipt."""

import argparse
import datetime as dt
import hashlib
import json
import sys

LIMIT = 2 * 1024 * 1024


class InvalidReceipt(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise InvalidReceipt(code)


def object_without_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-field")
        result[key] = value
    return result


def reject_constant(_value):
    raise InvalidReceipt("nonstandard-json-number")


def timestamp(value):
    require(isinstance(value, str), "missing-timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidReceipt("invalid-timestamp") from exc
    require(parsed.tzinfo is not None, "timestamp-needs-timezone")
    return parsed.astimezone(dt.timezone.utc)


def counter(value):
    require(isinstance(value, str) and value.isascii() and value.isdigit() and len(value) <= 20, "invalid-event-count")
    return int(value)


def verify(payload):
    require(isinstance(payload, dict), "receipt-must-be-object")
    property_id = payload.get("property_id")
    require(isinstance(property_id, str) and property_id.isascii() and property_id.isdigit(), "invalid-property-id")
    tier = payload.get("property_tier")
    require(tier in ("standard", "360"), "unknown-property-tier")
    started = timestamp(payload.get("request_started_at"))
    completed = timestamp(payload.get("response_received_at"))
    require(completed >= started, "response-precedes-request")
    deployment = timestamp(payload["deployment_at"]) if payload.get("deployment_at") is not None else None
    uncertainty = payload.get("clock_uncertainty_seconds")
    require(
        uncertainty is None or (type(uncertainty) is int and 0 <= uncertainty <= 86400), "invalid-clock-uncertainty"
    )
    expected = payload.get("expected_events")
    require(isinstance(expected, list) and 0 < len(expected) <= 100, "missing-or-excessive-expectations")
    minimums = {}
    for item in expected:
        require(isinstance(item, dict) and set(item) == {"name", "minimum_count"}, "invalid-event-expectation")
        name, minimum = item["name"], item["minimum_count"]
        require(
            isinstance(name, str) and 0 < len(name) <= 256 and name not in minimums, "invalid-or-duplicate-event-name"
        )
        require(type(minimum) is int and 0 < minimum <= 1_000_000_000, "invalid-minimum-count")
        minimums[name] = minimum
    request, response = payload.get("request"), payload.get("response")
    require(isinstance(request, dict) and isinstance(response, dict), "missing-request-or-response")
    require(request.get("property") == "properties/" + property_id, "property-binding-mismatch")
    require(request.get("dimensions") == [{"name": "eventName"}], "event-name-only-dimension-required")
    require(request.get("metrics") == [{"name": "eventCount"}], "event-count-only-metric-required")
    require(
        not any(request.get(key) for key in ("dimensionFilter", "metricFilter", "metricAggregations")),
        "filtered-or-aggregate-report-not-supported",
    )
    ranges = request.get("minuteRanges", [{"startMinutesAgo": 29, "endMinutesAgo": 0}])
    require(isinstance(ranges, list) and len(ranges) == 1 and isinstance(ranges[0], dict), "one-minute-range-required")
    start, end = ranges[0].get("startMinutesAgo", 29), ranges[0].get("endMinutesAgo", 0)
    maximum = 29 if tier == "standard" else 59
    require(type(start) is int and type(end) is int and 0 <= end <= start <= maximum, "invalid-minute-range")
    # Include possible server-minute boundaries using the caller's clock bound.
    # Without that evidence, these dates describe only the client clock frame.
    margin = dt.timedelta(seconds=uncertainty or 0)
    earliest = (started - margin).replace(second=0, microsecond=0) - dt.timedelta(minutes=start)
    latest = (completed + margin).replace(second=0, microsecond=0) - dt.timedelta(minutes=end) + dt.timedelta(minutes=1)
    require(response.get("kind") == "analyticsData#runRealtimeReport", "not-realtime-response")
    require(response.get("dimensionHeaders") == [{"name": "eventName"}], "unexpected-dimension-headers")
    require(
        response.get("metricHeaders") == [{"name": "eventCount", "type": "TYPE_INTEGER"}], "unexpected-metric-headers"
    )
    rows, row_count = response.get("rows", []), response.get("rowCount")
    require(isinstance(rows, list) and type(row_count) is int and row_count >= len(rows), "invalid-row-coverage")
    counts = {}
    for row in rows:
        require(isinstance(row, dict), "invalid-row")
        dimensions, metrics = row.get("dimensionValues"), row.get("metricValues")
        require(
            isinstance(dimensions, list) and len(dimensions) == 1 and isinstance(dimensions[0], dict),
            "invalid-event-dimension",
        )
        require(
            isinstance(metrics, list) and len(metrics) == 1 and isinstance(metrics[0], dict), "invalid-event-metric"
        )
        name = dimensions[0].get("value")
        require(isinstance(name, str) and 0 < len(name) <= 256 and name not in counts, "duplicate-or-invalid-event-row")
        counts[name] = counter(metrics[0].get("value"))
    complete = row_count == len(rows)
    events = []
    for name, minimum in minimums.items():
        count = counts.get(name)
        # Truncation cannot erase a row already supplied, but does prevent
        # interpreting an absent event as an observed zero.
        status = (
            "observed"
            if count is not None and count >= minimum
            else "below-expectation"
            if count is not None
            else "not-observed-in-receipt"
            if complete
            else "inconclusive"
        )
        events.append({"name": name, "minimum_count": minimum, "observed_count": count, "status": status})
    after_deployment = deployment is not None and uncertainty is not None and earliest >= deployment
    return {
        "schema_version": 1,
        "mode": "supplied-realtime-receipt",
        "input_sha256": hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "request_started_at": started.isoformat(),
        "response_received_at": completed.isoformat(),
        "event_window": {
            "start_inclusive": earliest.isoformat(),
            "end_exclusive": latest.isoformat(),
            "clock_basis": "caller-bounded" if uncertainty is not None else "client-only-unbounded",
        },
        "clock_uncertainty_seconds": uncertainty,
        "row_coverage_complete": complete,
        "deployment_window": "not-supplied"
        if deployment is None
        else "inconclusive-clock-bound"
        if uncertainty is None
        else "entirely-after-deployment"
        if after_deployment
        else "not-isolated-after-deployment",
        "events": events,
        "next_checks": [
            *(
                ["Recapture a complete event-name report; absent rows in this truncated receipt are inconclusive."]
                if not complete
                else []
            ),
            *(
                ["Select a window entirely after deployment before attributing any event to that deployment."]
                if deployment is not None and not after_deployment
                else []
            ),
            "For an absent or low-count event, inspect collection, consent, filters and processing evidence; do not declare an outage from this receipt alone.",
        ],
        "limits": [
            "Caller-supplied receipt, timestamps and clock uncertainty are not authenticated by this analyzer.",
            "Observed names/counts do not validate event parameters, revenue, user journeys or end-to-end tag correctness.",
            "No report result certifies a successful deployment or guarantees realtime processing latency.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-")
    args = parser.parse_args()
    try:
        if args.input == "-":
            raw = sys.stdin.buffer.read(LIMIT + 1)
        else:
            with open(args.input, "rb") as source:
                raw = source.read(LIMIT + 1)
        require(len(raw) <= LIMIT, "input-too-large")
        result = verify(json.loads(raw, object_pairs_hook=object_without_duplicates, parse_constant=reject_constant))
    except (InvalidReceipt, ValueError, OSError, UnicodeError, RecursionError, OverflowError) as error:
        print(
            json.dumps(
                {
                    "status": "held",
                    "code": str(error) if isinstance(error, InvalidReceipt) else "unreadable-or-invalid-json",
                }
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
