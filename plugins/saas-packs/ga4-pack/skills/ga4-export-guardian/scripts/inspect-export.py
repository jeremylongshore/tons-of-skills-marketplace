#!/usr/bin/env python3
"""Inspect supplied GA4 export inventory and a query-bound BigQuery dry run."""

import argparse
import collections
import datetime as dt
import hashlib
import json
import re
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

LIMIT = 2 * 1024 * 1024


class InvalidReceipt(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise InvalidReceipt(code)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-field")
        result[key] = value
    return result


def reject_constant(_value):
    raise InvalidReceipt("nonstandard-json-number")


def date(value):
    require(isinstance(value, str), "missing-date")
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as error:
        raise InvalidReceipt("invalid-date") from error
    require(parsed.isoformat() == value, "date-must-be-absolute-iso")
    return parsed


def timestamp(value):
    require(isinstance(value, str), "missing-timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise InvalidReceipt("invalid-timestamp") from error
    require(parsed.tzinfo is not None, "timestamp-needs-timezone")
    return parsed


def integer_string(value):
    require(isinstance(value, str) and value.isascii() and value.isdigit() and len(value) <= 19, "invalid-int64-string")
    number = int(value)
    require(number <= 2**63 - 1, "int64-range-exceeded")
    return number


def query_budget(payload):
    job = payload.get("dry_run_job")
    if job is None:
        collection = payload.get("collection")
        if isinstance(collection, dict) and collection.get("dry_run_state") == "held":
            return {
                "state": "held-collection",
                "next_check": "Obtain a successful dry-run receipt; execution is not approved.",
            }
        return {"state": "not-supplied"}
    require(isinstance(job, dict), "invalid-dry-run-job")
    config, stats = job.get("configuration"), job.get("statistics")
    require(isinstance(config, dict) and config.get("dryRun") is True, "dry-run-required")
    query = config.get("query")
    require(isinstance(query, dict) and query.get("useLegacySql") is False, "standard-sql-required")
    require(not query.get("destinationTable"), "persistent-query-destination-not-supported")
    require(isinstance(stats, dict) and isinstance(stats.get("query"), dict), "missing-query-statistics")
    status = job.get("status", {})
    require(isinstance(status, dict), "invalid-job-status")
    require(status.get("errorResult") is None, "dry-run-failed")
    require("state" not in status or status["state"] == "DONE", "dry-run-not-complete")
    statistics = stats["query"]
    require(statistics.get("statementType") == "SELECT", "select-statement-required")
    sql = query.get("query")
    require(isinstance(sql, str) and sql.strip(), "missing-query-text")
    query_hash = hashlib.sha256(sql.encode()).hexdigest()
    require(payload.get("expected_query_sha256") == query_hash, "query-fingerprint-mismatch")
    estimated = integer_string(statistics.get("totalBytesProcessed"))
    accuracy = statistics.get("totalBytesProcessedAccuracy", "UNKNOWN")
    require(accuracy in ("UNKNOWN", "PRECISE", "LOWER_BOUND", "UPPER_BOUND"), "unknown-estimate-accuracy")
    budget = integer_string(query["maximumBytesBilled"]) if "maximumBytesBilled" in query else None
    require(budget is None or budget > 0, "positive-byte-budget-required")
    if budget is None:
        state = "inconclusive-no-byte-budget"
    elif estimated > budget:
        state = "estimate-exceeds-byte-budget"
    elif accuracy not in ("PRECISE", "UPPER_BOUND"):
        state = "inconclusive-estimate-bound"
    else:
        state = "billing-verification-required"
    return {
        "state": state,
        "query_sha256": query_hash,
        "estimated_bytes_processed": estimated,
        "estimate_accuracy": accuracy,
        "configured_maximum_bytes_billed": budget,
        "limits": [
            "Dry-run bytes are an estimate, not bytes billed or a monetary charge.",
            "Processed bytes below a cap do not establish billable bytes below it; minimum billing and rounding are not evaluated.",
            "Carry an approved maximumBytesBilled into any separately authorized execution.",
            "Query identity is caller-bound; dataset affinity and complete referenced-table coverage are not proven here.",
        ],
    }


def inspect(payload):
    require(isinstance(payload, dict), "receipt-must-be-object")
    prop = payload.get("property_id")
    require(isinstance(prop, str) and prop.isascii() and prop.isdigit(), "invalid-property-id")
    require(payload.get("dataset_id") == "analytics_" + prop, "dataset-property-mismatch")
    zone = payload.get("property_time_zone")
    try:
        require(isinstance(zone, str), "missing-property-time-zone")
        timezone = ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError) as error:
        raise InvalidReceipt("invalid-property-time-zone") from error
    captured = timestamp(payload.get("captured_at"))
    today = captured.astimezone(timezone).date()
    window = payload.get("requested_window")
    require(isinstance(window, dict), "missing-requested-window")
    start, end = date(window.get("start_date")), date(window.get("end_date"))
    require(0 <= (end - start).days < 366, "invalid-or-excessive-window")
    began = date(payload.get("export_started_on"))
    settlement = payload.get("daily_settlement_days")
    require(
        settlement is None or (type(settlement) is int and 0 <= settlement <= 30), "invalid-operator-settlement-bound"
    )
    complete = payload.get("snapshot_complete")
    require(type(complete) is bool, "snapshot-coverage-required")
    tables = payload.get("tables")
    require(isinstance(tables, list) and len(tables) <= 50000, "invalid-table-inventory")
    inventory, ignored = {}, 0
    for table in tables:
        require(isinstance(table, dict) and isinstance(table.get("table_id"), str), "invalid-table-row")
        name = table["table_id"]
        match = re.fullmatch(r"events_(intraday_)?(\d{8})", name)
        if not match:
            ignored += 1
            continue
        require(name not in inventory, "duplicate-table-id")
        try:
            dt.datetime.strptime(match[2], "%Y%m%d")
        except ValueError as error:
            raise InvalidReceipt("invalid-event-table-date") from error
        count = integer_string(table["row_count"]) if table.get("row_count") is not None else None
        modified = (
            timestamp(table["last_modified_at"]).isoformat() if table.get("last_modified_at") is not None else None
        )
        inventory[name] = {"row_count": count, "last_modified_at": modified}
    days = []
    for offset in range((end - start).days + 1):
        day = start + dt.timedelta(days=offset)
        suffix = day.strftime("%Y%m%d")
        daily, intraday = "events_" + suffix, "events_intraday_" + suffix
        has_daily, has_intraday = daily in inventory, intraday in inventory
        age = (today - day).days
        if day < began:
            state = (
                "table-observed-before-declared-start" if has_daily or has_intraday else "outside-declared-export-start"
            )
        elif age < 0:
            state = "future-table-observed" if has_daily or has_intraday else "future-to-snapshot"
        elif has_daily:
            state = "daily-table-observed"
        elif has_intraday:
            state = "intraday-only-provisional"
        elif not complete:
            state = "inconclusive-inventory-coverage"
        elif settlement is None:
            state = "not-observed-no-settlement-bound"
        elif age <= settlement:
            state = "not-observed-recent"
        else:
            state = "not-observed-after-operator-bound"
        days.append(
            {
                "date": day.isoformat(),
                "state": state,
                "daily_table": inventory.get(daily),
                "intraday_table": inventory.get(intraday),
                "preferred_single_source": daily if has_daily else intraday if has_intraday else None,
                "coexisting_sources_must_not_be_summed": has_daily and has_intraday,
            }
        )
    return {
        "schema_version": 1,
        "mode": "supplied-export-evidence",
        "input_sha256": hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "captured_at": captured.isoformat(),
        "property_time_zone": zone,
        "declared_operator_settlement_days": settlement,
        "day_states": dict(collections.Counter(row["state"] for row in days)),
        "days": days,
        "ignored_non_export_tables": ignored,
        "query_budget": query_budget(payload),
        "limits": [
            "Caller-supplied inventory, export start and snapshot coverage are not independently authenticated.",
            "Observed tables and row counts do not certify complete event delivery, identity or lifetime cohort acquisition.",
            "Settlement days are an operator assumption, not a Google SLA; late or reprocessed data can change older tables.",
            "Daily and intraday observations are never added together; preferred source is a selection policy, not a completeness certificate.",
            "No query, export configuration, IAM or dataset mutation is performed.",
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
        result = inspect(json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant))
    except (InvalidReceipt, ValueError, TypeError, OSError, UnicodeError, RecursionError, OverflowError) as error:
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
