# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

_METHOD_ENUM = ["GET", "POST", "PATCH", "PUT", "DELETE"]
_API_PATH_PATTERN = r"^(?:/api/v1/|https?://[^/]+/api/v1/)"
_API_PATH_DESCRIPTION = "Use a /api/v1/... path or copied API URL with that path prefix."

TWEET_EXPLORE = {
    "name": "tweet_explore",
    "description": (
        "Search the bundled Xquik endpoint catalog before other calls. "
        "This tool makes no network request."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "minLength": 1,
                "pattern": "\\S",
                "description": (
                    "Search endpoint paths, summaries, parameters, and response shapes."
                ),
            },
            "category": {
                "type": "string",
                "minLength": 1,
                "pattern": "\\S",
                "description": "Endpoint category filter.",
            },
            "method": {
                "type": "string",
                "enum": _METHOD_ENUM,
                "description": "HTTP method filter.",
            },
            "path": {
                "type": "string",
                "minLength": 1,
                "pattern": "\\S",
                "description": "Exact or partial /api/v1 path filter.",
            },
            "free": {"type": "boolean", "description": "Filter free or paid endpoints."},
            "mpp": {"type": "boolean", "description": "Filter endpoints by MPP eligibility."},
            "include_actions": {
                "type": "boolean",
                "description": "Include write-like and private endpoints in catalog results.",
                "default": False,
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 25,
                "description": "Maximum endpoint descriptors to return.",
            },
        },
        "additionalProperties": False,
    },
}

TWEET_READ = {
    "name": "tweet_read",
    "description": (
        "Call one catalog-listed read-only Xquik endpoint from tweet_explore. "
        "Private and write-like endpoints are rejected."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "minLength": 8,
                "pattern": _API_PATH_PATTERN,
                "description": _API_PATH_DESCRIPTION,
            },
            "query": {
                "type": "object",
                "description": "Query parameters as string, number, or boolean values.",
                "propertyNames": {"minLength": 1, "pattern": "\\S"},
                "additionalProperties": {"type": ["string", "number", "boolean"]},
            },
        },
        "required": ["path"],
        "additionalProperties": False,
    },
}

TWEET_ACTION = {
    "name": "tweet_action",
    "description": (
        "Call one catalog-listed Xquik write or private-read endpoint. "
        "Set HERMES_TWEET_ENABLE_ACTIONS=true and show the user the request first."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "minLength": 8,
                "pattern": _API_PATH_PATTERN,
                "description": _API_PATH_DESCRIPTION,
            },
            "method": {"type": "string", "enum": _METHOD_ENUM, "default": "POST"},
            "query": {
                "type": "object",
                "description": "Query parameters as string, number, or boolean values.",
                "propertyNames": {"minLength": 1, "pattern": "\\S"},
                "additionalProperties": {"type": ["string", "number", "boolean"]},
            },
            "body": {
                "description": "JSON request body.",
                "type": ["object", "array", "string", "number", "boolean", "null"],
            },
            "reason": {
                "type": "string",
                "minLength": 1,
                "pattern": "\\S",
                "description": "Brief user-visible reason for the action.",
            },
        },
        "required": ["path", "reason"],
        "additionalProperties": False,
    },
}
