#!/usr/bin/env python3
"""Collect a bounded historical GA4 report using explicitly enabled existing ADC."""

import argparse
import datetime as dt
import importlib.metadata
import json
import sys
import time
from zoneinfo import ZoneInfo

from analyze import InvalidReceipt, digest, inspect, reject_constant, require, unique_object

LIMIT = 2 * 1024 * 1024
PAGE_SIZE = 1000
MAX_PAGES = 10
DEADLINE = 60


def prepare(plan):
    require(isinstance(plan, dict) and set(plan) == {"context", "request"}, "invalid-plan-fields")
    context, request = plan["context"], plan["request"]
    require(isinstance(context, dict) and isinstance(request, dict), "invalid-plan-objects")
    require(
        set(context) == {"property_id", "start_date", "end_date", "time_zone", "reporting_identity", "currency"},
        "invalid-context-fields",
    )
    prop = context["property_id"]
    require(isinstance(prop, str) and prop.isascii() and prop.isdigit(), "invalid-property-id")
    dates = []
    for name in ("start_date", "end_date"):
        require(isinstance(context[name], str), "invalid-date")
        value = dt.date.fromisoformat(context[name])
        require(value.isoformat() == context[name], "absolute-date-required")
        dates.append(value)
    require(0 <= (dates[1] - dates[0]).days < 366, "date-window-outside-bound")
    require(isinstance(context["time_zone"], str), "invalid-time-zone")
    ZoneInfo(context["time_zone"])
    for name in ("reporting_identity", "currency"):
        require(
            context[name] is None or (isinstance(context[name], str) and bool(context[name].strip())),
            "invalid-context-value",
        )
    allowed = {"dimensions", "metrics", "dimensionFilter", "metricFilter", "keepEmptyRows"}
    require(set(request) <= allowed, "unsupported-request-field")
    dimensions, metrics = request.get("dimensions", []), request.get("metrics")
    require(isinstance(dimensions, list) and len(dimensions) <= 9, "invalid-dimensions")
    require(isinstance(metrics, list) and 0 < len(metrics) <= 10, "invalid-metrics")
    for fields in (dimensions, metrics):
        names = set()
        for field in fields:
            require(isinstance(field, dict) and set(field) == {"name"}, "named-fields-only")
            name = field["name"]
            require(isinstance(name, str) and 0 < len(name) <= 256 and name not in names, "invalid-field-name")
            names.add(name)
    require(type(request.get("keepEmptyRows", False)) is bool, "invalid-keep-empty-rows")
    for name in ("dimensionFilter", "metricFilter"):
        require(name not in request or isinstance(request[name], dict), "invalid-filter")
    semantic = {"dimensions": dimensions, "metrics": metrics, "keepEmptyRows": request.get("keepEmptyRows", False)}
    for name in ("dimensionFilter", "metricFilter"):
        if request.get(name):
            semantic[name] = request[name]
    # Bind the comparison contract to effective report semantics, not a caller's
    # unrelated declaration that filters were absent.
    context = {**context, "filters": {"data_api_report": semantic}}
    wire = {
        **semantic,
        "property": "properties/" + prop,
        "dateRanges": [{"startDate": context["start_date"], "endDate": context["end_date"]}],
        "orderBys": [{"dimension": {"dimensionName": item["name"]}} for item in dimensions],
    }
    if context["currency"] is not None:
        wire["currencyCode"] = context["currency"]
    return context, wire


def collect(plan, fetch, *, monotonic=None):
    context, base = prepare(plan)
    monotonic = monotonic or time.monotonic
    deadline = monotonic() + DEADLINE
    pages, normalizations = [], []
    offset = 0
    state = "page-budget-exhausted"
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    for _ in range(MAX_PAGES):
        remaining = deadline - monotonic()
        if remaining <= 0:
            state = "deadline-exhausted"
            break
        request = {**base, "offset": str(offset), "limit": str(PAGE_SIZE)}
        response, changes = fetch(request, min(20, remaining))
        require(isinstance(response, dict), "unexpected-response")
        rows, count = response.get("rows", []), response.get("rowCount")
        require(isinstance(rows, list) and len(rows) <= PAGE_SIZE, "excessive-page-rows")
        require(type(count) is int and count >= 0, "invalid-row-count")
        pages.append({"offset": offset, "response": response})
        normalizations.append(changes)
        require(len(json.dumps(pages).encode()) <= LIMIT - 16384, "receipt-too-large")
        offset += len(rows)
        if offset >= count:
            state = "row-count-reached"
            break
        if not rows:
            state = "stalled-page"
            break
    require(bool(pages), "no-report-collected")
    receipt = {
        "context": context,
        "pages": pages,
        "collection": {
            "method": "properties.runReport",
            "state": state,
            "request_started_at": started,
            "response_received_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "request_sha256": digest(base),
            "maximum_pages": MAX_PAGES,
            "page_size": PAGE_SIZE,
            "collection_deadline_seconds": DEADLINE,
            "automatic_retries": False,
            "page_normalizations": normalizations,
        },
    }
    # Header/count drift and duplicate tuples cannot silently become comparable.
    inspect(receipt, "collected")
    require(len(json.dumps(receipt).encode()) <= LIMIT, "receipt-too-large")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Enable bounded read-only collection using existing ADC")
    args = parser.parse_args()
    client = None
    try:
        require(args.live, "live-read-not-enabled")
        raw = sys.stdin.buffer.read(LIMIT + 1)
        require(len(raw) <= LIMIT, "plan-too-large")
        plan = json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)
        _, wire = prepare(plan)
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import RunReportRequest, RunReportResponse

        # Parse nested filter contracts before credential discovery.
        RunReportRequest.from_json(json.dumps(wire))
        client = BetaAnalyticsDataClient(
            client_options={"scopes": ["https://www.googleapis.com/auth/analytics.readonly"]}
        )

        def fetch(request, timeout):
            result = client.run_report(
                request=RunReportRequest.from_json(json.dumps(request)), timeout=timeout, retry=None
            )
            require(isinstance(result, RunReportResponse), "unexpected-sdk-response")
            response = json.loads(
                RunReportResponse.to_json(
                    result, use_integers_for_enums=False, always_print_fields_with_no_presence=False
                )
            )
            changes = []
            if "rowCount" not in response:
                response["rowCount"] = result.row_count
                changes.append("protobuf-absent-rowCount-is-zero")
            return response, changes

        result = collect(plan, fetch)
        result["collection"]["sdk_version"] = importlib.metadata.version("google-analytics-data")
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except InvalidReceipt as exc:
        code = str(exc)
    except Exception:
        code = "collection-unavailable"
    finally:
        if client is not None:
            try:
                client.transport.close()
            except Exception:
                pass
    print(json.dumps({"status": "held", "code": code}))
    return 2


if __name__ == "__main__":
    sys.exit(main())
