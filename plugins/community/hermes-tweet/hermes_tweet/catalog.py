# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from typing import Any, cast
from urllib.parse import urlsplit

DEFAULT_LIMIT = 25
MAX_LIMIT = 100


@dataclass(frozen=True)
class Endpoint:
    category: str
    free: bool
    method: str
    path: str
    summary: str
    parameters: tuple[dict[str, Any], ...] = ()
    response_shape: str | None = None
    mpp: dict[str, str] | None = None
    action: bool = False

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "category": self.category,
            "free": self.free,
            "method": self.method,
            "path": self.path,
            "summary": self.summary,
            "action": self.action,
        }
        if self.parameters:
            data["parameters"] = list(self.parameters)
        if self.response_shape:
            data["responseShape"] = self.response_shape
        if self.mpp:
            data["mpp"] = self.mpp
        return data


def _load_raw() -> list[dict[str, Any]]:
    text = (
        files(__package__ or "hermes_tweet")
        .joinpath("catalog_data.json")
        .read_text(encoding="utf-8")
    )
    data = cast("object", json.loads(text))
    items = cast("list[object]", data if isinstance(data, list) else [])
    return [cast("dict[str, Any]", item) for item in items if isinstance(item, dict)]


def _tuple_parameters(value: Any) -> tuple[dict[str, Any], ...]:
    items = cast("list[object]", value if isinstance(value, list) else [])
    return tuple(cast("dict[str, Any]", item) for item in items if isinstance(item, dict))


def _endpoint(item: dict[str, Any]) -> Endpoint:
    return Endpoint(
        action=bool(item.get("action")),
        category=str(item.get("category", "unknown")),
        free=bool(item.get("free", False)),
        method=str(item.get("method", "GET")).upper(),
        mpp=item.get("mpp") if isinstance(item.get("mpp"), dict) else None,
        parameters=_tuple_parameters(item.get("parameters")),
        path=str(item.get("path", "")),
        response_shape=str(item["responseShape"]) if item.get("responseShape") else None,
        summary=str(item.get("summary", "")),
    )


ENDPOINTS: tuple[Endpoint, ...] = tuple(_endpoint(item) for item in _load_raw())


def normalize_method(method: Any, *, default: str = "GET") -> str:
    if not isinstance(method, str):
        return default.upper()
    normalized = method.strip().upper()
    return normalized or default.upper()


def normalize_limit(value: Any) -> int:
    if isinstance(value, bool):
        return DEFAULT_LIMIT
    if isinstance(value, str):
        value = value.strip()
        if not value.isdecimal():
            return DEFAULT_LIMIT
        return normalize_limit(int(value))
    if not isinstance(value, int):
        return DEFAULT_LIMIT
    return min(max(value, 1), MAX_LIMIT)


def _optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    return None


def _optional_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def _optional_method(value: Any) -> str | None:
    normalized = _optional_text(value)
    if not normalized:
        return None
    return normalize_method(normalized)


def _segments(path: str) -> list[str]:
    normalized = path.removesuffix("/")
    return normalized.split("/")


def normalize_path(path: str) -> str:
    return urlsplit(path.strip()).path


def matches_path(template: str, concrete: str) -> bool:
    normalized_template = normalize_path(template)
    normalized_concrete = normalize_path(concrete)
    if normalized_template == normalized_concrete:
        return True
    template_segments = _segments(normalized_template)
    concrete_segments = _segments(normalized_concrete)
    if len(template_segments) != len(concrete_segments):
        return False
    for template_segment, concrete_segment in zip(
        template_segments, concrete_segments, strict=True
    ):
        if template_segment.startswith("{") and template_segment.endswith("}"):
            if not concrete_segment:
                return False
            continue
        if template_segment.startswith(":"):
            if not concrete_segment:
                return False
            continue
        if template_segment != concrete_segment:
            return False
    return True


def find_endpoint(method: str, path: str) -> Endpoint | None:
    normalized = normalize_method(method)
    normalized_path = normalize_path(path)
    for endpoint in ENDPOINTS:
        if endpoint.method == normalized and matches_path(endpoint.path, normalized_path):
            return endpoint
    return None


def _matches_query(endpoint: Endpoint, query: str) -> bool:
    normalized = query.lower()
    haystack = " ".join(
        [
            endpoint.category,
            endpoint.method,
            endpoint.path,
            endpoint.summary,
            endpoint.response_shape or "",
            json.dumps(list(endpoint.parameters), ensure_ascii=False),
        ]
    ).lower()
    return normalized in haystack


def explore(args: dict[str, Any]) -> list[dict[str, Any]]:
    method = _optional_method(args.get("method"))
    category = _optional_text(args.get("category")).lower()
    path = _optional_text(args.get("path"))
    query = _optional_text(args.get("query"))
    limit = normalize_limit(args.get("limit"))
    include_actions = _optional_bool(args.get("include_actions")) is True

    endpoints = ENDPOINTS
    if method:
        endpoints = tuple(endpoint for endpoint in endpoints if endpoint.method == method)
    if category:
        endpoints = tuple(
            endpoint for endpoint in endpoints if endpoint.category.lower() == category
        )
    if path:
        endpoints = tuple(
            endpoint
            for endpoint in endpoints
            if path in endpoint.path or matches_path(endpoint.path, path)
        )
    if query:
        endpoints = tuple(endpoint for endpoint in endpoints if _matches_query(endpoint, query))
    free = _optional_bool(args.get("free"))
    if free is not None:
        endpoints = tuple(endpoint for endpoint in endpoints if endpoint.free is free)
    mpp = _optional_bool(args.get("mpp"))
    if mpp is not None:
        endpoints = tuple(endpoint for endpoint in endpoints if (endpoint.mpp is not None) is mpp)
    if not include_actions:
        endpoints = tuple(endpoint for endpoint in endpoints if not endpoint.action)
    return [endpoint.to_dict() for endpoint in endpoints[:limit]]
