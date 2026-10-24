#!/usr/bin/env python3
"""Verify a supplied prompt webhook's original bytes; never release a prompt."""

import argparse
import datetime as dt
import hashlib
import hmac
import json
import os
import re
import sys
import time

LIMIT = 2 * 1024 * 1024


class InvalidReceipt(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise InvalidReceipt(code)


def identity(value):
    require(isinstance(value, str) and 0 < len(value) <= 256 and bool(value.strip()), "invalid-identity")
    return value


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-field")
        result[key] = value
    return result


def reject_constant(_value):
    raise InvalidReceipt("nonstandard-json-number")


def verify(raw, header, secret, project_id, now, seen):
    require(isinstance(raw, bytes) and 0 < len(raw) <= LIMIT, "invalid-body-size")
    require(isinstance(header, str) and len(header) <= 128, "invalid-signature-header")
    match = re.fullmatch(r"t=([0-9]{1,12}),v1=([0-9a-fA-F]{64})", header)
    require(match is not None, "invalid-signature-header")
    require(isinstance(secret, bytes) and 0 < len(secret) <= 4096, "missing-or-excessive-signing-secret")
    require(type(now) is int and 0 <= now < 10**12, "invalid-review-time")
    signed = int(match[1])
    # Five minutes is our receiver review policy, not a claimed Langfuse SLA.
    require(abs(now - signed) <= 300, "signature-outside-review-window")
    expected = hmac.new(secret, match[1].encode("ascii") + b"." + raw, hashlib.sha256).digest()
    require(hmac.compare_digest(expected, bytes.fromhex(match[2])), "signature-mismatch")
    # Parse only after authenticating the exact body bytes. No decoded/reencoded
    # JSON is substituted into the HMAC message.
    payload = json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)
    require(isinstance(payload, dict), "invalid-event")
    event_id = identity(payload.get("id"))
    require(payload.get("type") == "prompt-version" and payload.get("apiVersion") == "v1", "unsupported-event-contract")
    require(payload.get("action") in ("created", "updated", "deleted"), "unsupported-event-action")
    event_time = payload.get("timestamp")
    require(isinstance(event_time, str) and len(event_time) <= 64, "invalid-event-timestamp")
    try:
        parsed_time = dt.datetime.fromisoformat(event_time.replace("Z", "+00:00"))
    except (ValueError, OverflowError) as exc:
        raise InvalidReceipt("invalid-event-timestamp") from exc
    require(parsed_time.tzinfo is not None, "event-timestamp-needs-timezone")
    prompt = payload.get("prompt")
    require(isinstance(prompt, dict), "missing-prompt")
    identity(prompt.get("id"))
    name = identity(prompt.get("name"))
    project_id = identity(project_id)
    require(prompt.get("projectId") == project_id, "event-project-mismatch")
    version = prompt.get("version")
    require(type(version) is int and 0 < version < 2**31, "invalid-prompt-version")
    prompt_type = prompt.get("type")
    require(prompt_type in ("text", "chat"), "unsupported-prompt-type")
    require(
        isinstance(prompt.get("prompt"), str if prompt_type == "text" else list),
        "invalid-prompt-content-shape",
    )
    labels = prompt.get("labels")
    require(isinstance(labels, list) and len(labels) <= 256, "invalid-labels")
    for label in labels:
        identity(label)
    require(len(labels) == len(set(labels)), "duplicate-label")
    event_hash = digest(project_id + "\0" + event_id)
    replay = None
    if seen is not None:
        require(
            isinstance(seen, dict) and set(seen) == {"schema_version", "project_sha256", "processed_event_sha256"},
            "invalid-replay-receipt",
        )
        require(type(seen["schema_version"]) is int and seen["schema_version"] == 1, "invalid-replay-schema")
        require(seen["project_sha256"] == digest(project_id), "replay-project-mismatch")
        hashes = seen["processed_event_sha256"]
        require(isinstance(hashes, list) and len(hashes) <= 10000, "invalid-replay-history")
        require(
            all(isinstance(item, str) and re.fullmatch(r"[0-9a-f]{64}", item) for item in hashes),
            "invalid-replay-history",
        )
        require(len(hashes) == len(set(hashes)), "duplicate-replay-history")
        replay = event_hash in set(hashes)
    return {
        "status": "duplicate-supplied-event"
        if replay
        else "authenticated-supplied-event"
        if replay is False
        else "signature-valid-replay-unchecked",
        "project_sha256": digest(project_id),
        "prompt_name_sha256": digest(name),
        "event_sha256": event_hash,
        "body_sha256": hashlib.sha256(raw).hexdigest(),
        "version": version,
        "prompt_type": prompt_type,
        "action": payload["action"],
        "label_count": len(labels),
        "signed_at": signed,
        "reviewed_at": now,
        "replay_in_supplied_history": replay,
        "limits": [
            "Signature proves possession of the supplied secret, not independently authenticated project ownership.",
            "Replay history is supplied, bounded and not written or atomically claimed by this tool.",
            "Webhook order, label state and current deployed version require fresh read-only API evidence.",
            "This verifies an event envelope; it does not authorize deployment, label promotion or rollback.",
        ],
    }


def read_bounded(path, maximum):
    with open(path, "rb") as source:
        result = source.read(maximum + 1)
    require(len(result) <= maximum, "input-too-large")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("body")
    parser.add_argument("--header-file", required=True)
    parser.add_argument("--secret-env", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--seen-receipt")
    parser.add_argument("--now", type=int, default=None)
    args = parser.parse_args()
    try:
        require(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", args.secret_env), "invalid-secret-env-name")
        secret = os.environ.get(args.secret_env, "").encode("utf-8")
        header = read_bounded(args.header_file, 128).decode("ascii").rstrip("\r\n")
        raw = read_bounded(args.body, LIMIT)
        seen = None
        if args.seen_receipt:
            seen = json.loads(
                read_bounded(args.seen_receipt, LIMIT), object_pairs_hook=unique_object, parse_constant=reject_constant
            )
        result = verify(raw, header, secret, args.project_id, int(time.time()) if args.now is None else args.now, seen)
    except (ValueError, OSError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, InvalidReceipt) else "unreadable-or-invalid-input"
        print(json.dumps({"status": "held", "code": code}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "authenticated-supplied-event" else 1


if __name__ == "__main__":
    raise SystemExit(main())
