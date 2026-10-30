"""Scoped HTTP method experiments on exclusively owned disposable fixtures.

No request is issued during permission validation. The ledger is exclusive and
durable before each request; an ambiguous response stops the experiment rather
than retrying a mutation or deleting an unverified resource.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import secrets
import stat
import time
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

from .engagement import classify_target, load_mapping, parse_timestamp, scope_contains, scopes_overlap

ACTIVE_METHODS = frozenset({"TRACE", "DEBUG", "PROPFIND", "PUT", "DELETE", "MKCOL", "COPY", "MOVE", "CONNECT"})
WRITE_METHODS = frozenset({"PUT", "DELETE", "MKCOL", "COPY", "MOVE"})
MAX_BODY = 65536


class Inconclusive(Exception):
    """The experiment lacks sufficient evidence to continue safely."""


def canonical_url(value: object) -> str:
    _, kind, normalized = classify_target(value)
    if kind != "url" or normalized is None:
        raise ValueError("A literal HTTP(S) URL without credentials or ambiguous path syntax is required")
    return normalized


def origin(value: str) -> str:
    scheme, _, rest = value.partition("://")
    return scheme + "://" + rest.split("/", 1)[0]


def validate_permission(path: Path, target: str, methods: list[str]) -> dict:
    """Check existing ROE contracts plus explicit method and fixture permission.

    This checks structural attestations, not cryptographic identity or legal
    authority. The caller must independently obtain the owner's approval.
    """
    roe = load_mapping(path)
    checker = (
        Path(__file__).resolve().parents[1] / "skills/confirming-pentest-authorization/scripts/check_authorization.py"
    )
    spec = importlib.util.spec_from_file_location("method_probe_roe_check", checker)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    findings = module.validate_roe(roe, "method probe permission", [])
    if any(f.severity.value != "info" for f in findings):
        raise ValueError("ROE metadata, scope or attested time window failed validation")
    target = canonical_url(target)
    grant = roe.get("http_method_probe")
    if not isinstance(grant, dict) or canonical_url(grant.get("target")) != target:
        raise ValueError("ROE must contain an exact http_method_probe target")
    allowed = grant.get("allowed_methods")
    if not isinstance(allowed, list) or any(
        not isinstance(m, str) or m not in ACTIVE_METHODS | {"LOCK"} for m in allowed
    ):
        raise ValueError("allowed_methods must contain supported uppercase method names")
    if (
        not isinstance(methods, list)
        or not methods
        or not all(isinstance(m, str) and m in ACTIVE_METHODS for m in methods)
    ):
        raise ValueError("Request a nonempty list of supported method names")
    if len(methods) != len(set(methods)) or not set(methods) <= set(allowed):
        raise ValueError("Every requested method must have separate explicit ROE permission")
    unexpected = grant.get("unexpected_methods", [])
    if not isinstance(unexpected, list) or not all(isinstance(m, str) and m in allowed for m in unexpected):
        raise ValueError("unexpected_methods must be an explicitly attested subset of allowed_methods")

    def scoped(url: str) -> bool:
        return any(scope_contains(s, url) for s in roe["in_scope_targets"]) and not any(
            scopes_overlap(s, url) for s in roe.get("out_of_scope_targets", [])
        )

    if not scoped(target):
        raise ValueError("The requested target is outside the attested scope or explicitly excluded")
    result = dict(grant)
    result["requested_methods"] = tuple(methods)
    result["target"] = target
    result["expires"] = parse_timestamp(roe["time_window"]["end"])
    if set(methods) & WRITE_METHODS:
        base = canonical_url(grant.get("disposable_base"))
        if origin(base) != origin(target) or base == origin(base) + "/" or not base.endswith("/"):
            raise ValueError("Writes require a dedicated same-origin disposable directory")
        if not scoped(base):
            raise ValueError("The entire disposable directory must be included and have no overlapping exclusion")
        if grant.get("exclusive_disposable_namespace") is not True or grant.get("cleanup_authorized") is not True:
            raise ValueError("Exclusive fixture ownership and cleanup require explicit true attestations")
        helpers = {"DELETE"}
        if set(methods) & {"PUT", "DELETE", "COPY", "MOVE"}:
            helpers.add("PUT")
        if "MKCOL" in methods:
            helpers.update({"PROPFIND", "LOCK"})
        if not helpers <= set(allowed):
            raise ValueError("Fixture creation, inspection and cleanup require explicit helper-method permission")
        result["disposable_base"] = base
    if "CONNECT" in methods:
        destination = canonical_url(grant.get("proxy_destination"))
        if not target.startswith("http://") or target != origin(target) + "/":
            raise ValueError("Controlled CONNECT verification supports an explicit HTTP proxy root only")
        if not destination.startswith("https://") or not scoped(destination):
            raise ValueError("The controlled HTTPS proxy destination must be explicitly in scope")
        digest = grant.get("proxy_response_sha256")
        if (
            grant.get("controlled_proxy_destination") is not True
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise ValueError("CONNECT needs an attested controlled destination and its expected response digest")
        result["proxy_destination"] = destination
    if "DEBUG" in methods:
        digest = grant.get("debug_response_sha256")
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError("DEBUG verification requires an owner-approved response fixture digest")
    return result


class Ledger:
    """Never overwrite/reuse a prior operation ledger or resume writes blindly."""

    def __init__(self, path: Path):
        # Pin the verified directory descriptor: checking a path and later
        # reopening it would allow a parent-path replacement between operations.
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            parent = os.fstat(directory)
            if parent.st_uid != os.getuid() or stat.S_IMODE(parent.st_mode) & 0o077:
                raise ValueError("The ledger parent must be owned by the current user and private (0700)")
            fd = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
            self.file = os.fdopen(fd, "w", encoding="utf-8")
            try:
                self.write({"phase": "started", "version": 1})
                os.fsync(directory)
            except Exception:
                self.file.close()
                raise
        finally:
            os.close(directory)

    def write(self, event: dict) -> None:
        self.file.write(json.dumps({"time": dt.datetime.now(dt.timezone.utc).isoformat(), **event}) + "\n")
        self.file.flush()
        os.fsync(self.file.fileno())

    def close(self) -> None:
        self.file.close()


class FixtureRunner:
    """Bounded, no-redirect, no-retry transport with verifiable fixture ownership."""

    def __init__(self, session, permission: dict, ledger: Ledger, timeout: float):
        if not math.isfinite(timeout) or not 0 < timeout <= 30:
            raise ValueError("The per-request timeout must be finite, greater than zero, and at most 30 seconds")
        self.session = session
        self.permission = permission
        self.ledger = ledger
        self.timeout = timeout
        self.deadline = time.monotonic() + 180
        self.requests = 0
        self.owned: dict[str, tuple[bytes, str]] = {}
        self.resources: set[str] = set()
        self.checked_absent: set[str] = set()
        self.attempted_creation: set[str] = set()
        self.collections: set[str] = set()
        self.collection_locks: dict[str, str] = {}
        session.trust_env = False
        session.auth = None
        session.proxies = {}
        for name in ("Authorization", "Proxy-Authorization", "Cookie"):
            session.headers.pop(name, None)

    def admit(self, method: str, url: str, kwargs: dict) -> None:
        if canonical_url(url) != url or url not in self.resources | {self.permission["target"]}:
            raise Inconclusive("A request escaped the exact target or generated disposable resources")
        if method in WRITE_METHODS | {"LOCK"} and url not in self.resources:
            raise Inconclusive("Writes are restricted to generated disposable resources, never the supplied target")
        if set(kwargs) - {"headers", "data"}:
            raise Inconclusive("Unsupported transport overrides are forbidden")
        headers = kwargs.get("headers", {})
        allowed_headers = {
            "If-Match",
            "If-None-Match",
            "Content-Type",
            "Destination",
            "Overwrite",
            "Depth",
            "X-Pentest-Nonce",
            "If",
            "Timeout",
        }
        if not isinstance(headers, dict) or any(
            k not in allowed_headers
            or not isinstance(v, str)
            or len(v) > 1024
            or any(ord(c) < 32 or ord(c) == 127 for c in v)
            for k, v in headers.items()
        ):
            raise Inconclusive("Unsupported or malformed request headers")
        payload = kwargs.get("data", b"")
        if not isinstance(payload, bytes) or len(payload) > 512:
            raise Inconclusive("Only bounded synthetic fixture payloads are supported")
        if method not in {"GET", "HEAD", "OPTIONS"} and method not in self.permission["allowed_methods"]:
            raise Inconclusive("This HTTP method lacks explicit permission")
        collection_helper = (
            method in {"LOCK", "PROPFIND"}
            and "MKCOL" in self.permission["requested_methods"]
            and url in self.collections
        )
        if (
            method not in WRITE_METHODS | {"GET", "HEAD", "OPTIONS"}
            and method not in self.permission["requested_methods"]
            and not collection_helper
        ):
            raise Inconclusive("This active method was not explicitly selected")
        if method == "CONNECT":
            raise Inconclusive("CONNECT requires the controlled tunnel adapter, not a status-only request")
        if method in {"PUT", "MKCOL"}:
            if (
                url not in self.checked_absent
                or url in self.owned
                or url in self.attempted_creation
                or headers.get("If-None-Match") != "*"
            ):
                raise Inconclusive("Creation requires a fresh absent fixture and a no-overwrite precondition")
        elif method in {"DELETE", "COPY", "MOVE"}:
            if url not in self.owned or headers.get("If-Match") != self.owned[url][1]:
                raise Inconclusive("Mutation requires verified fixture ownership and its strong ETag")
            if url in self.collections:
                token = self.collection_locks.get(url)
                if method != "DELETE" or token is None or headers.get("If") != "(" + token + ")":
                    raise Inconclusive("Collection cleanup requires its verified exclusive write lock")
            if method in {"COPY", "MOVE"}:
                destination = headers.get("Destination")
                if (
                    destination not in self.checked_absent
                    or destination not in self.resources
                    or destination in self.owned
                    or destination in self.attempted_creation
                    or headers.get("Overwrite") != "F"
                ):
                    raise Inconclusive("WebDAV destination must be a fresh disposable resource with overwrite disabled")
        elif method == "LOCK":
            if (
                not collection_helper
                or url not in self.owned
                or headers.get("If-Match") != self.owned[url][1]
                or headers.get("Depth") != "infinity"
                or headers.get("Timeout") != "Second-60"
            ):
                raise Inconclusive("LOCK is only supported on the verified disposable collection")

    def request(self, method: str, url: str, **kwargs) -> tuple[int, dict, bytes]:
        self.admit(method, url, kwargs)
        remaining = self.deadline - time.monotonic()
        if remaining <= 0 or self.requests >= 64 or dt.datetime.now(dt.timezone.utc) >= self.permission["expires"]:
            raise Inconclusive("The request budget or attested time window has expired")
        self.ledger.write({"phase": "intent", "method": method, "url": url})
        self.requests += 1
        if method in WRITE_METHODS:
            self.checked_absent.discard(url)
            if method in {"PUT", "MKCOL"}:
                self.attempted_creation.add(url)
            if method in {"COPY", "MOVE"}:
                self.checked_absent.discard(kwargs["headers"]["Destination"])
                self.attempted_creation.add(kwargs["headers"]["Destination"])
        self.session.cookies.clear()
        response = None
        try:
            response = self.session.request(
                method, url, timeout=min(self.timeout, remaining), allow_redirects=False, stream=True, **kwargs
            )
            body = bytearray()
            # Check the total deadline even for a slow byte-at-a-time peer.
            for chunk in response.iter_content(chunk_size=1):
                if time.monotonic() >= self.deadline or len(body) + len(chunk) > MAX_BODY:
                    raise Inconclusive("The response exceeded its deadline or body-size bound")
                body.extend(chunk)
            status, headers, data = response.status_code, dict(response.headers), bytes(body)
            self.ledger.write(
                {
                    "phase": "response",
                    "method": method,
                    "url": url,
                    "status": status,
                    "body_sha256": hashlib.sha256(data).hexdigest(),
                }
            )
            return status, headers, data
        except Inconclusive:
            self.ledger.write({"phase": "ambiguous", "method": method, "url": url, "error_class": "ResponseBound"})
            raise
        except Exception as exc:
            self.ledger.write({"phase": "ambiguous", "method": method, "url": url, "error_class": type(exc).__name__})
            raise Inconclusive(
                "Request failed; inspect the private ledger and reconcile before further mutation"
            ) from exc
        finally:
            if response is not None:
                response.close()

    @staticmethod
    def strong_etag(headers: dict) -> str:
        value = next((v for k, v in headers.items() if k.lower() == "etag"), "")
        if not isinstance(value, str) or re.fullmatch(r'"[\x21\x23-\x7e]{1,200}"', value) is None:
            raise Inconclusive("A strong fixture ETag was not available; no conditional mutation is safe")
        return value

    def fresh_url(self, collection: bool = False) -> str:
        url = self.permission["disposable_base"] + "method-probe-" + secrets.token_hex(24) + ("/" if collection else "")
        if url in self.resources:
            raise Inconclusive("A fixture identifier collision occurred")
        self.resources.add(url)
        return url

    def absent(self, url: str) -> None:
        status, _, _ = self.request("HEAD", url)
        if status != 404:
            raise Inconclusive("The unique fixture resource is not demonstrably absent; no write was attempted")
        self.checked_absent.add(url)

    def create(self) -> str:
        url = self.fresh_url()
        self.absent(url)
        payload = ("synthetic-method-probe:" + secrets.token_hex(32)).encode("ascii")
        status, _, _ = self.request(
            "PUT", url, data=payload, headers={"If-None-Match": "*", "Content-Type": "application/octet-stream"}
        )
        if status != 201:
            raise Inconclusive(
                "Creation was not confirmed as a new resource; preserve the ledger for manual reconciliation"
            )
        status, headers, body = self.request("GET", url)
        if status != 200 or body != payload:
            raise Inconclusive("The new fixture could not be identified by exact payload readback")
        etag = self.strong_etag(headers)
        self.owned[url] = payload, etag
        self.ledger.write(
            {"phase": "owned", "url": url, "etag": etag, "body_sha256": hashlib.sha256(payload).hexdigest()}
        )
        return url

    def cleanup(self, url: str) -> None:
        payload, etag = self.owned[url]
        status, headers, body = self.request("GET", url)
        if status != 200 or body != payload or self.strong_etag(headers) != etag:
            raise Inconclusive("Fixture ownership changed; it was not deleted")
        status, _, _ = self.request("DELETE", url, headers={"If-Match": etag})
        if status not in (200, 204):
            raise Inconclusive("Conditional cleanup was not confirmed; the fixture remains pending")
        self.absent(url)
        del self.owned[url]
        self.ledger.write({"phase": "cleaned", "url": url})

    @staticmethod
    def dav_xml(body: bytes):
        try:
            text = body.decode("utf-8")
            if "<!" in text or "\x00" in text or len(body) > MAX_BODY:
                raise ValueError("Unsupported XML declaration or size")
            return ET.fromstring(text)
        except (UnicodeError, ET.ParseError, ValueError) as exc:
            raise Inconclusive("WebDAV response was not bounded UTF-8 XML without declarations") from exc

    def empty_collection(self, url: str) -> str:
        status, _, body = self.request(
            "PROPFIND",
            url,
            headers={"Depth": "1", "Content-Type": "application/xml; charset=utf-8"},
            data=b'<d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/><d:getetag/></d:prop></d:propfind>',
        )
        if status != 207:
            raise Inconclusive("Collection membership could not be inspected")
        tree = self.dav_xml(body)
        responses = tree.findall("{DAV:}response")
        if tree.tag != "{DAV:}multistatus" or len(responses) != 1 or len(list(tree)) != 1:
            raise Inconclusive("The disposable collection was not demonstrably empty")
        response = responses[0]
        hrefs = response.findall("{DAV:}href")
        try:
            if len(hrefs) != 1 or not hrefs[0].text or canonical_url(urljoin(url, hrefs[0].text)) != url:
                raise ValueError("Wrong collection identity")
        except ValueError as exc:
            raise Inconclusive("The DAV response did not identify the exact collection") from exc
        etags = []
        collection = False
        for part in response.findall("{DAV:}propstat"):
            statuses = part.findall("{DAV:}status")
            if len(statuses) != 1 or re.fullmatch(r"HTTP/1\.[01] 200(?: [^\r\n]*)?", statuses[0].text or "") is None:
                raise Inconclusive("Collection properties were incomplete or ambiguous")
            collection |= part.find("{DAV:}prop/{DAV:}resourcetype/{DAV:}collection") is not None
            etags.extend(p.text for p in part.findall("{DAV:}prop/{DAV:}getetag"))
        if not collection or len(etags) != 1:
            raise Inconclusive("Collection type and unique ETag were not verified")
        return self.strong_etag({"ETag": etags[0]})

    def collection_probe(self) -> dict:
        """Verify MKCOL and cleanup only an empty, exclusively locked fixture.

        Relies on RFC 4918 compliant write-lock enforcement. Unknown server
        semantics, lost acknowledgements or unexpected children stop cleanup.
        No speculative recursive deletion or mutation retry is performed.
        """
        if "MKCOL" not in self.permission["requested_methods"]:
            raise Inconclusive("MKCOL was not explicitly selected")
        url = self.fresh_url(collection=True)
        self.absent(url)
        status, _, _ = self.request("MKCOL", url, headers={"If-None-Match": "*"})
        if status != 201:
            raise Inconclusive("Collection creation was not confirmed; reconcile the private ledger")
        self.collections.add(url)
        etag = self.empty_collection(url)
        self.owned[url] = b"", etag
        self.ledger.write({"phase": "owned-collection", "url": url, "etag": etag})
        nonce = secrets.token_hex(24)
        payload = (
            '<d:lockinfo xmlns:d="DAV:"><d:lockscope><d:exclusive/></d:lockscope>'
            "<d:locktype><d:write/></d:locktype><d:owner>" + nonce + "</d:owner></d:lockinfo>"
        ).encode("ascii")
        lock_started = time.monotonic()
        status, headers, body = self.request(
            "LOCK",
            url,
            data=payload,
            headers={"If-Match": etag, "Depth": "infinity", "Timeout": "Second-60", "Content-Type": "application/xml"},
        )
        token = next((v for k, v in headers.items() if k.lower() == "lock-token"), "")
        if (
            status != 200
            or not isinstance(token, str)
            or re.fullmatch(r"<[A-Za-z][A-Za-z0-9+.-]*:[A-Za-z0-9:/._~-]{1,200}>", token) is None
        ):
            raise Inconclusive("Exclusive collection lock was not confirmed; no deletion attempted")
        tree = self.dav_xml(body)
        locks = tree.findall("{DAV:}lockdiscovery/{DAV:}activelock")
        if tree.tag != "{DAV:}prop" or len(locks) != 1:
            raise Inconclusive("The lock response did not describe a unique active lock")
        lock = locks[0]
        timeout = lock.findtext("{DAV:}timeout", "")
        try:
            lock_root = canonical_url(lock.findtext("{DAV:}lockroot/{DAV:}href", ""))
        except ValueError as exc:
            raise Inconclusive("The lock root was not the exact disposable collection") from exc
        if (
            lock.find("{DAV:}lockscope/{DAV:}exclusive") is None
            or lock.find("{DAV:}locktype/{DAV:}write") is None
            or lock.findtext("{DAV:}depth") != "infinity"
            or lock.findtext("{DAV:}owner") != nonce
            or lock.findtext("{DAV:}locktoken/{DAV:}href") != token[1:-1]
            or lock_root != url
            or re.fullmatch(r"Second-[1-9][0-9]?", timeout) is None
            or int(timeout.partition("-")[2]) > 60
        ):
            raise Inconclusive("The server did not confirm the bounded exclusive write-lock contract")
        self.collection_locks[url] = token
        self.ledger.write(
            {"phase": "locked-collection", "url": url, "token_sha256": hashlib.sha256(token.encode()).hexdigest()}
        )
        # Inspect after locking: an ETag alone need not cover concurrent children.
        etag = self.empty_collection(url)
        self.owned[url] = b"", etag
        if time.monotonic() >= lock_started + int(timeout.partition("-")[2]):
            raise Inconclusive("The collection lock may have expired; no deletion attempted")
        status, _, _ = self.request("DELETE", url, headers={"If-Match": etag, "If": "(" + token + ")"})
        if status not in (200, 204):
            raise Inconclusive("Locked collection cleanup was not confirmed")
        self.absent(url)
        del self.owned[url]
        del self.collection_locks[url]
        self.collections.remove(url)
        result = {
            "method": "MKCOL",
            "outcome": "verified",
            "cleanup": "verified",
            "fixture_id": hashlib.sha256(url.encode()).hexdigest(),
        }
        self.ledger.write({"phase": "verified", **result})
        return result

    def file_probe(self, method: str) -> dict:
        if method not in {"PUT", "DELETE", "COPY", "MOVE"}:
            raise Inconclusive("This adapter only verifies disposable file operations")
        if method not in self.permission["requested_methods"]:
            raise Inconclusive("This file method was not explicitly selected")
        source = self.create()
        payload, etag = self.owned[source]
        if method in {"COPY", "MOVE"}:
            destination = self.fresh_url()
            self.absent(destination)
            status, headers, body = self.request("GET", source)
            if status != 200 or body != payload or self.strong_etag(headers) != etag:
                raise Inconclusive("The source fixture changed before the WebDAV operation")
            status, _, _ = self.request(
                method, source, headers={"If-Match": etag, "Destination": destination, "Overwrite": "F"}
            )
            if status != 201:
                raise Inconclusive("WebDAV did not confirm creation of a new destination; reconcile both fixture URLs")
            status, headers, body = self.request("GET", destination)
            if status != 200 or body != payload:
                raise Inconclusive("The WebDAV destination failed exact synthetic payload verification")
            self.owned[destination] = payload, self.strong_etag(headers)
            if method == "MOVE":
                self.absent(source)
                del self.owned[source]
            self.cleanup(destination)
        if source in self.owned:
            self.cleanup(source)
        result = {
            "method": method,
            "outcome": "verified",
            "fixture_id": hashlib.sha256(source.encode()).hexdigest(),
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "cleanup": "verified",
        }
        self.ledger.write({"phase": "verified", **result})
        return result

    def trace_probe(self) -> dict:
        nonce = secrets.token_hex(24)
        status, _, body = self.request("TRACE", self.permission["target"], headers={"X-Pentest-Nonce": nonce})
        if status in (401, 403, 405, 501):
            return {"method": "TRACE", "outcome": "rejected", "status_code": status}
        path = "/" + self.permission["target"].partition("://")[2].partition("/")[2]
        if not 200 <= status < 300 or nonce.encode() not in body or ("TRACE " + path + " HTTP/").encode() not in body:
            raise Inconclusive("TRACE did not demonstrate both a request line and the fresh nonce echo")
        result = {
            "method": "TRACE",
            "outcome": "verified",
            "proof": "request-line-and-nonce-echo",
            "response_sha256": hashlib.sha256(body).hexdigest(),
        }
        self.ledger.write({"phase": "verified", **result})
        return result

    def propfind_probe(self) -> dict:
        """Inspect only the selected resource with Depth: 0 (RFC 4918 §9.1)."""
        status, _, body = self.request(
            "PROPFIND",
            self.permission["target"],
            headers={"Depth": "0", "Content-Type": "application/xml; charset=utf-8"},
            data=b'<d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/></d:prop></d:propfind>',
        )
        if status in (401, 403, 405, 501):
            return {"method": "PROPFIND", "outcome": "rejected", "status_code": status}
        if status != 207:
            raise Inconclusive("PROPFIND did not return a WebDAV multistatus response")
        try:
            text = body.decode("utf-8")
            # Reject declarations, DTDs, entities and comments before parsing.
            # UTF-8-only decoding also prevents UTF-16 declaration bypasses.
            if "<!" in text or "\x00" in text:
                raise ValueError("Unsupported XML declaration")
            tree = ET.fromstring(text)
            if tree.tag != "{DAV:}multistatus":
                raise ValueError("Missing DAV multistatus")
            responses = tree.findall("{DAV:}response")
            if len(responses) != 1 or len(list(tree)) != 1:
                raise ValueError("Depth-zero response must describe exactly one resource")
            response = responses[0]
            hrefs = response.findall("{DAV:}href")
            if len(hrefs) != 1 or not hrefs[0].text:
                raise ValueError("Missing unique resource href")
            resource = canonical_url(urljoin(self.permission["target"], hrefs[0].text))
            if resource != self.permission["target"]:
                raise ValueError("The response describes another resource")
            valid = False
            for propstat in response.findall("{DAV:}propstat"):
                statuses = propstat.findall("{DAV:}status")
                if len(statuses) != 1:
                    raise ValueError("Ambiguous property status")
                if re.fullmatch(r"HTTP/1\.[01] 200(?: [^\r\n]*)?", statuses[0].text or ""):
                    valid |= propstat.find("{DAV:}prop/{DAV:}resourcetype") is not None
            if not valid:
                raise ValueError("Requested resource type was not successfully returned")
        except (UnicodeError, ET.ParseError, ValueError) as exc:
            raise Inconclusive("PROPFIND lacked bounded, exact-resource DAV property evidence") from exc
        result = {
            "method": "PROPFIND",
            "outcome": "verified",
            "proof": "depth-zero-exact-resource-property",
            "response_sha256": hashlib.sha256(body).hexdigest(),
        }
        self.ledger.write({"phase": "verified", **result})
        return result

    def debug_probe(self) -> dict:
        """Compare an explicitly approved DEBUG fixture; a 200 is not proof."""
        expected = self.permission.get("debug_response_sha256")
        if not isinstance(expected, str) or re.fullmatch(r"[0-9a-f]{64}", expected) is None:
            raise Inconclusive("DEBUG requires an owner-approved response fixture digest")
        status, _, body = self.request("DEBUG", self.permission["target"])
        if status in (401, 403, 405, 501):
            return {"method": "DEBUG", "outcome": "rejected", "status_code": status}
        digest = hashlib.sha256(body).hexdigest()
        if status != 200 or digest != expected:
            raise Inconclusive("DEBUG did not return the exact owner-approved response fixture")
        result = {
            "method": "DEBUG",
            "outcome": "verified",
            "proof": "owner-approved-response-fixture",
            "response_sha256": digest,
        }
        self.ledger.write({"phase": "verified", **result})
        return result

    def connect_probe(self) -> dict:
        destination = self.permission.get("proxy_destination")
        if "CONNECT" not in self.permission["requested_methods"] or not isinstance(destination, str):
            raise Inconclusive("Controlled CONNECT destination permission is missing")
        remaining = self.deadline - time.monotonic()
        if remaining <= 0 or self.requests + 2 > 64 or dt.datetime.now(dt.timezone.utc) >= self.permission["expires"]:
            raise Inconclusive("The tunnel request budget or attested time window has expired")
        self.ledger.write(
            {"phase": "intent", "method": "CONNECT", "url": self.permission["target"], "destination": destination}
        )
        self.requests += 2
        self.session.cookies.clear()
        response = None
        try:
            # An explicit HTTPS request through the approved HTTP proxy makes
            # the HTTP adapter perform CONNECT. TLS verification and an exact
            # controlled-response digest establish more than a proxy's 200.
            response = self.session.request(
                "GET",
                destination,
                proxies={"https": self.permission["target"]},
                verify=True,
                timeout=min(self.timeout, remaining),
                allow_redirects=False,
                stream=True,
            )
            body = bytearray()
            for chunk in response.iter_content(chunk_size=1):
                if time.monotonic() >= self.deadline or len(body) + len(chunk) > MAX_BODY:
                    raise Inconclusive("The tunnel response exceeded its deadline or size bound")
                body.extend(chunk)
            digest = hashlib.sha256(body).hexdigest()
            self.ledger.write(
                {"phase": "response", "method": "CONNECT", "status": response.status_code, "body_sha256": digest}
            )
            if response.status_code != 200 or digest != self.permission["proxy_response_sha256"]:
                raise Inconclusive("The authenticated controlled destination did not return the expected fixture")
            result = {
                "method": "CONNECT",
                "outcome": "verified",
                "proof": "verified-TLS-controlled-destination",
                "response_sha256": digest,
            }
            self.ledger.write({"phase": "verified", **result})
            return result
        except Exception as exc:
            self.ledger.write({"phase": "ambiguous", "method": "CONNECT", "error_class": type(exc).__name__})
            if isinstance(exc, Inconclusive):
                raise
            raise Inconclusive(
                "Controlled CONNECT verification failed; no arbitrary proxy capability is inferred"
            ) from exc
        finally:
            if response is not None:
                response.close()
