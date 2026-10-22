# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import os
from math import isfinite
from typing import Any, cast
from urllib.parse import urljoin

import httpx

API_V1_PREFIX = "/api/v1/"
DEFAULT_BASE_URL = "https://xquik.com"
TIMEOUT_SECONDS = 30.0


def _env_text(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip()
    return normalized or default


def _request_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def normalize_query_params(value: Any) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    output: dict[str, str] = {}
    for key, item in cast("dict[object, object]", value).items():
        if not isinstance(key, str):
            continue
        normalized_key = key.strip()
        if not normalized_key:
            continue
        if isinstance(item, bool):
            output[normalized_key] = str(item).lower()
        elif isinstance(item, (str, int)) or (isinstance(item, float) and isfinite(item)):
            output[normalized_key] = str(item)
    return output or None


def base_url() -> str:
    return _env_text("XQUIK_BASE_URL", DEFAULT_BASE_URL).rstrip("/") + "/"


def api_key() -> str:
    return _env_text("XQUIK_API_KEY")


def check_api_available() -> bool:
    return bool(api_key())


def action_enabled() -> bool:
    return check_api_available() and _env_text("HERMES_TWEET_ENABLE_ACTIONS").lower() == "true"


def build_headers(key: str, *, has_body: bool) -> dict[str, str]:
    headers: dict[str, str] = {}
    if key.startswith("xq_"):
        headers["x-api-key"] = key
    elif key:
        headers["authorization"] = f"Bearer {key}"
    if has_body:
        headers["content-type"] = "application/json"
    return headers


def _agent_readable_response(response: httpx.Response) -> bool:
    content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
    return (
        not content_type
        or content_type.startswith("text/")
        or content_type == "application/json"
        or content_type.endswith("+json")
    )


def _response_payload(response: httpx.Response) -> Any:
    if response.is_success and not _agent_readable_response(response):
        return {
            "success": False,
            "error": "Binary response unavailable. Use the Xquik REST API to download it.",
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type", ""),
        }
    try:
        payload = response.json()
    except ValueError:
        payload = {"text": response.text}
    if not response.is_success:
        return {
            "success": False,
            "error": "API request failed. Review the status and response.",
            "status_code": response.status_code,
            "response": payload,
        }
    return payload


def request(
    method: Any,
    path: Any,
    query: Any = None,
    body: Any | None = None,
) -> Any:
    normalized_method = _request_text(method).upper() or "GET"
    normalized_path = _request_text(path)
    params = normalize_query_params(query)
    if not normalized_path.startswith(API_V1_PREFIX):
        return {
            "success": False,
            "error": f"Invalid path. Start it with {API_V1_PREFIX}",
        }
    if "?" in normalized_path or "#" in normalized_path:
        return {
            "success": False,
            "error": "Query parameters misplaced. Pass them through the query object.",
        }

    key = api_key()
    if not key:
        return {
            "success": False,
            "error": "API key missing. Set XQUIK_API_KEY in the runtime environment.",
        }

    url = urljoin(base_url(), normalized_path.lstrip("/"))
    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.request(
                method=normalized_method,
                url=url,
                params=params,
                json=body,
                headers=build_headers(key, has_body=body is not None),
            )
        return _response_payload(response)
    except httpx.HTTPError:
        return {
            "success": False,
            "error": "Network request failed. Check the connection and retry.",
        }


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
