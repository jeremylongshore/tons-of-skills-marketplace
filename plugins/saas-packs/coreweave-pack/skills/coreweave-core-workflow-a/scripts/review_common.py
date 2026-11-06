"""Small offline evidence boundary shared by the standalone operator reviewers."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path


def instant(value):
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("timezone required")
    return value


def finite(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


class Report:
    def __init__(self):
        self.findings = []
        self.observations = {}

    def require(self, condition, code, message, unknown=False):
        if not condition:
            self.findings.append({"code": code, "severity": "unknown" if unknown else "blocker", "message": message})

    def result(self):
        status = (
            "blocked"
            if any(f["severity"] == "blocker" for f in self.findings)
            else ("incomplete" if self.findings else "reviewed")
        )
        return {
            "status": status,
            "findings": self.findings,
            "observations": self.observations,
            "evidence_boundary": "Supplied snapshot only; no account query, mutation, or authenticated approval.",
        }


def pairs(items):
    result = {}
    for k, v in items:
        if k in result:
            raise ValueError("duplicate JSON key")
        result[k] = v
    return result


def run(analyze):
    parser = argparse.ArgumentParser(description="Review local evidence only; never contacts a CoreWeave account.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", help="Explicit time for fixture replay; defaults to current UTC time")
    args = parser.parse_args()
    report = Report()
    try:
        if args.input.stat().st_size > 4_000_000:
            raise ValueError("input too large")
        raw = args.input.read_bytes()
        data = json.loads(raw, object_pairs_hook=pairs)
        if not isinstance(data, dict) or data.get("schema") != "coreweave-evidence/v1":
            raise ValueError("unsupported schema")
        now = instant(args.as_of) if args.as_of else datetime.now(timezone.utc)
        captured = instant(data["captured_at"])
        age = (now - captured).total_seconds()
        report.require(
            0 <= age <= 300, "evidence-age", "Snapshot must be within the preceding five minutes.", unknown=True
        )
        for key in ("context", "namespace"):
            expected = data.get("expected_" + key)
            report.require(
                isinstance(expected, str) and bool(expected) and data.get(key) == expected,
                "scope-" + key,
                "Explicit intended and observed scope must agree.",
            )
        analyze(data, report)
        result = report.result()
        result.update(input_sha256=hashlib.sha256(raw).hexdigest(), evaluated_at=now.isoformat())
    except (ValueError, TypeError, KeyError, AttributeError, IndexError, OSError):
        result = {
            "status": "blocked",
            "findings": [
                {
                    "code": "invalid-input",
                    "severity": "blocker",
                    "message": "Malformed or incomplete evidence contract. No input content echoed.",
                }
            ],
            "observations": {},
        }
    print(json.dumps(result, indent=2, allow_nan=False))
    return {"reviewed": 0, "blocked": 2, "incomplete": 3}[result["status"]]
