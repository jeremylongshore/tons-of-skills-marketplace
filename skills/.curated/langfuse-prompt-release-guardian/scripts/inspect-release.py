#!/usr/bin/env python3
"""Review explicit prompt versions and a label snapshot without changing them."""

import argparse
import datetime as dt
import hashlib
import json
import re
import sys

LIMIT = 2 * 1024 * 1024


class InvalidReceipt(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise InvalidReceipt(code)


def identity(value):
    require(isinstance(value, str) and 0 < len(value) <= 256 and bool(value.strip()), "invalid-identity")
    return value


def names(value):
    require(isinstance(value, list) and len(value) <= 1000, "invalid-name-list")
    result = {identity(item) for item in value}
    require(len(result) == len(value), "duplicate-name")
    return result


def version(value):
    require(type(value) is int and 0 < value < 2**31, "invalid-version")
    return value


def timestamp(value):
    require(isinstance(value, str) and len(value) <= 64, "invalid-timestamp")
    try:
        result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, OverflowError) as exc:
        raise InvalidReceipt("invalid-timestamp") from exc
    require(result.tzinfo is not None, "timestamp-needs-timezone")
    return result


def digest(value):
    try:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    except (ValueError, TypeError, UnicodeError) as exc:
        raise InvalidReceipt("unhashable-or-nonfinite-prompt-data") from exc
    return hashlib.sha256(raw).hexdigest()


def fingerprint(prompt):
    # Labels/tags can move independently from immutable version content.
    return digest({key: prompt.get(key) for key in ("name", "version", "type", "prompt", "config", "resolutionGraph")})


def template_contract(prompt):
    variables, placeholders, unsupported = set(), set(), False
    if prompt["type"] == "text":
        require(
            isinstance(prompt.get("prompt"), str) and bool(prompt["prompt"].strip()), "invalid-or-empty-text-prompt"
        )
        texts = [prompt["prompt"]]
    else:
        messages = prompt.get("prompt")
        require(isinstance(messages, list) and 0 < len(messages) <= 1000, "invalid-chat-prompt")
        texts = []
        for message in messages:
            require(isinstance(message, dict), "invalid-chat-message")
            if message.get("type") == "placeholder":
                placeholders.add(identity(message.get("name")))
            else:
                require(message.get("type", "chatmessage") == "chatmessage", "unsupported-chat-message")
                identity(message.get("role"))
                require(isinstance(message.get("content"), str), "invalid-chat-content")
                texts.append(message["content"])
    for text in texts:
        require(len(text) <= LIMIT, "prompt-text-too-large")
        rest, position = [], 0
        # Advance monotonically: a regex retry at every unmatched opening brace
        # makes malformed input quadratic even within the receipt size limit.
        while True:
            start = text.find("{{", position)
            if start < 0:
                break
            end = text.find("}}", start + 2)
            if end < 0:
                unsupported = True
                break
            rest.append(text[position:start])
            token = re.fullmatch(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}", text[start : end + 2])
            if token:
                variables.add(token[1])
            else:
                unsupported = True
            position = end + 2
        rest.append(text[position:])
        remainder = "".join(rest)
        if "{{" in remainder or "}}" in remainder:
            unsupported = True
    return variables, placeholders, unsupported


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-field")
        result[key] = value
    return result


def reject_constant(_value):
    raise InvalidReceipt("nonstandard-json-number")


def analyze(payload, fingerprints_only=False):
    require(isinstance(payload, dict), "invalid-receipt")
    require(type(payload.get("schema_version")) is int and payload["schema_version"] == 1, "unsupported-schema")
    require(payload.get("receipt_kind") == "prompt-release-review", "wrong-receipt-kind")
    context, policy = payload.get("context"), payload.get("policy")
    require(isinstance(context, dict) and isinstance(policy, dict), "missing-context-or-policy")
    project, name, label = (identity(policy.get(key)) for key in ("project_id", "name", "label"))
    require(context.get("project_id") == project, "project-context-mismatch")
    identity(context.get("project_binding_review_ref"))
    reviewed = timestamp(context.get("reviewed_at"))
    maximum_age = context.get("maximum_age_seconds")
    require(type(maximum_age) is int and 0 < maximum_age <= 86400, "invalid-evidence-age-policy")
    current_version, candidate_version = (version(policy.get(key)) for key in ("current_version", "candidate_version"))
    require(current_version != candidate_version, "same-version-is-not-a-release-change")
    require(label != "latest", "automatic-latest-label-not-a-release-target")
    findings, prompts = [], {}
    for side in ("current", "candidate"):
        snapshot = payload.get(side)
        require(isinstance(snapshot, dict), "missing-prompt-snapshot")
        require(snapshot.get("name") == name, "snapshot-name-mismatch")
        request, response = snapshot.get("request"), snapshot.get("response")
        require(isinstance(request, dict) and isinstance(response, dict), "invalid-native-prompt-snapshot")
        expected_query = (
            {"label": label, "resolve": True} if side == "current" else {"version": candidate_version, "resolve": True}
        )
        require(request == expected_query, "snapshot-query-not-explicit-or-mismatched")
        require(request.get("resolve") is True, "dependency-resolution-not-requested")
        require(response.get("name") == name, "returned-prompt-name-mismatch")
        require(response.get("type") in ("text", "chat"), "unsupported-prompt-type")
        require(
            response.get("resolutionGraph") is None or isinstance(response["resolutionGraph"], dict),
            "invalid-resolution-graph",
        )
        actual_version = version(response.get("version"))
        labels = names(response.get("labels"))
        names(response.get("tags"))
        require("isFallback" not in response, "sdk-fallback-wrapper-not-native-api-response")
        age = (reviewed - timestamp(snapshot.get("captured_at"))).total_seconds()
        if age < 0 or age > maximum_age:
            findings.append(side + "-snapshot-stale-or-from-future")
        if actual_version != (current_version if side == "current" else candidate_version):
            findings.append(side + "-version-drift")
        if side == "current" and label not in labels:
            findings.append("current-label-not-observed")
        if side == "candidate" and label in labels:
            findings.append("target-label-already-on-candidate")
        template_contract(response)
        prompts[side] = response
    hashes = {side + "_sha256": fingerprint(prompt) for side, prompt in prompts.items()}
    if fingerprints_only:
        return {"status": "unreviewed-fingerprints", **hashes}
    identity(policy.get("review_ref"))
    for key, value in hashes.items():
        expected = policy.get(key)
        require(
            isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected), "missing-reviewed-prompt-fingerprint"
        )
        if expected != value:
            findings.append(key.replace("_sha256", "-reviewed-content-drift"))
    runtime_variables = names(policy.get("runtime_variables"))
    runtime_placeholders = names(policy.get("runtime_placeholders"))
    require(type(policy.get("allow_config_change")) is bool, "missing-config-change-policy")
    current, candidate = prompts["current"], prompts["candidate"]
    if current["type"] != candidate["type"]:
        findings.append("prompt-type-change-needs-runtime-migration")
    if digest(current.get("config")) != digest(candidate.get("config")) and not policy["allow_config_change"]:
        findings.append("config-change-not-approved")
    contracts = {side: template_contract(prompt) for side, prompt in prompts.items()}
    for side, (variables, placeholders, unsupported) in contracts.items():
        if unsupported:
            findings.append(side + "-template-needs-sdk-compile-review")
        if not variables <= runtime_variables:
            findings.append(side + "-runtime-variables-unavailable")
        if not placeholders <= runtime_placeholders:
            findings.append(side + "-runtime-placeholders-unavailable")
    return {
        "status": "reviewable-proposal" if not findings else "needs-investigation",
        "proposal": "promotion" if candidate_version > current_version else "rollback",
        "current_version": current_version,
        "candidate_version": candidate_version,
        "current_variable_count": len(contracts["current"][0]),
        "candidate_variable_count": len(contracts["candidate"][0]),
        "candidate_placeholder_count": len(contracts["candidate"][1]),
        **hashes,
        "findings": findings,
        "limits": [
            "Supplied snapshots, project bindings and review references are not independently authenticated.",
            "Simple string-variable and chat-placeholder names are checked; values and model behavior are not evaluated.",
            "Complex Mustache syntax requires an SDK compile review; this tool does not emulate its compiler.",
            "Label reads are not atomic, and runtime caches or fallbacks may serve a different version.",
            "No release, label mutation or command is executed; re-read label state and obtain release authority separately.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-")
    parser.add_argument(
        "--fingerprints", action="store_true", help="emit unreviewed fingerprints, not a release verdict"
    )
    args = parser.parse_args()
    try:
        if args.input == "-":
            raw = sys.stdin.buffer.read(LIMIT + 1)
        else:
            with open(args.input, "rb") as source:
                raw = source.read(LIMIT + 1)
        require(len(raw) <= LIMIT, "input-too-large")
        result = analyze(
            json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant), args.fingerprints
        )
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
    except (ValueError, OSError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, InvalidReceipt) else "unreadable-or-invalid-json"
        print(json.dumps({"status": "held", "code": code}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "reviewable-proposal" else 1


if __name__ == "__main__":
    raise SystemExit(main())
