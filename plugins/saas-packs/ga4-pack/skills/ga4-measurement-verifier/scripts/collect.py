#!/usr/bin/env python3
"""Collect one bounded realtime report using explicitly enabled existing ADC."""

import argparse
import datetime as dt
import importlib.metadata
import json
import sys

from verify import InvalidReceipt, object_without_duplicates, reject_constant, require, timestamp, verify

LIMIT = 2 * 1024 * 1024


def validate_plan(plan):
    require(isinstance(plan, dict), "plan-must-be-object")
    require(
        set(plan) <= {"property_id", "property_tier", "expected_events", "deployment_at", "clock_uncertainty_seconds"},
        "unknown-plan-field",
    )
    property_id = plan.get("property_id")
    require(isinstance(property_id, str) and property_id.isascii() and property_id.isdigit(), "invalid-property-id")
    require(plan.get("property_tier") in ("standard", "360"), "unknown-property-tier")
    if plan.get("deployment_at") is not None:
        timestamp(plan["deployment_at"])
    uncertainty = plan.get("clock_uncertainty_seconds")
    require(
        uncertainty is None or (type(uncertainty) is int and 0 <= uncertainty <= 86400), "invalid-clock-uncertainty"
    )
    expected = plan.get("expected_events")
    require(isinstance(expected, list) and 0 < len(expected) <= 100, "missing-or-excessive-expectations")
    names = set()
    for item in expected:
        require(isinstance(item, dict) and set(item) == {"name", "minimum_count"}, "invalid-event-expectation")
        name, minimum = item["name"], item["minimum_count"]
        require(isinstance(name, str) and 0 < len(name) <= 256 and name not in names, "invalid-or-duplicate-event-name")
        require(type(minimum) is int and 0 < minimum <= 1_000_000_000, "invalid-minimum-count")
        names.add(name)
    return {
        "property": "properties/" + property_id,
        "dimensions": [{"name": "eventName"}],
        "metrics": [{"name": "eventCount"}],
        "minuteRanges": [{"startMinutesAgo": 29, "endMinutesAgo": 0}],
        "limit": "10000",
    }


def collect(plan, fetch, *, clock=None):
    request = validate_plan(plan)
    clock = clock or (lambda: dt.datetime.now(dt.timezone.utc))
    started = clock().isoformat()
    response, normalizations = fetch(request)
    completed = clock().isoformat()
    receipt = {
        **plan,
        "request": request,
        "response": response,
        "request_started_at": started,
        "response_received_at": completed,
        "collection": {
            "method": "properties.runRealtimeReport",
            "normalizations": normalizations,
            "maximum_rows": 10000,
            "timeout_seconds": 20,
            "automatic_retries": False,
        },
    }
    # Reject unsupported wire shapes rather than printing a misleading receipt.
    verify(receipt)
    require(len(json.dumps(receipt).encode()) <= LIMIT, "response-too-large")
    return receipt


def sdk_fetch(request):
    # Import and credential discovery occur only after --live and plan validation.
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import RunRealtimeReportRequest, RunRealtimeReportResponse

    wire_request = RunRealtimeReportRequest.from_json(json.dumps(request))
    client = BetaAnalyticsDataClient(client_options={"scopes": ["https://www.googleapis.com/auth/analytics.readonly"]})
    try:
        result = client.run_realtime_report(request=wire_request, retry=None, timeout=20)
        require(isinstance(result, RunRealtimeReportResponse), "unexpected-sdk-response")
        response = json.loads(
            RunRealtimeReportResponse.to_json(
                result, use_integers_for_enums=False, always_print_fields_with_no_presence=False
            )
        )
        normalizations = []
        if "rowCount" not in response:
            response["rowCount"] = result.row_count
            normalizations.append("protobuf-absent-rowCount-is-zero")
        if not response.get("kind"):
            response["kind"] = "analyticsData#runRealtimeReport"
            normalizations.append("kind-derived-from-typed-runRealtimeReport-result")
        return response, normalizations
    finally:
        client.transport.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Enable one read-only request using existing ADC")
    args = parser.parse_args()
    try:
        require(args.live, "live-read-not-enabled")
        raw = sys.stdin.buffer.read(LIMIT + 1)
        require(len(raw) <= LIMIT, "plan-too-large")
        plan = json.loads(raw, object_pairs_hook=object_without_duplicates, parse_constant=reject_constant)
        validate_plan(plan)
        receipt = collect(plan, sdk_fetch)
        receipt["collection"]["sdk_version"] = importlib.metadata.version("google-analytics-data")
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except (InvalidReceipt, ValueError) as exc:
        code = str(exc) if isinstance(exc, InvalidReceipt) else "invalid-plan-json"
    except Exception:
        # Provider messages may contain identifiers or credential details.
        code = "collection-unavailable"
    print(json.dumps({"status": "held", "code": code}))
    return 2


if __name__ == "__main__":
    sys.exit(main())
