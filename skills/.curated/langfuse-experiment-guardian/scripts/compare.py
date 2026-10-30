#!/usr/bin/env python3
"""Check supplied experiment receipts against a caller-reviewed case policy."""

import argparse
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation, localcontext

LIMIT = 2 * 1024 * 1024


class InvalidReceipt(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise InvalidReceipt(code)


def identity(value):
    require(isinstance(value, str) and 0 < len(value) <= 256 and bool(value.strip()), "invalid-identity")
    return value


def fingerprint(value):
    return hashlib.sha256(value.encode()).hexdigest()


def content_hash(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value), "invalid-case-content-hash")
    return value


def number(value):
    require(type(value) in (int, float, str, Decimal), "invalid-score-type")
    require(len(str(value)) <= 128, "score-too-large")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise InvalidReceipt("invalid-score") from exc
    require(result.is_finite() and abs(result.adjusted()) <= 100, "nonfinite-or-unbounded-score")
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
    policy = payload.get("policy")
    require(isinstance(policy, dict), "missing-policy")
    for key in ("project_id", "dataset_id", "dataset_version", "baseline_run_id", "baseline_review_ref"):
        identity(policy.get(key))
    mode = policy.get("mode")
    require(mode in ("all-required", "preserve-baseline-passes"), "invalid-release-policy")
    expected = policy.get("expected_cases")
    require(isinstance(expected, list) and 0 < len(expected) <= 10000, "missing-or-excessive-required-cases")
    manifest = {}
    for case in expected:
        require(isinstance(case, dict), "invalid-required-case")
        key = identity(case.get("case_id"))
        require(key not in manifest, "duplicate-required-case")
        content_hash(case.get("content_sha256"))
        require(type(case.get("critical")) is bool, "missing-critical-case-classification")
        manifest[key] = case
    definitions = policy.get("evaluators")
    require(isinstance(definitions, list) and 0 < len(definitions) <= 32, "missing-or-excessive-evaluators")
    evaluators = {}
    for definition in definitions:
        require(isinstance(definition, dict), "invalid-evaluator-definition")
        name = identity(definition.get("name"))
        require(name not in evaluators, "duplicate-evaluator-definition")
        identity(definition.get("version"))
        low, high, threshold = (number(definition.get(k)) for k in ("minimum", "maximum", "threshold"))
        require(low < high and low <= threshold <= high, "invalid-score-range-or-threshold")
        require(definition.get("direction") in ("higher", "lower"), "invalid-score-direction")
        evaluators[name] = {**definition, "low": low, "high": high, "threshold": threshold}
    exceptions = policy.get("accepted_baseline_failures", [])
    require(isinstance(exceptions, list) and len(exceptions) <= 10000, "invalid-baseline-exceptions")
    accepted = set()
    for exception in exceptions:
        require(isinstance(exception, dict), "invalid-baseline-exception")
        pair = (identity(exception.get("case_id")), identity(exception.get("evaluator")))
        require(pair[0] in manifest and pair[1] in evaluators and pair not in accepted, "invalid-exception-target")
        identity(exception.get("review_ref"))
        accepted.add(pair)
    require(not accepted or mode == "preserve-baseline-passes", "exceptions-require-preserve-policy")

    findings, finding_count = [], 0

    def finding(code, run=None, case=None, evaluator=None):
        nonlocal finding_count
        finding_count += 1
        if len(findings) < 100:
            item = {"code": code}
            if run is not None:
                item["run"] = run
            if case is not None:
                item["case_id_sha256"] = fingerprint(case)
            if evaluator is not None:
                item["evaluator_sha256"] = fingerprint(evaluator)
            findings.append(item)

    results = {}
    run_ids = {}
    for label in ("baseline", "candidate"):
        receipt = payload.get(label)
        require(isinstance(receipt, dict), "missing-run-receipt")
        run_ids[label] = identity(receipt.get("run_id"))
        if label == "baseline" and run_ids[label] != policy["baseline_run_id"]:
            finding("baseline-does-not-match-reviewed-policy", label)
        for key in ("project_id", "dataset_id", "dataset_version"):
            if receipt.get(key) != policy[key]:
                finding("unknown-or-mismatched-" + key.replace("_", "-"), label)
        if receipt.get("export_complete") is not True:
            finding("export-completeness-not-established", label)
        if not isinstance(receipt.get("application_ref"), str) or not receipt["application_ref"].strip():
            finding("application-revision-unavailable", label)
        versions = receipt.get("evaluator_versions")
        require(isinstance(versions, dict), "missing-evaluator-versions")
        for name, definition in evaluators.items():
            if versions.get(name) != definition["version"]:
                finding("evaluator-version-not-comparable", label, evaluator=name)
        rows = receipt.get("cases")
        require(isinstance(rows, list) and len(rows) <= 10000, "invalid-case-results")
        seen, cells = set(), {}
        for row in rows:
            require(isinstance(row, dict), "invalid-case-result")
            key = identity(row.get("case_id"))
            require(key not in seen, "duplicate-result-case")
            seen.add(key)
            if key not in manifest:
                finding("unexpected-case", label, key)
                continue
            if row.get("content_sha256") != manifest[key]["content_sha256"]:
                finding("case-content-not-comparable", label, key)
            state = row.get("task_state")
            require(state in ("ok", "error", "unknown"), "invalid-task-state")
            if state != "ok":
                finding("task-execution-not-successful", label, key)
            scores = row.get("evaluations")
            require(isinstance(scores, list) and len(scores) <= 128, "invalid-evaluations")
            selected = {}
            for score in scores:
                require(isinstance(score, dict), "invalid-evaluation")
                name = identity(score.get("name"))
                if name not in evaluators:
                    continue
                require(name not in selected, "duplicate-selected-evaluation")
                selected[name] = score.get("value")
            for name, definition in evaluators.items():
                if selected.get(name) is None:
                    finding("required-evaluation-missing", label, key, name)
                    continue
                value = number(selected[name])
                require(definition["low"] <= value <= definition["high"], "score-outside-declared-range")
                cells[key, name] = (
                    value >= definition["threshold"]
                    if definition["direction"] == "higher"
                    else value <= definition["threshold"]
                )
        for missing in manifest.keys() - seen:
            finding("required-case-missing", label, missing)
        results[label] = cells
    if run_ids["baseline"] == run_ids["candidate"]:
        finding("baseline-and-candidate-are-the-same-run")

    comparable = finding_count == 0
    summaries = []
    failures = 0
    if comparable:
        for name in evaluators:
            baseline_passes = candidate_passes = regressions = 0
            for key, case in manifest.items():
                before, after = results["baseline"][key, name], results["candidate"][key, name]
                baseline_passes += before
                candidate_passes += after
                regressions += before and not after
                if mode == "preserve-baseline-passes" and not before and (key, name) not in accepted:
                    finding("baseline-failure-has-no-reviewed-exception", "baseline", key, name)
                if not after and (mode == "all-required" or before or case["critical"]):
                    failures += 1
                    finding("candidate-required-case-failed", "candidate", key, name)
            with localcontext() as context:
                context.prec = 32
                summaries.append(
                    {
                        "evaluator_sha256": fingerprint(name),
                        "required_cases": len(manifest),
                        "baseline_passes": baseline_passes,
                        "candidate_passes": candidate_passes,
                        "new_failures": regressions,
                        "candidate_pass_fraction": str(Decimal(candidate_passes) / len(manifest)),
                    }
                )
    unreviewed = any(f["code"] == "baseline-failure-has-no-reviewed-exception" for f in findings)
    # A truncated finding list must not hide an unreviewed baseline failure.
    if comparable and mode == "preserve-baseline-passes":
        unreviewed = any(not passed and cell not in accepted for cell, passed in results["baseline"].items())
    return {
        "schema_version": 1,
        "mode": "supplied-experiment-receipts",
        "decision": "inconclusive" if not comparable or unreviewed else "fail" if failures else "pass",
        "summaries": summaries if comparable else [],
        "finding_count": finding_count,
        "findings": findings,
        "findings_truncated": finding_count > len(findings),
        "limits": [
            "Supplied policy, identity, task state and export completeness are not independently authenticated.",
            "A pass satisfies the supplied case policy; it does not approve deployment or replace human review.",
            "No task, evaluator, provider call, score write or baseline update is executed.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="Receipt JSON, or - for stdin")
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
    return 0 if result["decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
