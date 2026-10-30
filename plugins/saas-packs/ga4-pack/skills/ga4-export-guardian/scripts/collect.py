#!/usr/bin/env python3
"""Collect bounded export metadata and optionally one dry-run-only query."""

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import re
import sys
import time
from zoneinfo import ZoneInfo

SPEC = importlib.util.spec_from_file_location("ga4_export_receipt", Path(__file__).with_name("inspect-export.py"))
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)
require = ENGINE.require
LIMIT = 2 * 1024 * 1024
MAX_TABLES = 1000
DEADLINE = 60


def prepare(plan):
    require(isinstance(plan, dict), "plan-must-be-object")
    required = {
        "project_id",
        "property_id",
        "dataset_id",
        "property_time_zone",
        "requested_window",
        "export_started_on",
        "daily_settlement_days",
    }
    require(required <= set(plan) <= required | {"sql", "maximum_bytes_billed"}, "invalid-plan-fields")
    require(
        isinstance(plan["project_id"], str) and re.fullmatch(r"[a-z][a-z0-9-]{4,61}[a-z0-9]", plan["project_id"]),
        "invalid-project-id",
    )
    prop = plan["property_id"]
    require(isinstance(prop, str) and prop.isascii() and prop.isdigit(), "invalid-property-id")
    require(plan["dataset_id"] == "analytics_" + prop, "dataset-property-mismatch")
    require(isinstance(plan["property_time_zone"], str), "invalid-time-zone")
    ZoneInfo(plan["property_time_zone"])
    window = plan["requested_window"]
    require(isinstance(window, dict) and set(window) == {"start_date", "end_date"}, "invalid-window")
    start, end = ENGINE.date(window["start_date"]), ENGINE.date(window["end_date"])
    require(0 <= (end - start).days < 366, "date-window-outside-bound")
    ENGINE.date(plan["export_started_on"])
    bound = plan["daily_settlement_days"]
    require(bound is None or (type(bound) is int and 0 <= bound <= 30), "invalid-settlement-bound")
    if "sql" in plan:
        require(isinstance(plan["sql"], str) and 0 < len(plan["sql"].encode()) <= 65536, "invalid-or-excessive-sql")
        cap = plan.get("maximum_bytes_billed")
        require(type(cap) is int and 0 < cap <= 2**63 - 1, "positive-byte-budget-required")
    else:
        require("maximum_bytes_billed" not in plan, "byte-budget-without-query")
    return start, end


def collect(plan, list_pages, get_table, dry_run=None, *, monotonic=None):
    start, end = prepare(plan)
    monotonic = monotonic or time.monotonic
    deadline = monotonic() + DEADLINE
    tables, failures = [], []
    count = 0
    complete = False
    pages = iter(list_pages())
    for _ in range(11):
        # The SDK iterator applies its fixed 20-second timeout to each page.
        # Do not start a page when that timeout would exceed this deadline.
        if deadline - monotonic() < 20:
            failures.append("listing-deadline-exhausted")
            break
        try:
            page = next(pages)
        except StopIteration:
            complete = True
            break
        except Exception:
            failures.append("listing-unavailable")
            break
        for item in page:
            count += 1
            if count > MAX_TABLES:
                failures.append("listing-table-budget-exhausted")
                break
            require(
                item.project == plan["project_id"] and item.dataset_id == plan["dataset_id"], "table-target-mismatch"
            )
            match = re.fullmatch(r"events_(?:intraday_)?(\d{8})", item.table_id)
            if not match:
                continue
            table_date = dt.datetime.strptime(match[1], "%Y%m%d").date()
            if not start <= table_date <= end:
                continue
            row = {"table_id": item.table_id}
            remaining = deadline - monotonic()
            if remaining <= 0:
                failures.append("metadata-deadline-exhausted")
            else:
                try:
                    table = get_table(item.reference, min(20, remaining))
                    require(table.reference == item.reference, "table-target-mismatch")
                    if table.num_rows is not None:
                        row["row_count"] = str(table.num_rows)
                    if table.modified is not None:
                        row["last_modified_at"] = table.modified.isoformat()
                except Exception:
                    failures.append("table-metadata-unavailable")
            tables.append(row)
        if count > MAX_TABLES:
            break
    else:
        failures.append("listing-page-budget-exhausted")
    receipt = {key: value for key, value in plan.items() if key not in {"project_id", "sql", "maximum_bytes_billed"}}
    receipt.update(
        {
            "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "snapshot_complete": complete and not failures,
            "tables": tables,
            "collection": {
                "project_id": plan["project_id"],
                "scope": "requested-date-window",
                "listed_entries": count,
                "maximum_listed_entries": MAX_TABLES,
                "deadline_seconds": DEADLINE,
                "automatic_retries": False,
                "gaps": sorted(set(failures)),
                "dry_run_state": "not-requested",
            },
        }
    )
    if "sql" in plan:
        remaining = deadline - monotonic()
        receipt["collection"]["dry_run_state"] = "held"
        if remaining > 0 and dry_run is not None:
            try:
                job = dry_run(plan["sql"], plan["maximum_bytes_billed"], min(20, remaining))
                candidate = {
                    **receipt,
                    "dry_run_job": job,
                    "expected_query_sha256": hashlib.sha256(plan["sql"].encode()).hexdigest(),
                }
                ENGINE.query_budget(candidate)
                receipt = candidate
                receipt["collection"]["dry_run_state"] = "collected-not-execution-approved"
            except Exception:
                receipt["collection"]["dry_run_state"] = "held"
    ENGINE.inspect(receipt)
    require(len(json.dumps(receipt).encode()) <= LIMIT, "receipt-too-large")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Enable approved metadata reads and any requested dry run")
    args = parser.parse_args()
    client = None
    try:
        require(args.live, "live-read-not-enabled")
        raw = sys.stdin.buffer.read(LIMIT + 1)
        require(len(raw) <= LIMIT, "plan-too-large")
        plan = json.loads(raw, object_pairs_hook=ENGINE.unique_object, parse_constant=ENGINE.reject_constant)
        prepare(plan)
        import google.auth
        from google.cloud import bigquery

        scope = "bigquery" if "sql" in plan else "bigquery.readonly"
        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/" + scope])
        client = bigquery.Client(project=plan["project_id"], credentials=credentials)
        dataset = plan["project_id"] + "." + plan["dataset_id"]

        def list_pages():
            return client.list_tables(dataset, max_results=1001, page_size=100, retry=None, timeout=20).pages

        def get_table(reference, timeout):
            return client.get_table(reference, retry=None, timeout=timeout)

        def dry_run(sql, cap, timeout):
            config = bigquery.QueryJobConfig(
                dry_run=True, use_legacy_sql=False, use_query_cache=False, maximum_bytes_billed=cap
            )
            job = client.query(sql, job_config=config, retry=None, job_retry=None, timeout=timeout)
            require(isinstance(job, bigquery.QueryJob), "unexpected-sdk-job")
            # to_api_repr() serializes request configuration, not server result
            # statistics. Preserve public result properties explicitly instead.
            require(type(job.total_bytes_processed) is int, "missing-dry-run-byte-estimate")
            result = job.to_api_repr()
            result["statistics"] = {
                "query": {
                    "statementType": job.statement_type,
                    "totalBytesProcessed": str(job.total_bytes_processed),
                }
            }
            result["status"] = {"state": job.state, "errorResult": job.error_result}
            return result

        result = collect(plan, list_pages, get_table, dry_run)
        if "dry_run_job" in result:
            result["collection"]["dry_run_normalization"] = "configuration-plus-public-sdk-statistics-and-status"
        result["collection"]["sdk_version"] = importlib.metadata.version("google-cloud-bigquery")
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except ENGINE.InvalidReceipt as exc:
        code = str(exc)
    except Exception:
        code = "collection-unavailable"
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass
    print(json.dumps({"status": "held", "code": code}))
    return 2


if __name__ == "__main__":
    sys.exit(main())
