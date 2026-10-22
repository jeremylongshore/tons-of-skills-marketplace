# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, cast

from .catalog import explore as explore_catalog
from .catalog import find_endpoint, matches_path, normalize_method, normalize_path
from .client import action_enabled, check_api_available, dumps, normalize_query_params, request

ARGS_ERROR = "Invalid tool arguments. Pass a JSON object."
ACTION_REASON_ERROR = "Action reason missing. Add a user-visible reason."
ACTION_DISABLED_ERROR = (
    "Action disabled. Set HERMES_TWEET_ENABLE_ACTIONS=true to enable tweet_action."
)
PATH_QUERY_ERROR = "Query parameters misplaced. Pass them through the query object."
BLOCKED_ACTION_ERROR = (
    "Endpoint blocked. Complete account-connection challenges outside Hermes Tweet."
)
TOOL_FAILURE_ERROR = "Tool call failed. Review the request and retry."
BLOCKED_ACTION_ENDPOINTS: tuple[tuple[str, str], ...] = (
    ("POST", "/api/v1/x/account-connection-challenges/{id}/submit"),
)


def _args(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    return cast("dict[str, Any]", value)


def _args_error() -> str:
    return dumps({"success": False, "error": ARGS_ERROR})


def _text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def _path_error(path: str) -> str:
    if "?" not in path and "#" not in path:
        return ""
    return PATH_QUERY_ERROR


def _is_blocked_action(method: str, path: str) -> bool:
    return any(
        blocked_method == method and matches_path(blocked_path, path)
        for blocked_method, blocked_path in BLOCKED_ACTION_ENDPOINTS
    )


def _validate_action(tool_args: dict[str, Any]) -> tuple[str, str, str]:
    if not action_enabled():
        return "", "", ACTION_DISABLED_ERROR
    if not _text(tool_args.get("reason")):
        return "", "", ACTION_REASON_ERROR

    method = normalize_method(tool_args.get("method"), default="POST")
    path = _text(tool_args.get("path"))
    path_error = _path_error(path)
    if path_error:
        return "", "", path_error

    catalog_path = normalize_path(path)
    if _is_blocked_action(method, catalog_path):
        return "", "", BLOCKED_ACTION_ERROR
    if find_endpoint(method, catalog_path) is None:
        error = f"Endpoint unavailable. Choose a catalog-listed route: {method} {path}"
        return "", "", error
    return method, catalog_path, ""


def explore(args: Any, **_: Any) -> str:
    try:
        tool_args = _args(args)
        if tool_args is None:
            return _args_error()
        return dumps({"success": True, "endpoints": explore_catalog(tool_args)})
    except Exception:
        return dumps({"success": False, "error": TOOL_FAILURE_ERROR})


def call_read(args: Any, **_: Any) -> str:
    try:
        tool_args = _args(args)
        if tool_args is None:
            return _args_error()
        path = _text(tool_args.get("path"))
        path_error = _path_error(path)
        if path_error:
            return dumps({"success": False, "error": path_error})
        catalog_path = normalize_path(path)
        endpoint = find_endpoint("GET", catalog_path)
        if endpoint is None:
            return dumps(
                {
                    "success": False,
                    "error": f"Endpoint unavailable. Choose a catalog-listed route: GET {path}",
                }
            )
        if endpoint.action:
            return dumps(
                {
                    "success": False,
                    "error": "Read blocked. Use tweet_action for private or write-like endpoints.",
                }
            )
        return dumps(
            request("GET", catalog_path, query=normalize_query_params(tool_args.get("query")))
        )
    except Exception:
        return dumps({"success": False, "error": TOOL_FAILURE_ERROR})


def call_action(args: Any, **_: Any) -> str:
    try:
        tool_args = _args(args)
        if tool_args is None:
            return _args_error()
        method, catalog_path, error = _validate_action(tool_args)
        if error:
            return dumps({"success": False, "error": error})
        return dumps(
            request(
                method,
                catalog_path,
                query=normalize_query_params(tool_args.get("query")),
                body=tool_args.get("body"),
            )
        )
    except Exception:
        return dumps({"success": False, "error": TOOL_FAILURE_ERROR})


def xstatus(raw_args: Any = "") -> str:
    _ = raw_args
    return call_read({"path": "/api/v1/account"})


def xtrends(raw_args: Any = "") -> str:
    category = _text(raw_args)
    query = {"category": category} if category else None
    return call_read({"path": "/api/v1/x/trends", "query": query})


__all__ = [
    "action_enabled",
    "call_action",
    "call_read",
    "check_api_available",
    "explore",
    "xstatus",
    "xtrends",
]
