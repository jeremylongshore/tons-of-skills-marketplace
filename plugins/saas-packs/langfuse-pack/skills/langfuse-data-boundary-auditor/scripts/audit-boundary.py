#!/usr/bin/env python3
"""Audit supplied observation JSON against an explicit field and retention policy."""

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


def timestamp(value):
    require(isinstance(value, str) and len(value) <= 64, "invalid-timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, OverflowError) as exc:
        raise InvalidReceipt("invalid-timestamp") from exc
    require(parsed.tzinfo is not None, "timestamp-needs-timezone")
    return parsed


def pointer(value):
    require(isinstance(value, str) and len(value) <= 4096 and value.startswith("/"), "invalid-field-pointer")
    require(not re.search(r"~(?![01])", value), "invalid-pointer-escape")
    result = tuple(part.replace("~1", "/").replace("~0", "~") for part in value[1:].split("/"))
    require(len(result) <= 64, "field-policy-too-deep")
    return result


def leaves(value, path=(), depth=0):
    require(depth <= 64, "payload-too-deep")
    if isinstance(value, dict) and value:
        for key, item in value.items():
            require(isinstance(key, str) and len(key) <= 256, "excessive-field-key")
            yield from leaves(item, path + ((key, False),), depth + 1)
    elif isinstance(value, list) and value:
        for index, item in enumerate(value):
            yield from leaves(item, path + ((str(index), True),), depth + 1)
    else:
        yield path


def matches(path, trie):
    states = [trie]
    for actual, array_index in path:
        following = []
        for state in states:
            if actual != "*" and actual in state:
                following.append(state[actual])
            if array_index and "*" in state:
                following.append(state["*"])
        if not following:
            return False
        states = following
    return any(None in state for state in states)


def path_hash(path):
    # Preserve object-vs-array identity without emitting names or raw values.
    raw = json.dumps(path, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


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
    require(payload.get("receipt_kind") == "observation-boundary-review", "wrong-receipt-kind")
    context, policy = payload.get("context"), payload.get("policy")
    require(isinstance(context, dict) and isinstance(policy, dict), "missing-context-or-policy")
    project = identity(policy.get("project_id"))
    require(context.get("project_id") == project, "project-context-mismatch")
    identity(policy.get("review_ref"))
    reviewed, captured = (timestamp(context.get(key)) for key in ("reviewed_at", "captured_at"))
    start, end = (timestamp(context.get(key)) for key in ("from_start_time", "to_start_time"))
    require(start < end <= captured <= reviewed, "invalid-capture-or-window")
    require(end - start <= dt.timedelta(days=90), "excessive-selection-window")
    maximum_age = policy.get("maximum_age_seconds")
    require(type(maximum_age) is int and 0 < maximum_age <= 86400, "invalid-age-policy")
    maximum_retention = policy.get("maximum_retention_days")
    require(type(maximum_retention) is int and maximum_retention >= 3, "invalid-retention-policy")
    allowed = policy.get("allowed_field_paths")
    require(isinstance(allowed, list) and 0 < len(allowed) <= 1000, "invalid-field-policy")
    allowed = [pointer(item) for item in allowed]
    require(len(set(allowed)) == len(allowed), "duplicate-field-policy")
    trie = {}
    for field_path in allowed:
        node = trie
        for part in field_path:
            node = node.setdefault(part, {})
        node[None] = True
    require(type(context.get("collection_complete")) is bool, "missing-collection-completeness")
    findings = Counter()
    if (reviewed - captured).total_seconds() > maximum_age:
        findings["stale-capture"] += 1
    if not context["collection_complete"]:
        findings["collection-declared-incomplete"] += 1

    projects = payload.get("project_lookup")
    require(isinstance(projects, dict) and isinstance(projects.get("data"), list), "invalid-native-project-lookup")
    require(len(projects["data"]) == 1 and isinstance(projects["data"][0], dict), "ambiguous-project-lookup")
    native_project = projects["data"][0]
    require(native_project.get("id") == project, "native-project-mismatch")
    retention = native_project.get("retentionDays")
    if retention is None or (type(retention) is int and retention == 0):
        findings["configured-retention-not-established"] += 1
        retention = None
    else:
        require(type(retention) is int and retention >= 3, "invalid-native-retention")
        if retention > maximum_retention:
            findings["configured-retention-exceeds-owner-policy"] += 1
    reviews = payload.get("coverage_reviews")
    require(isinstance(reviews, dict), "missing-coverage-reviews")
    for name in ("access_permissions", "dataset_items", "audit_logs", "external_copies", "retention_execution"):
        value = reviews.get(name)
        if value is None:
            findings[name + "-review-unavailable"] += 1
        else:
            identity(value)

    pages = payload.get("pages")
    require(isinstance(pages, list) and 0 < len(pages) <= 100, "missing-or-excessive-pages")
    cursor, used, previous_query = None, set(), None
    rows_seen, path_counts, leaf_count = set(), Counter(), 0
    for index, page in enumerate(pages):
        require(isinstance(page, dict), "invalid-page")
        query, response = page.get("request"), page.get("response")
        require(isinstance(query, dict) and isinstance(response, dict), "invalid-native-page")
        require(
            set(query) <= {"fields", "limit", "cursor", "fromStartTime", "toStartTime", "traceId"},
            "unsupported-query-scope",
        )
        require(
            timestamp(query.get("fromStartTime")) == start and timestamp(query.get("toStartTime")) == end,
            "query-window-mismatch",
        )
        if "traceId" in query:
            identity(query["traceId"])
        require(isinstance(query.get("fields"), str) and "core" in query["fields"].split(","), "core-fields-required")
        limit = query.get("limit", 50)
        require(type(limit) is int and 1 <= limit <= 1000, "invalid-page-limit")
        require(query.get("cursor") == cursor and (not index or cursor is not None), "broken-cursor-chain")
        stable = {key: value for key, value in query.items() if key != "cursor"}
        require(not index or stable == previous_query, "query-changed-during-collection")
        previous_query = stable
        rows, meta = response.get("data"), response.get("meta")
        require(isinstance(rows, list) and len(rows) <= limit and isinstance(meta, dict), "invalid-native-response")
        for row in rows:
            require(isinstance(row, dict) and row.get("projectId") == project, "observation-project-mismatch")
            key = (identity(row.get("traceId")), identity(row.get("id")))
            require(key not in rows_seen and len(rows_seen) < 10000, "duplicate-or-excessive-observations")
            rows_seen.add(key)
            if "traceId" in query:
                require(row["traceId"] == query["traceId"], "observation-trace-mismatch")
            require(start <= timestamp(row.get("startTime")) < end, "observation-outside-selection-window")
        # Audit all response fields, not only recognized native observation keys.
        for path in leaves(response):
            leaf_count += 1
            require(leaf_count <= 50000, "too-many-payload-leaves")
            if not matches(path, trie):
                findings["unapproved-payload-leaf"] += 1
                path_counts[path_hash(path)] += 1
        cursor = meta.get("cursor")
        if "cursor" in meta:
            identity(cursor)
            require(cursor not in used, "cursor-cycle")
            used.add(cursor)
    if cursor is not None:
        findings["cursor-not-exhausted"] += 1
    if not rows_seen:
        findings["empty-observation-selection"] += 1
    return {
        "status": "matches-supplied-policy" if not findings else "needs-investigation",
        "page_count": len(pages),
        "observation_count": len(rows_seen),
        "payload_leaf_count": leaf_count,
        "configured_retention_days": retention,
        "trace_restricted_selection": "traceId" in previous_query,
        "findings": dict(sorted(findings.items())),
        "unapproved_path_count": len(path_counts),
        "unapproved_paths": [
            {"path_sha256": key, "occurrences": value} for key, value in sorted(path_counts.items())[:100]
        ],
        "paths_truncated": len(path_counts) > 100,
        "limits": [
            "Only supplied observation response payloads are inventoried; source instrumentation and other stores are outside this scan.",
            "Field approval is an owner policy, not detection of PII, anonymization or permission to publish the original payload.",
            "Project lookup, timestamps and review references are supplied evidence, not independently authenticated controls.",
            "Cursor exhaustion covers this query only, not inaccessible history, an atomic snapshot or complete project export.",
            "Configured retention and review references do not prove deletion execution, storage encryption or legal/security compliance.",
            "No network, credential, masking, deletion, export or production mutation is performed.",
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
    return 0 if result["status"] == "matches-supplied-policy" else 1


if __name__ == "__main__":
    raise SystemExit(main())
