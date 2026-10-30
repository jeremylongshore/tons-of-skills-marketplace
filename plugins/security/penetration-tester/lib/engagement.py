"""Local engagement-file parsing and scope comparisons.

These helpers perform no DNS requests or signature verification. Unknown
target forms are rejected rather than treated as evidence of permission.
"""

from __future__ import annotations

import datetime as dt
import ipaddress
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


def load_mapping(path: Path) -> dict[str, Any]:
    """Read YAML with PyYAML, or JSON when PyYAML is unavailable."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError("Engagement file not found") from exc
    except (OSError, UnicodeError) as exc:
        raise ValueError("Cannot read engagement file") from exc
    try:
        import yaml
    except ImportError:
        try:
            data = json.loads(text)
        except ValueError as exc:
            raise ValueError("YAML requires PyYAML; JSON is also supported") from exc
    else:
        try:
            data = yaml.safe_load(text)
        except (yaml.YAMLError, ValueError, TypeError, OverflowError) as exc:
            raise ValueError("Invalid YAML or JSON engagement file") from exc
    if not isinstance(data, dict):
        raise ValueError("Engagement file must contain a mapping")
    return data


def parse_timestamp(value: Any) -> dt.datetime | None:
    """Require an ISO timestamp with an explicit UTC offset."""
    if isinstance(value, dt.datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    try:
        return parsed.astimezone(dt.timezone.utc)
    except (ValueError, OverflowError):
        return None


def _host(value: str) -> str | None:
    if "%" in value or value.endswith(".."):
        return None
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        pass
    value = value.rstrip(".").lower()
    if len(value) > 253 or re.fullmatch(r"[0-9.]+", value):
        return None
    labels = value.split(".")
    if not all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label) for label in labels):
        return None
    return value


def classify_target(entry: Any) -> tuple[str, str, str | None]:
    """Return raw value, target type and normalized value without resolving it."""
    if isinstance(entry, dict):
        keys = set(entry) & {"host", "cidr", "url", "cloud_account", "saas_tenant"}
        if len(keys) != 1:
            return "invalid entry", "malformed", None
        field = keys.pop()
        if not isinstance(entry[field], str):
            return "invalid entry", "malformed", None
        raw, kind, normalized = classify_target(entry[field])
        expected = {
            "host": {"hostname", "wildcard", "ipv4", "ipv6"},
            "cidr": {"cidrv4", "cidrv6"},
            "url": {"url"},
            "cloud_account": {"cloud"},
            "saas_tenant": {"saas"},
        }
        return (raw, kind, normalized) if kind in expected[field] else (raw, "malformed", None)
    if not isinstance(entry, str):
        return "invalid entry", "malformed", None
    raw = entry.strip()
    invalid = (raw, "malformed", None)
    if not raw or "%" in raw or any(c.isspace() for c in raw):
        return invalid
    if raw.lower().startswith(("http://", "https://")):
        try:
            uri = urlsplit(raw)
            host = _host(uri.hostname or "")
            port = uri.port
            if not host or uri.username is not None or uri.password is not None or "?" in raw or "#" in raw:
                return invalid
            # Encoded/dot-segment paths require server-specific normalization;
            # this offline checker cannot safely grant scope for them.
            if "%" in uri.path or "\\" in uri.path or any(x in (".", "..") for x in uri.path.split("/")):
                return invalid
            if port is not None and not 1 <= port <= 65535:
                return invalid
            netloc = f"[{host}]" if ":" in host else host
            if port is not None and port != {"http": 80, "https": 443}[uri.scheme]:
                netloc += f":{port}"
            return raw, "url", urlunsplit((uri.scheme, netloc, uri.path or "/", "", ""))
        except ValueError:
            return invalid
    prefix, sep, identifier = raw.partition(":")
    cloud = {"aws", "gcp", "azure"}
    saas = {"okta", "auth0", "saml", "google-workspace", "microsoft365", "salesforce"}
    if sep and prefix.lower() in cloud | saas:
        if not re.fullmatch(r"[A-Za-z0-9._-]+", identifier):
            return invalid
        kind = "cloud" if prefix.lower() in cloud else "saas"
        return raw, kind, prefix.lower() + ":" + identifier
    try:
        if "/" in raw:
            network = ipaddress.ip_network(raw, strict=False)
            return raw, f"cidrv{network.version}", str(network)
        address = ipaddress.ip_address(raw)
        return raw, f"ipv{address.version}", str(address)
    except ValueError:
        pass
    if raw.startswith("*."):
        suffix = _host(raw[2:])
        if suffix and ":" not in suffix and not re.fullmatch(r"[0-9.]+", suffix):
            return raw, "wildcard", "*." + suffix
        return invalid
    host = _host(raw)
    return (raw, "hostname", host) if host else invalid


def is_unbounded(entry: Any) -> bool:
    _, kind, normalized = classify_target(entry)
    return kind in ("cidrv4", "cidrv6") and ipaddress.ip_network(normalized).prefixlen == 0


def _network(kind: str, value: str):
    if kind in ("ipv4", "ipv6", "cidrv4", "cidrv6"):
        return ipaddress.ip_network(value, strict=False)
    return None


def scope_contains(scope: Any, target: Any) -> bool:
    """Whether the entire target lies inside one scope entry."""
    _, sk, sn = classify_target(scope)
    _, tk, tn = classify_target(target)
    if sn is None or tn is None:
        return False
    if (sk, sn) == (tk, tn):
        return True
    su = urlsplit(sn) if sk == "url" else None
    tu = urlsplit(tn) if tk == "url" else None
    scope_net = _network(sk, sn)
    target_net = _network(tk, tn)
    if scope_net is not None:
        if tu is not None:
            try:
                target_net = ipaddress.ip_network(tu.hostname, strict=False)
            except ValueError:
                return False
        return target_net is not None and scope_net.version == target_net.version and target_net.subnet_of(scope_net)
    if sk == "url":
        if tu is None or (su.scheme, su.netloc) != (tu.scheme, tu.netloc):
            return False
        base = su.path.rstrip("/")
        return not base or tu.path == base or tu.path.startswith(base + "/")
    target_host = tu.hostname if tu is not None else tn
    if sk == "hostname":
        return tk in ("hostname", "url") and sn == target_host
    if sk == "wildcard" and tk in ("hostname", "wildcard", "url"):
        return target_host.endswith("." + sn[2:])
    return False


def scopes_overlap(left: Any, right: Any) -> bool:
    """Detect intersections, including hostname/URL and wildcard exclusions."""
    _, lk, ln = classify_target(left)
    _, rk, rn = classify_target(right)
    if ln is None or rn is None:
        return False
    a, b = _network(lk, ln), _network(rk, rn)
    if a is not None and b is not None:
        return a.version == b.version and a.overlaps(b)
    return scope_contains(left, right) or scope_contains(right, left)
