#!/usr/bin/env python3
"""Compare supplied GA4 report receipts; never collect data or mutate a property."""

import argparse
import datetime as dt
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation, localcontext
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

LIMIT = 2 * 1024 * 1024
CONTEXT = ("property_id", "start_date", "end_date", "time_zone", "filters", "reporting_identity", "currency")


class InvalidReceipt(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise InvalidReceipt(code)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-field")
        result[key] = value
    return result


def reject_constant(value):
    raise InvalidReceipt("nonstandard-json-number")


def number(value):
    require(isinstance(value, str) and len(value) <= 128, "metric-value-must-be-a-bounded-string")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise InvalidReceipt("invalid-numeric-metric") from exc
    require(result.is_finite() and abs(result.adjusted()) <= 100, "nonfinite-or-unbounded-metric")
    return result


def inspect(receipt, label):
    require(isinstance(receipt, dict), "receipt-must-be-an-object")
    context = receipt.get("context")
    require(isinstance(context, dict), "missing-context")
    require(all(key in context for key in CONTEXT), "missing-context-field")
    prop = context["property_id"]
    require(isinstance(prop, str) and prop.isascii() and prop.isdigit(), "invalid-property-id")
    for name in ("start_date", "end_date"):
        try:
            require(isinstance(context[name], str), "invalid-date")
            parsed = dt.date.fromisoformat(context[name])
            require(parsed.isoformat() == context[name], "date-must-be-absolute-iso")
        except (ValueError, TypeError) as exc:
            raise InvalidReceipt("invalid-date") from exc
    require(context["start_date"] <= context["end_date"], "reversed-date-window")
    try:
        require(isinstance(context["time_zone"], str), "invalid-time-zone")
        ZoneInfo(context["time_zone"])
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise InvalidReceipt("invalid-time-zone") from exc
    require(isinstance(context["filters"], (dict, type(None))), "invalid-filter-contract")
    for name in ("reporting_identity", "currency"):
        require(context[name] is None or isinstance(context[name], str), "invalid-context-value")
        require(context[name] is None or bool(context[name].strip()), "empty-context-value")
    pages = receipt.get("pages")
    require(isinstance(pages, list) and 0 < len(pages) <= 1000, "missing-or-excessive-pages")
    findings, rows = [], {}

    def finding(code, pointer, next_check):
        findings.append({"code": code, "evidence": pointer, "next_check": next_check})

    dimension_names = metric_names = metric_types = None
    expected_count = None
    offset = 0
    complete = True
    for index, page in enumerate(pages):
        pointer = f"/{label}/pages/{index}"
        require(isinstance(page, dict), "invalid-page")
        actual_offset = page.get("offset")
        require(type(actual_offset) is int and actual_offset >= 0, "invalid-page-offset")
        response = page.get("response")
        require(isinstance(response, dict), "missing-page-response")
        dh, mh = response.get("dimensionHeaders", []), response.get("metricHeaders")
        require(isinstance(dh, list) and isinstance(mh, list) and mh, "invalid-headers")
        require(
            all(isinstance(h, dict) and isinstance(h.get("name"), str) and h["name"] for h in dh + mh),
            "invalid-header-name",
        )
        dn, mn = [h["name"] for h in dh], [h["name"] for h in mh]
        mt = [h.get("type") for h in mh]
        require(all(isinstance(t, str) and t for t in mt), "missing-metric-type")
        require(len(set(dn)) == len(dn) and len(set(mn)) == len(mn), "duplicate-header")
        if dimension_names is None:
            dimension_names, metric_names, metric_types = dn, mn, mt
        require((dn, mn, mt) == (dimension_names, metric_names, metric_types), "headers-changed-between-pages")
        count = response.get("rowCount")
        require(type(count) is int and count >= 0, "missing-or-invalid-row-count")
        if expected_count is None:
            expected_count = count
        if count != expected_count:
            complete = False
            finding(
                "row-count-changed",
                pointer + "/response/rowCount",
                "Recollect a stable bounded report; rows may have changed during pagination.",
            )
        batch = response.get("rows", [])
        require(isinstance(batch, list), "invalid-rows")
        if actual_offset != offset or (not batch and count > offset):
            complete = False
            finding(
                "pagination-gap-or-stall",
                pointer + "/offset",
                "Collect every page from offset zero without gaps or repeated pages.",
            )
        for row_index, row in enumerate(batch):
            require(isinstance(row, dict), "invalid-row")
            dv, mv = row.get("dimensionValues", []), row.get("metricValues")
            require(isinstance(dv, list) and len(dv) == len(dn), "dimension-width-mismatch")
            require(isinstance(mv, list) and len(mv) == len(mn), "metric-width-mismatch")
            require(all(isinstance(v, dict) and isinstance(v.get("value"), str) for v in dv + mv), "invalid-row-value")
            key = tuple(v["value"] for v in dv)
            values = tuple(number(v["value"]) for v in mv)
            if key in rows:
                complete = False
                finding(
                    "duplicate-dimension-key",
                    pointer + f"/response/rows/{row_index}",
                    "Check pagination order, changing data and duplicate exports; do not sum user counts.",
                )
            else:
                rows[key] = values
        offset = actual_offset + len(batch)
        metadata = response.get("metadata")
        if metadata is None:
            finding(
                "quality-metadata-unavailable",
                pointer + "/response/metadata",
                "Capture the response metadata before asserting report quality.",
            )
            metadata = {}
        require(isinstance(metadata, dict), "invalid-metadata")
        for name, code, check in (
            (
                "dataLossFromOtherRow",
                "high-cardinality-aggregation-loss",
                "Inspect the (other) row and dimensional cardinality; this signal is not sampling.",
            ),
            (
                "subjectToThresholding",
                "thresholding-applies",
                "Check threshold-sensitive dimensions; the flag alone does not prove rows were withheld.",
            ),
        ):
            if name in metadata:
                require(type(metadata[name]) is bool, "quality-flag-must-be-boolean")
                if metadata[name]:
                    finding(code, pointer + "/response/metadata/" + name, check)
        sampling = metadata.get("samplingMetadatas", [])
        require(isinstance(sampling, list), "invalid-sampling-metadata")
        for sample_index, sample in enumerate(sampling):
            require(isinstance(sample, dict), "invalid-sampling-entry")
            read = number(sample.get("samplesReadCount"))
            space = number(sample.get("samplingSpaceSize"))
            require(
                read >= 0 and space > 0 and read <= space and read == int(read) and space == int(space),
                "invalid-sampling-counts",
            )
            if read < space:
                finding(
                    "sampled-report",
                    pointer + f"/response/metadata/samplingMetadatas/{sample_index}",
                    "Retain the sample fraction; use an appropriate smaller query or separately validated event-level analysis if exact counts are needed.",
                )
        if metadata.get("timeZone") is not None:
            require(metadata["timeZone"] == context["time_zone"], "context-time-zone-contradicts-response")
        if metadata.get("currencyCode") is not None and context["currency"] is not None:
            require(metadata["currencyCode"] == context["currency"], "context-currency-contradicts-response")
    if offset != expected_count or len(rows) != expected_count:
        complete = False
        finding(
            "incomplete-row-coverage",
            f"/{label}/pages",
            "Retain all pages and the total row count; a row limit is not a complete report.",
        )
    if not rows:
        finding(
            "empty-report",
            f"/{label}/pages",
            "Confirm the selected property, collection and reporting window; empty rows alone do not prove zero traffic.",
        )
    if context["filters"] is None:
        finding(
            "filter-contract-unavailable",
            f"/{label}/context/filters",
            "Record the complete filter contract; use an empty object only when filters are verified absent.",
        )
    if context["reporting_identity"] is None:
        finding(
            "reporting-identity-unavailable",
            f"/{label}/context/reporting_identity",
            "Record the UI/report identity setting; do not infer that raw and modeled users are comparable.",
        )
    if "TYPE_CURRENCY" in metric_types and context["currency"] is None:
        finding(
            "currency-unavailable",
            f"/{label}/context/currency",
            "Record the response/report currency before comparing monetary values.",
        )
    return {
        "context": context,
        "dimensions": dimension_names,
        "metrics": metric_names,
        "types": metric_types,
        "rows": rows,
        "complete": complete,
        "findings": findings,
    }


def analyze(payload):
    require(isinstance(payload, dict) and set(payload) == {"left", "right"}, "expected-two-report-receipts")
    reports = {name: inspect(payload[name], name) for name in ("left", "right")}
    left, right = reports["left"], reports["right"]
    mismatches = [key for key in CONTEXT if left["context"][key] != right["context"][key]]
    mismatches += [key for key in ("dimensions", "metrics", "types") if left[key] != right[key]]
    findings = [{"report": name, **f} for name, report in reports.items() for f in report["findings"]]
    comparable = not mismatches and all(
        r["complete"]
        and r["context"]["filters"] is not None
        and r["context"]["reporting_identity"] is not None
        and ("TYPE_CURRENCY" not in r["types"] or r["context"]["currency"] is not None)
        for r in reports.values()
    )
    deltas = []
    only_left = only_right = None
    if comparable:
        only_left, only_right = (
            len(left["rows"].keys() - right["rows"].keys()),
            len(right["rows"].keys() - left["rows"].keys()),
        )
        for key in sorted(left["rows"].keys() & right["rows"].keys()):
            for name, a, b in zip(left["metrics"], left["rows"][key], right["rows"][key]):
                if a != b:
                    # Bounded 128-character inputs and exponent range need more
                    # than Decimal's default 28 digits for exact subtraction.
                    with localcontext() as arithmetic:
                        arithmetic.prec = 512
                        difference = b - a
                        percent = str(difference / abs(a) * 100) if a else None
                    deltas.append(
                        {
                            "dimension_key_sha256": digest(key),
                            "metric": name,
                            "left": str(a),
                            "right": str(b),
                            "right_minus_left": str(difference),
                            "percent_change": percent,
                        }
                    )
    return {
        "schema_version": 1,
        "mode": "supplied-receipts",
        "input_sha256": digest(payload),
        "comparison": "context-mismatch"
        if mismatches
        else (
            "comparable-with-quality-caveats"
            if comparable and findings
            else "comparable"
            if comparable
            else "inconclusive"
        ),
        "context_mismatches": mismatches,
        "findings": findings,
        "metric_deltas": deltas,
        "dimension_rows_only_left": only_left,
        "dimension_rows_only_right": only_right,
        "limits": [
            "Caller-supplied context and responses are not independently authenticated.",
            "Matching numbers do not prove correctness; differences do not establish a cause.",
            "No cross-row sums are computed for users, rates or other potentially non-additive metrics.",
            "Quality flags describe report conditions; absence of a flag does not certify complete collection.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="JSON receipt pair, or - for stdin")
    args = parser.parse_args()
    try:
        if args.input == "-":
            raw = sys.stdin.buffer.read(LIMIT + 1)
        else:
            with open(args.input, "rb") as source:
                raw = source.read(LIMIT + 1)
        require(len(raw) <= LIMIT, "input-too-large")
        result = analyze(json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant))
    except (InvalidReceipt, json.JSONDecodeError, UnicodeError, OSError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, InvalidReceipt) else "unreadable-or-invalid-json"
        print(json.dumps({"status": "held", "code": code}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
