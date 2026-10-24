#!/usr/bin/env python3
"""Compare one supplied OTLP JSON batch with scoped Langfuse v2 readback pages."""

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from collections import Counter

LIMIT = 2 * 1024 * 1024


class InvalidReceipt(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise InvalidReceipt(code)


def identity(value):
    require(isinstance(value, str) and 0 < len(value) <= 256 and bool(value.strip()), "invalid-identity")
    return value


def hex_id(value, size):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{%d}" % size, value), "invalid-otel-id")
    require(int(value, 16) != 0, "zero-otel-id")
    return value.lower()


def unsigned(value, maximum):
    require(type(value) is int or isinstance(value, str), "invalid-unsigned-integer")
    require(re.fullmatch(r"[0-9]{1,20}", str(value)), "invalid-unsigned-integer")
    parsed = int(value)
    require(0 <= parsed <= maximum, "unsigned-integer-out-of-range")
    return parsed


def instant(value):
    require(isinstance(value, str) and len(value) <= 64, "invalid-timestamp")
    try:
        result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, OverflowError) as exc:
        raise InvalidReceipt("invalid-timestamp") from exc
    require(result.tzinfo is not None, "timestamp-needs-timezone")
    try:
        result = result.astimezone(dt.timezone.utc)
        delta = result - dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
        return (delta.days * 86400 + delta.seconds) * 1000000000 + delta.microseconds * 1000
    except (ValueError, OverflowError) as exc:
        raise InvalidReceipt("invalid-timestamp") from exc


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-field")
        result[key] = value
    return result


def reject_constant(_value):
    raise InvalidReceipt("nonstandard-json-number")


def analyze(payload):
    require(isinstance(payload, dict), "invalid-receipt")
    require(type(payload.get("schema_version")) is int and payload["schema_version"] == 1, "unsupported-schema")
    require(payload.get("receipt_kind") == "otlp-v2-readback", "wrong-receipt-kind")
    context = payload.get("context")
    require(isinstance(context, dict), "missing-context")
    project = identity(context.get("project_id"))
    exported, captured = (instant(context.get(key)) for key in ("export_finished_at", "readback_finished_at"))
    require(0 <= exported <= captured, "readback-before-export")
    require(type(context.get("capture_complete")) is bool, "missing-capture-completeness")
    findings = Counter()
    if not context["capture_complete"]:
        findings["incomplete-capture"] += 1

    request = payload.get("otlp_request")
    require(isinstance(request, dict), "missing-otlp-request")
    resources = request.get("resourceSpans", [])
    require(isinstance(resources, list) and len(resources) <= 1000, "invalid-resource-spans")
    expected = {}
    for resource in resources:
        require(isinstance(resource, dict), "invalid-resource")
        scopes = resource.get("scopeSpans", [])
        require(isinstance(scopes, list) and len(scopes) <= 1000, "invalid-scope-spans")
        for scope in scopes:
            require(isinstance(scope, dict), "invalid-scope")
            spans = scope.get("spans", [])
            require(isinstance(spans, list) and len(spans) <= 10000, "invalid-spans")
            for span in spans:
                require(isinstance(span, dict), "invalid-span")
                trace, span_id = hex_id(span.get("traceId"), 32), hex_id(span.get("spanId"), 16)
                key = (trace, span_id)
                require(key not in expected, "duplicate-exported-span")
                parent = span.get("parentSpanId", "")
                require(isinstance(parent, str), "invalid-parent-span-id")
                parent = hex_id(parent, 16) if parent else None
                start, end = (unsigned(span.get(k, 0), 2**64 - 1) for k in ("startTimeUnixNano", "endTimeUnixNano"))
                require(type(span.get("flags", 0)) is int and 0 <= span.get("flags", 0) < 2**32, "invalid-span-flags")
                if not start or not end or end < start:
                    findings["unended-or-invalid-span-time"] += 1
                elif end > exported:
                    findings["span-ended-after-export-receipt"] += 1
                if not isinstance(span.get("name"), str) or not span["name"].strip():
                    findings["missing-span-name"] += 1
                for field in ("droppedAttributesCount", "droppedEventsCount", "droppedLinksCount"):
                    if unsigned(span.get(field, 0), 2**32 - 1):
                        findings["exported-span-has-dropped-data"] += 1
                expected[key] = {"parent": parent, "start": start, "end": end}
                require(len(expected) <= 10000, "too-many-spans")
    if not expected:
        findings["empty-export-batch"] += 1
    traces = {key[0] for key in expected}
    require(len(traces) <= 100, "too-many-traces")
    # A parent outside this batch can be legitimate; it is an explicit boundary,
    # not proof that a provider dropped the parent.
    visited = set()
    for (trace, span_id), item in expected.items():
        parent = item["parent"]
        if parent and (trace, parent) not in expected:
            findings["parent-outside-export-batch"] += 1
        key, path = (trace, span_id), set()
        while key in expected and key not in visited:
            if key in path:
                findings["exported-parent-cycle"] += 1
                break
            path.add(key)
            key = (trace, expected[key]["parent"])
        visited.update(path)

    export = payload.get("export_http")
    if export is None:
        findings["export-response-unavailable"] += 1
    else:
        require(isinstance(export, dict) and type(export.get("status")) is int, "invalid-export-response")
        require(100 <= export["status"] <= 599, "invalid-http-status")
        response = export.get("response")
        require(isinstance(response, dict), "invalid-export-body")
        if export["status"] != 200:
            findings["export-http-not-successful"] += 1
        else:
            partial = response.get("partialSuccess")
            if partial is not None:
                require(isinstance(partial, dict), "invalid-partial-success")
                rejected = unsigned(partial.get("rejectedSpans", 0), 2**63 - 1)
                require(rejected <= len(expected), "rejected-count-exceeds-batch")
                message = partial.get("errorMessage", "")
                require(isinstance(message, str), "invalid-export-warning")
                findings["export-partial-rejection" if rejected else "export-warning-or-partial-envelope"] += 1

    readbacks = payload.get("readbacks")
    require(isinstance(readbacks, list) and len(readbacks) <= 100, "invalid-readbacks")
    observed, covered = {}, set()
    for readback in readbacks:
        require(isinstance(readback, dict), "invalid-readback")
        trace = hex_id(readback.get("trace_id"), 32)
        require(trace in traces and trace not in covered, "unexpected-or-duplicate-readback-trace")
        covered.add(trace)
        pages = readback.get("pages")
        require(isinstance(pages, list) and len(pages) <= 100, "invalid-pages")
        if not pages:
            findings["readback-pages-unavailable"] += 1
        cursor, used, previous_query = None, set(), None
        for index, page in enumerate(pages):
            require(isinstance(page, dict), "invalid-page")
            query, response = page.get("request"), page.get("response")
            require(isinstance(query, dict) and isinstance(response, dict), "invalid-native-page")
            require(
                set(query) <= {"traceId", "fields", "limit", "cursor", "parseIoAsJson", "fromStartTime", "toStartTime"},
                "filtered-readback-not-supported",
            )
            require(query.get("traceId") == trace, "readback-query-trace-mismatch")
            window_start, window_end = (instant(query.get(k)) for k in ("fromStartTime", "toStartTime"))
            require(0 <= window_start < window_end <= captured, "invalid-readback-window")
            require(window_end - window_start <= 90 * 86400 * 1000000000, "excessive-readback-window")
            require(
                all(window_start <= item["start"] < window_end for key, item in expected.items() if key[0] == trace),
                "expected-span-outside-readback-window",
            )
            fields = query.get("fields", "")
            require(isinstance(fields, str), "invalid-fields")
            require({"core", "basic", "time"} <= set(fields.split(",")), "missing-readback-fields")
            require(query.get("parseIoAsJson", False) is False, "parsed-io-not-supported")
            limit = query.get("limit", 50)
            require(type(limit) is int and 1 <= limit <= 1000, "invalid-page-limit")
            stable_query = {k: v for k, v in query.items() if k != "cursor"}
            if index:
                require(stable_query == previous_query, "readback-query-changed")
            previous_query = stable_query
            supplied = query.get("cursor")
            require(supplied == cursor and (not index or cursor is not None), "broken-cursor-chain")
            rows, meta = response.get("data"), response.get("meta")
            require(isinstance(rows, list) and len(rows) <= limit and isinstance(meta, dict), "invalid-native-response")
            for row in rows:
                require(isinstance(row, dict), "invalid-observation")
                require(
                    row.get("projectId") == project and row.get("traceId") == trace,
                    "readback-project-or-trace-mismatch",
                )
                key = (trace, hex_id(row.get("id"), 16))
                require(key not in observed, "duplicate-readback-observation")
                require(len(observed) < 10000, "too-many-readback-observations")
                parent = row.get("parentObservationId")
                parent = hex_id(parent, 16) if parent is not None else None
                start = instant(row.get("startTime"))
                require(window_start <= start < window_end, "returned-span-outside-readback-window")
                end = instant(row["endTime"]) if row.get("endTime") is not None else None
                observed[key] = {"parent": parent, "start": start, "end": end}
            cursor = meta.get("cursor")
            if "cursor" in meta:
                identity(cursor)
                require(cursor not in used, "cursor-cycle")
                used.add(cursor)
        if cursor is not None:
            findings["readback-cursor-not-exhausted"] += 1
    if covered != traces:
        findings["trace-readback-unavailable"] += len(traces - covered)

    matched = 0
    for key, item in expected.items():
        row = observed.get(key)
        if row is None:
            findings["expected-span-not-observed"] += 1
            continue
        matched += 1
        if row["parent"] != item["parent"]:
            findings["readback-parent-mismatch"] += 1
        # Reconcile at millisecond resolution; this is not nanosecond equality.
        if row["start"] // 1000000 != item["start"] // 1000000:
            findings["readback-start-mismatch"] += 1
        if row["end"] is None or row["end"] < row["start"]:
            findings["readback-span-not-ended"] += 1
        elif row["end"] // 1000000 != item["end"] // 1000000:
            findings["readback-end-mismatch"] += 1
    return {
        "status": "observed-supplied-batch" if not findings else "needs-investigation",
        "expected_spans": len(expected),
        "matched_span_ids": matched,
        "additional_readback_spans": len(set(observed) - set(expected)),
        "trace_count": len(traces),
        "findings": dict(sorted(findings.items())),
        "limits": [
            "Supplied export and readback receipts are not independently authenticated.",
            "This compares one captured batch; it cannot prove all application operations were instrumented.",
            "Not observed means absent from supplied pages, not proven provider data loss or a freshness SLA breach.",
            "A successful transport response or flush is not a per-span readback acknowledgement.",
            "No callbacks, retries, network calls, credentials, SDK changes or production mutations are performed.",
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
        result = analyze(json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant))
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
    except (ValueError, OSError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, InvalidReceipt) else "unreadable-or-invalid-json"
        print(json.dumps({"status": "held", "code": code}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "observed-supplied-batch" else 1


if __name__ == "__main__":
    raise SystemExit(main())
