#!/usr/bin/env python3
"""Audit supplied Langfuse Observations API v2 pages without querying a provider."""

import argparse
import datetime as dt
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation, localcontext

LIMIT = 2 * 1024 * 1024
FIELDS = {"core", "basic", "time", "io", "metadata", "model", "usage", "prompt", "metrics", "trace_context"}
QUERY_KEYS = {
    "fields",
    "limit",
    "cursor",
    "fromStartTime",
    "toStartTime",
    "type",
    "environment",
    "version",
    "name",
    "traceId",
    "level",
    "userId",
    "sessionId",
    "parentObservationId",
    "isRootObservation",
    "filter",
    "parseIoAsJson",
}


class InvalidReceipt(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise InvalidReceipt(code)


def identity(value):
    require(isinstance(value, str) and 0 < len(value) <= 256 and bool(value.strip()), "invalid-identity")
    return value


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(raw).hexdigest()


def timestamp(value):
    require(isinstance(value, str) and len(value) <= 64, "invalid-timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(parsed.tzinfo is not None, "timestamp-needs-timezone")
        return parsed.astimezone(dt.timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise InvalidReceipt("invalid-timestamp") from exc


def number(value):
    require(type(value) in (int, float, str, Decimal) and len(str(value)) <= 128, "invalid-usage-or-cost")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise InvalidReceipt("invalid-usage-or-cost") from exc
    require(result.is_finite() and result >= 0 and abs(result.adjusted()) <= 100, "unsupported-usage-or-cost")
    return result


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-field")
        result[key] = value
    return result


def reject_constant(_value):
    raise InvalidReceipt("nonstandard-json-number")


def analyze(payload):
    require(
        isinstance(payload, dict) and type(payload.get("schema_version")) is int and payload["schema_version"] == 1,
        "unsupported-receipt-schema",
    )
    require(payload.get("receipt_kind") == "observations-v2", "wrong-source-api")
    context = payload.get("context")
    require(isinstance(context, dict), "missing-context")
    project = identity(context.get("project_id"))
    start, end = (timestamp(context.get(key)) for key in ("from_start_time", "to_start_time"))
    require(start < end and end - start <= dt.timedelta(days=366), "invalid-or-excessive-window")
    collected_start, collected_end = (
        timestamp(context.get(key)) for key in ("collection_started_at", "collection_finished_at")
    )
    require(collected_start <= collected_end, "reversed-collection-window")
    require(
        context.get("collection_complete") is None or type(context["collection_complete"]) is bool,
        "invalid-collection-completeness",
    )
    pages = payload.get("pages")
    require(isinstance(pages, list) and 0 < len(pages) <= 100, "missing-or-excessive-pages")
    findings, finding_count = [], 0

    def finding(code, observation=None):
        nonlocal finding_count
        finding_count += 1
        if len(findings) < 100:
            row = {"code": code}
            if observation is not None:
                row["observation_key_sha256"] = digest(observation)
            findings.append(row)

    if context.get("collection_complete") is not True:
        finding("collection-not-declared-complete")
    if end > collected_end:
        finding("requested-window-extends-past-collection")
    seen, cursors, query = set(), set(), None
    expected_cursor = None
    eligible = known_cost = known_usage = zero_cost = total_rows = 0
    costs, models = [], {}
    chain_complete = True
    for index, page in enumerate(pages):
        require(isinstance(page, dict), "invalid-page")
        request, response = page.get("request"), page.get("response")
        require(isinstance(request, dict) and isinstance(response, dict), "missing-page-request-or-response")
        require(set(request) <= QUERY_KEYS, "unsupported-query-field")
        require("parseIoAsJson" not in request or request["parseIoAsJson"] is False, "unsupported-input-decoding")
        for field in (
            "type",
            "version",
            "name",
            "traceId",
            "level",
            "userId",
            "sessionId",
            "parentObservationId",
            "filter",
        ):
            if field in request:
                require(isinstance(request[field], str) and len(request[field]) <= LIMIT, "invalid-query-filter-type")
        if "isRootObservation" in request:
            require(type(request["isRootObservation"]) is bool, "invalid-root-observation-filter")
        if "environment" in request:
            environments = request["environment"]
            require(
                isinstance(environments, str)
                or isinstance(environments, list)
                and all(isinstance(value, str) for value in environments),
                "invalid-environment-filter",
            )
        page_query = {key: value for key, value in request.items() if key != "cursor"}
        if query is None:
            query = page_query
        elif page_query != query:
            finding("query-changed-between-pages")
            chain_complete = False
        if request.get("filter") not in (None, ""):
            finding("advanced-filter-overrides-simple-window-needs-review")
            chain_complete = False
        if request.get("fromStartTime") is None or request.get("toStartTime") is None:
            finding("request-window-not-established")
            chain_complete = False
        elif timestamp(request["fromStartTime"]) != start or timestamp(request["toStartTime"]) != end:
            finding("request-window-differs-from-context")
            chain_complete = False
        cursor = request.get("cursor")
        require(cursor is None or isinstance(cursor, str) and 0 < len(cursor) <= 4096, "invalid-request-cursor")
        if cursor != expected_cursor or index > 0 and expected_cursor is None:
            finding("cursor-chain-gap-or-restart")
            chain_complete = False
        limit = request.get("limit", 50)
        require(type(limit) is int and 0 < limit <= 1000, "invalid-page-limit")
        selected = request.get("fields", "core,basic")
        require(isinstance(selected, str), "invalid-field-groups")
        groups = [field.strip() for field in selected.split(",")]
        require(groups and len(groups) == len(set(groups)) and set(groups) <= FIELDS, "invalid-field-groups")
        usage_requested = "usage" in groups
        if not usage_requested:
            finding("usage-field-group-not-requested")
        data, meta = response.get("data"), response.get("meta")
        require(isinstance(data, list) and len(data) <= limit and isinstance(meta, dict), "invalid-page-response")
        # The native v2 API omits meta.cursor when there is no next page.
        expected_cursor = meta.get("cursor")
        require(
            "cursor" not in meta or isinstance(expected_cursor, str) and 0 < len(expected_cursor) <= 4096,
            "invalid-response-cursor",
        )
        if expected_cursor is not None:
            if expected_cursor in cursors or not data:
                finding("cursor-cycle-or-empty-nonterminal-page")
                chain_complete = False
            cursors.add(expected_cursor)
        total_rows += len(data)
        require(total_rows <= 10000, "too-many-observations")
        for observation in data:
            require(isinstance(observation, dict), "invalid-observation")
            require(observation.get("projectId") == project, "observation-project-mismatch")
            observation_id = identity(observation.get("id"))
            require("traceId" in observation, "missing-observation-trace-identity")
            trace_id = observation["traceId"]
            require(trace_id is None or isinstance(trace_id, str), "invalid-observation-trace-identity")
            if trace_id is not None:
                identity(trace_id)
            key = (trace_id, observation_id)
            require(key not in seen, "duplicate-observation-key")
            seen.add(key)
            observed_start = timestamp(observation.get("startTime"))
            require(start <= observed_start < end, "observation-outside-declared-window")
            kind = identity(observation.get("type"))
            if kind not in ("GENERATION", "EMBEDDING"):
                continue
            eligible += 1
            observed_end = observation.get("endTime")
            if observed_end is None:
                finding("observation-not-ended", key)
            else:
                require(timestamp(observed_end) >= observed_start, "observation-end-before-start")
                if timestamp(observed_end) > collected_end:
                    finding("observation-end-after-collection-clock", key)
            model = observation.get("model")
            require(model is None or isinstance(model, str), "invalid-model-name")
            model_key = digest(model)
            group = models.setdefault(model_key, {"rows": 0, "known_cost_rows": 0, "costs": []})
            group["rows"] += 1
            cost = observation.get("totalCost")
            if usage_requested and cost is not None:
                value = number(cost)
                costs.append(value)
                group["costs"].append(value)
                group["known_cost_rows"] += 1
                known_cost += 1
                zero_cost += value == 0
            else:
                finding("recorded-total-cost-unavailable", key)
            usage = observation.get("usageDetails")
            if usage_requested and isinstance(usage, dict) and usage:
                for amount in usage.values():
                    number(amount)
                known_usage += 1
            else:
                finding("usage-details-unavailable", key)
    if expected_cursor is not None:
        finding("next-page-not-retained")
        chain_complete = False
    if not eligible:
        finding("no-eligible-observations-not-proof-of-zero-spend")
    with localcontext() as decimal_context:
        decimal_context.prec = 512
        known_sum = str(sum(costs, Decimal(0))) if known_cost else None
        model_rows = [
            {
                "model_sha256": name,
                "retrieved_rows": group["rows"],
                "known_cost_rows": group["known_cost_rows"],
                "unavailable_cost_rows": group["rows"] - group["known_cost_rows"],
                "known_rows_recorded_cost_usd": str(sum(group["costs"], Decimal(0))) if group["costs"] else None,
            }
            for name, group in sorted(models.items())
        ]
    reviewable = finding_count == 0 and chain_complete
    return {
        "schema_version": 1,
        "mode": "supplied-observations-v2-pages",
        "status": "reviewable-retrieved-set" if reviewable else "needs-investigation",
        "query_sha256": digest(query),
        "pagination_chain_complete": chain_complete,
        "retrieved_rows": total_rows,
        "eligible_rows": eligible,
        "known_cost_rows": known_cost,
        "unavailable_cost_rows": eligible - known_cost,
        "explicit_zero_cost_rows": zero_cost,
        "known_usage_rows": known_usage,
        "known_rows_recorded_cost_usd": known_sum,
        "retrieved_set_recorded_cost_usd": known_sum if reviewable else None,
        "model_groups": model_rows[:50],
        "model_group_count": len(model_rows),
        "model_groups_truncated": len(model_rows) > 50,
        "finding_count": finding_count,
        "findings": findings,
        "findings_truncated": finding_count > len(findings),
        "limits": [
            "Supplied pages, project binding and collection declarations are not independently authenticated.",
            "Cursor exhaustion is not an atomic snapshot or proof that all application calls were traced.",
            "Recorded USD cost may be ingested or inferred; it is not a verified provider bill or savings estimate.",
            "Known-row subtotals exclude unavailable costs; no usage types or overlapping cost components are summed.",
            "Use Metrics API v2 for project aggregates; this tool audits the retained observation set only.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="JSON receipt, or - for stdin")
    args = parser.parse_args()
    try:
        if args.input == "-":
            raw = sys.stdin.buffer.read(LIMIT + 1)
        else:
            with open(args.input, "rb") as source:
                raw = source.read(LIMIT + 1)
        require(len(raw) <= LIMIT, "input-too-large")
        result = analyze(
            json.loads(raw, object_pairs_hook=unique_object, parse_float=Decimal, parse_constant=reject_constant)
        )
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
    except (ValueError, OSError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, InvalidReceipt) else "unreadable-or-invalid-json"
        print(json.dumps({"status": "held", "code": code}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "reviewable-retrieved-set" else 1


if __name__ == "__main__":
    raise SystemExit(main())
