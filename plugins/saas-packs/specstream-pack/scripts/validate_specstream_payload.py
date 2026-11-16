#!/usr/bin/env python3
"""Offline validator for SpecStream Search, Extract, Table, Schedule, and MCP payloads.

Runs completely offline using the Python standard library. Makes zero network calls
and requires no SPECSTREAM_API_KEY environment variable.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

VALID_SEARCH_SPEEDS = {"default", "fast"}
VALID_EXTRACT_FORMATS = {"markdown", "text", "html"}
VALID_EXTRACT_INCLUDES = {"full_text", "html", "links", "response"}
VALID_SCHEDULE_CADENCES = {"hourly", "daily", "weekly", "monthly", "yearly"}
VALID_DELIVERY_CHANNELS = {"slack", "email", "sheet", "crm", "webhook"}
SPECSTREAM_MCP_URL = "https://api.specstream.ai/mcp"
PUBLIC_HTTP_URL_RE = re.compile(r"^https?://[^\s/$.?#][^\s]*$")


def _is_public_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    candidate = value.strip()
    return bool(candidate and PUBLIC_HTTP_URL_RE.match(candidate))


def _check_idempotency_key(payload: dict[str, Any], errors: list[str]) -> None:
    key = payload.get("idempotency_key")
    if key is not None:
        if not isinstance(key, str) or not key.strip():
            errors.append("idempotency_key must be a non-empty string")
        elif len(key) > 128:
            errors.append("idempotency_key exceeds the 128-character limit")


def validate_search(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Validate a Search API (/v1/web-search) request payload."""
    errors: list[str] = []
    warnings: list[str] = []

    q = payload.get("q")
    if not isinstance(q, str) or not q.strip():
        errors.append("q must be a non-empty string (1 to 2,000 characters)")
    elif len(q) > 2000:
        errors.append("q exceeds the 2,000-character limit")

    speed = payload.get("speed")
    if speed is not None and speed not in VALID_SEARCH_SPEEDS:
        errors.append(f"speed must be one of {sorted(VALID_SEARCH_SPEEDS)}")

    images = payload.get("images")
    if images is not None and not isinstance(images, bool):
        errors.append("images must be a boolean")

    passages = payload.get("passages")
    if passages is not None and not isinstance(passages, bool):
        errors.append("passages must be a boolean")

    if images is True and passages is True:
        errors.append("passages cannot be combined with images=true")

    num = payload.get("num")
    if num is not None:
        max_num = 200 if images is True else 100
        if isinstance(num, bool) or not isinstance(num, int) or num < 1 or num > max_num:
            errors.append(f"num must be an integer between 1 and {max_num}")

    page = payload.get("page")
    if page is not None:
        if isinstance(page, bool) or not isinstance(page, int) or page < 1 or page > 10:
            errors.append("page must be an integer between 1 and 10")

    pages_wait_ms = payload.get("pages_wait_ms")
    if pages_wait_ms is not None:
        if (
            isinstance(pages_wait_ms, bool)
            or not isinstance(pages_wait_ms, int)
            or pages_wait_ms < 0
            or pages_wait_ms > 3500
        ):
            errors.append("pages_wait_ms must be an integer between 0 and 3500")
        elif passages is not True:
            warnings.append("pages_wait_ms only applies when passages=true")

    _check_idempotency_key(payload, errors)
    return errors, warnings


def validate_extract(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Validate an Extract API (/v1/extract) request payload."""
    errors: list[str] = []
    warnings: list[str] = []

    urls = payload.get("urls")
    pages = payload.get("pages")
    if urls is None and pages is None:
        errors.append("extract payload requires at least one entry in urls or pages")
        return errors, warnings

    total_items = 0
    if urls is not None:
        if not isinstance(urls, list):
            errors.append("urls must be a JSON array")
        else:
            total_items += len(urls)
            for idx, url in enumerate(urls):
                if not _is_public_http_url(url):
                    errors.append(f"urls[{idx}] must be an http or https URL")

    if pages is not None:
        if not isinstance(pages, list):
            errors.append("pages must be a JSON array")
        else:
            total_items += len(pages)
            for idx, page in enumerate(pages):
                if not isinstance(page, dict) or not isinstance(page.get("html"), str) or not page["html"].strip():
                    errors.append(f"pages[{idx}] must be an object with non-empty html string")
                elif "url" in page and page["url"] is not None and not _is_public_http_url(page["url"]):
                    errors.append(f"pages[{idx}].url must be an http or https URL when provided")

    if total_items < 1 or total_items > 20:
        errors.append("combined urls and pages count must be between 1 and 20")

    fmt = payload.get("format")
    if fmt is not None and fmt not in VALID_EXTRACT_FORMATS:
        errors.append(f"format must be one of {sorted(VALID_EXTRACT_FORMATS)}")

    include = payload.get("include")
    if include is not None:
        if not isinstance(include, list) or any(item not in VALID_EXTRACT_INCLUDES for item in include):
            errors.append(f"include items must be drawn from {sorted(VALID_EXTRACT_INCLUDES)}")

    _check_idempotency_key(payload, errors)
    return errors, warnings


def validate_table(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Validate a Deep Search table/list request or authorization payload."""
    errors: list[str] = []
    warnings: list[str] = []

    request_text = payload.get("request") or payload.get("q")
    if not isinstance(request_text, str) or not request_text.strip():
        errors.append("request (or q) must be a non-empty plain-language list specification")

    count = payload.get("count")
    if count is not None:
        if isinstance(count, bool) or not isinstance(count, int) or count < 1 or count > 500:
            errors.append("count for /v1/agent/lists must be an integer between 1 and 500")

    if "confirm_max_cents" in payload:
        confirm = payload["confirm_max_cents"]
        if isinstance(confirm, bool) or not isinstance(confirm, int) or confirm <= 0:
            errors.append("confirm_max_cents must be a positive integer")
        if not payload.get("quote_id") and not payload.get("task_id"):
            warnings.append("authorize_capacity_work requires quote_id/quote_hash or an A2A task_id")

    _check_idempotency_key(payload, errors)
    return errors, warnings


def validate_schedule(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Validate a SpecStream saved schedule / recurring monitor configuration."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(payload.get("name"), str) or not payload["name"].strip():
        errors.append("name must be a non-empty schedule name")

    cadence = payload.get("cadence")
    if cadence not in VALID_SCHEDULE_CADENCES:
        errors.append(f"cadence must be one of {sorted(VALID_SCHEDULE_CADENCES)}")

    cap = payload.get("spend_cap_cents")
    if isinstance(cap, bool) or not isinstance(cap, int) or cap <= 0:
        errors.append("spend_cap_cents must be a positive integer spend limit in cents")

    delivery = payload.get("delivery")
    if delivery is not None:
        if not isinstance(delivery, list) or not delivery:
            errors.append("delivery must be a non-empty list when provided")
        else:
            for idx, item in enumerate(delivery):
                if not isinstance(item, dict) or item.get("channel") not in VALID_DELIVERY_CHANNELS:
                    errors.append(
                        f"delivery[{idx}].channel must be one of {sorted(VALID_DELIVERY_CHANNELS)}"
                    )
                if item.get("channel") == "webhook":
                    target = item.get("url", "")
                    if not isinstance(target, str) or not target.startswith("https://"):
                        errors.append(f"delivery[{idx}].url for webhook must use https://")

    return errors, warnings


def validate_mcp(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Validate a SpecStream MCP client configuration object offline."""
    errors: list[str] = []
    warnings: list[str] = []

    servers = payload.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        errors.append("mcpServers must be a non-empty object")
        return errors, warnings

    specstream_entry = servers.get("specstream")
    if not isinstance(specstream_entry, dict):
        errors.append("mcpServers.specstream must be an object")
        return errors, warnings

    url = specstream_entry.get("url")
    if url != SPECSTREAM_MCP_URL:
        errors.append(f"mcpServers.specstream.url must equal {SPECSTREAM_MCP_URL}")

    transport = specstream_entry.get("type") or specstream_entry.get("transport")
    if transport is not None and transport not in {"http", "streamable-http", "streamableHttp"}:
        errors.append("mcpServers.specstream transport/type must be Streamable HTTP (http)")

    headers = specstream_entry.get("headers")
    if isinstance(headers, dict):
        auth = headers.get("Authorization") or headers.get("authorization")
        if isinstance(auth, str) and auth.strip() and "${" not in auth and "<" not in auth:
            errors.append(
                "Authorization header must reference an environment variable (e.g. ${SPECSTREAM_API_KEY}), not a literal token"
            )

    return errors, warnings


VALIDATORS = {
    "search": validate_search,
    "extract": validate_extract,
    "table": validate_table,
    "schedule": validate_schedule,
    "mcp": validate_mcp,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate SpecStream payloads offline without API keys or network calls."
    )
    parser.add_argument("--kind", required=True, choices=sorted(VALIDATORS))
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--file", type=Path, help="Path to JSON payload file")
    source_group.add_argument("--stdin", action="store_true", help="Read JSON payload from stdin")
    args = parser.parse_args(argv)

    try:
        raw = sys.stdin.read() if args.stdin else args.file.read_text(encoding="utf-8")
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "kind": args.kind, "errors": [str(exc)], "warnings": []}))
        return 1

    if not isinstance(payload, dict):
        print(
            json.dumps(
                {
                    "ok": False,
                    "kind": args.kind,
                    "errors": ["top-level JSON value must be an object"],
                    "warnings": [],
                }
            )
        )
        return 1

    errors, warnings = VALIDATORS[args.kind](payload)
    result = {
        "ok": len(errors) == 0,
        "kind": args.kind,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
