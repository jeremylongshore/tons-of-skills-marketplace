#!/usr/bin/env python3
"""Offline cost-plan inspection. Never executes a plan or authenticates an approval."""

import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import sys


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"{label}: explicit numeric value required")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{label}: invalid number") from exc
    if not result.is_finite() or result < 0 or result > Decimal("1e15"):
        raise ValueError(f"{label}: finite nonnegative bounded value required")
    return result


def required(obj, key):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip() or any(c in value for c in "\n\r\x00"):
        raise ValueError(f"{key}: explicit single-line value required")
    return value


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return result


def digest(plan):
    return hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def review(plan, approval=None, now=None):
    if not isinstance(plan, dict) or plan.get("schema") != "coreweave-cost-plan/v1":
        raise ValueError("expected coreweave-cost-plan/v1 object")
    now = now or datetime.now(timezone.utc)
    for key in ("owner", "organization", "context", "namespace", "currency", "rate_source"):
        required(plan, key)
    if len(plan["currency"]) != 3 or not plan["currency"].isascii() or not plan["currency"].isupper():
        raise ValueError("currency: three uppercase letters required")
    start, end = timestamp(required(plan, "valid_from")), timestamp(required(plan, "expires_at"))
    if not start <= now < end:
        raise ValueError("plan is stale or not yet valid")
    if plan.get("all_charge_categories_reviewed") is not True:
        raise ValueError("storage, transfer, capacity commitments and other charges require owner review")
    rows = plan.get("resources")
    if not isinstance(rows, list) or not rows or len(rows) > 1000:
        raise ValueError("resources: nonempty bounded inventory required")
    seen, output, total = set(), [], Decimal(0)
    for resource in rows:
        if not isinstance(resource, dict):
            raise ValueError("resource must be an object")
        identity = required(resource, "id")
        if identity in seen:
            raise ValueError("duplicate resource identity")
        seen.add(identity)
        for key in ("kind", "name", "action", "teardown_command", "retained_data", "artifact_sha256"):
            required(resource, key)
        if resource["action"] not in ("create", "update", "replace", "upload"):
            raise ValueError("unsupported action; destruction requires a separate review")
        artifact = resource["artifact_sha256"]
        if len(artifact) != 64 or any(c not in "0123456789abcdef" for c in artifact):
            raise ValueError("artifact_sha256: hash the exact reviewed artifact")
        count = number(resource.get("gpu_count"), "gpu_count")
        if count != int(count):
            raise ValueError("gpu_count must be an integer")
        gpu_type = required(resource, "gpu_type")
        if (count == 0) != (gpu_type == "none"):
            raise ValueError("gpu_type must be none exactly when gpu_count is zero")
        rate = number(resource.get("gpu_hourly_rate"), "gpu_hourly_rate")
        hours = number(resource.get("duration_hours"), "duration_hours")
        if hours == 0:
            raise ValueError("duration_hours must be positive")
        charges = resource.get("other_charges")
        if not isinstance(charges, list):
            raise ValueError("other_charges must be an explicit list (empty only after review)")
        subtotal = count * rate * hours
        for charge in charges:
            required(charge, "category")
            required(charge, "basis")
            subtotal += number(charge.get("amount"), "charge amount")
        total += subtotal
        output.append(
            {
                "id": identity,
                "gpu_type": gpu_type,
                "gpu_count": int(count),
                "gpu_hourly_rate": str(rate),
                "duration_hours": str(hours),
                "estimated_cost": str(subtotal),
                "action": resource["action"],
                "kind": resource["kind"],
                "name": resource["name"],
                "teardown_command": resource["teardown_command"],
                "retained_data": resource["retained_data"],
            }
        )
    budget = number(plan.get("budget_ceiling"), "budget_ceiling")
    if total > budget:
        raise ValueError("estimated cost exceeds owner budget ceiling")
    fingerprint = digest(plan)
    result = {
        "status": "needs_human_confirmation",
        "plan_sha256": fingerprint,
        "currency": plan["currency"],
        "estimated_total": str(total),
        "resources": output,
        "authority": "Offline review only; no execution or authenticated approval.",
        "target": {k: plan[k] for k in ("organization", "context", "namespace")},
    }
    if approval is not None:
        if not isinstance(approval, dict) or approval.get("plan_sha256") != fingerprint:
            raise ValueError("approval does not match the exact plan")
        if approval.get("decision") != "confirm" or required(approval, "approver") != plan["owner"]:
            raise ValueError("owner confirmation is missing")
        approved_at = timestamp(required(approval, "confirmed_at"))
        if not start <= approved_at <= now < end:
            raise ValueError("approval timestamp outside valid plan window")
        result["status"] = "supplied_confirmation_matches"
        result["authority"] = (
            "Receipt consistency only. Reconfirm in the trusted user/protected-environment channel; this JSON is not authorization."
        )
    return result


def pairs(values):
    result = {}
    for key, value in values:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def read(path):
    if path.stat().st_size > 2_000_000:
        raise ValueError("input exceeds 2 MB")
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--approval", type=Path)
    args = parser.parse_args()
    try:
        result = review(read(args.plan), read(args.approval) if args.approval else None)
    except (ValueError, TypeError, KeyError, OSError, AttributeError):
        # Do not echo raw input or exception strings that could contain credentials.
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "reason": "Invalid, incomplete, stale, over-budget or mismatched plan/confirmation. Review the documented contract.",
                }
            )
        )
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
