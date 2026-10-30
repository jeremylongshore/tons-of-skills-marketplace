"""Disposable-resource admission and cleanup use an in-memory HTTP peer only."""

from copy import deepcopy
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import xml.etree.ElementTree as ET

import pytest

from lib.method_probe import FixtureRunner, Inconclusive, Ledger, validate_permission

TARGET = "https://fixture.example.test/app"
BASE = "https://fixture.example.test/probe-fixtures/"


@pytest.fixture
def roe(sample_roe_dict):
    result = deepcopy(sample_roe_dict)
    now = dt.datetime.now(dt.timezone.utc)
    result["time_window"] = {
        "start": (now - dt.timedelta(hours=1)).isoformat(),
        "end": (now + dt.timedelta(hours=1)).isoformat(),
    }
    result["signature_block"]["signed_at"] = now.isoformat()
    result["in_scope_targets"] = ["https://fixture.example.test/"]
    result["out_of_scope_targets"] = []
    result["http_method_probe"] = {
        "target": TARGET,
        "allowed_methods": ["PUT", "DELETE", "COPY", "MOVE", "MKCOL", "TRACE"],
        "unexpected_methods": ["PUT"],
        "disposable_base": BASE,
        "exclusive_disposable_namespace": True,
        "cleanup_authorized": True,
    }
    return result


def permission(tmp_path, roe, methods=None, target=TARGET):
    path = tmp_path / "synthetic-roe.json"
    path.write_text(json.dumps(roe))
    return validate_permission(path, target, ["PUT"] if methods is None else methods)


def test_permission_reuses_roe_and_requires_exact_scoped_fixture_contract(tmp_path, roe):
    grant = permission(tmp_path, roe)
    assert grant["target"] == TARGET
    assert grant["disposable_base"] == BASE
    assert grant["expires"] > dt.datetime.now(dt.timezone.utc)


@pytest.mark.parametrize(
    "field,value",
    [
        ("target", "https://other.example.test/app"),
        ("allowed_methods", ["DELETE"]),
        ("allowed_methods", ["PUT", "DELETE", "POST"]),
        ("cleanup_authorized", "true"),
        ("exclusive_disposable_namespace", False),
        ("disposable_base", "https://fixture.example.test/"),
        ("disposable_base", "https://other.example.test/probe-fixtures/"),
        ("disposable_base", "https://fixture.example.test/probe-fixtures"),
        ("disposable_base", "https://fixture.example.test/probe-fixtures/%2e%2e/"),
        ("unexpected_methods", ["CONNECT"]),
    ],
)
def test_malformed_or_unapproved_permissions_block_before_transport(tmp_path, roe, field, value):
    roe["http_method_probe"][field] = value
    with pytest.raises(ValueError):
        permission(tmp_path, roe)


def test_any_overlapping_exclusion_blocks_entire_disposable_base(tmp_path, roe):
    roe["out_of_scope_targets"] = [BASE + "reserved/"]
    with pytest.raises(ValueError, match="exclusion"):
        permission(tmp_path, roe)


@pytest.mark.parametrize("methods", [["PUT", "PUT"], ["DEBUG"], [{}], []])
def test_requested_methods_must_be_distinct_and_explicitly_permitted(tmp_path, roe, methods):
    with pytest.raises(ValueError):
        permission(tmp_path, roe, methods)


def test_expired_roe_does_not_admit_writes(tmp_path, roe):
    now = dt.datetime.now(dt.timezone.utc)
    roe["time_window"] = {
        "start": (now - dt.timedelta(hours=2)).isoformat(),
        "end": (now - dt.timedelta(hours=1)).isoformat(),
    }
    with pytest.raises(ValueError, match="ROE"):
        permission(tmp_path, roe)


def test_ledger_is_private_exclusive_and_preserves_prior_bytes(tmp_path):
    tmp_path.chmod(0o700)
    path = tmp_path / "operations.jsonl"
    ledger = Ledger(path)
    ledger.write({"phase": "synthetic"})
    ledger.close()
    old = path.read_bytes()
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert [json.loads(line)["phase"] for line in old.splitlines()] == ["started", "synthetic"]
    with pytest.raises(FileExistsError):
        Ledger(path)
    assert path.read_bytes() == old
    alias = tmp_path / "alias.jsonl"
    alias.symlink_to(path)
    with pytest.raises(OSError):
        Ledger(alias)
    assert path.read_bytes() == old


def test_ledger_refuses_a_shared_parent(tmp_path):
    tmp_path.chmod(0o755)
    with pytest.raises(ValueError, match="private"):
        Ledger(tmp_path / "operations.jsonl")
    assert not (tmp_path / "operations.jsonl").exists()


class Response:
    def __init__(self, status, data=b"", headers=None):
        self.status_code = status
        self.headers = headers or {}
        self.data = data
        self.closed = False

    def iter_content(self, chunk_size):
        assert chunk_size == 1
        for byte in self.data:
            yield bytes([byte])

    def close(self):
        self.closed = True


class Peer:
    def __init__(self):
        self.headers = {"Authorization": "synthetic ambient", "Cookie": "synthetic ambient"}
        self.cookies = {"synthetic": "ambient"}
        self.proxies = {"https": "synthetic proxy"}
        self.auth = "synthetic ambient"
        self.trust_env = True
        self.data = {}
        self.calls = []
        self.fail_after_put = False
        self.destination_race = False
        self.move_keeps_source = False

    def request(self, method, url, **kwargs):
        assert not self.trust_env and self.auth is None and not self.cookies and not self.proxies
        assert "Authorization" not in self.headers and "Cookie" not in self.headers
        assert kwargs["allow_redirects"] is False and kwargs["stream"] is True
        self.calls.append((method, url, kwargs))
        headers = kwargs.get("headers", {})
        if method == "HEAD":
            return Response(200 if url in self.data else 404)
        if method == "GET":
            if url not in self.data:
                return Response(404)
            body, etag = self.data[url]
            return Response(200, body, {"ETag": etag})
        if method == "PUT":
            assert headers["If-None-Match"] == "*"
            if url in self.data:
                return Response(412)
            self.data[url] = kwargs["data"], '"synthetic-v1"'
            if self.fail_after_put:
                raise OSError("synthetic acknowledgement loss")
            return Response(201)
        if method == "DELETE":
            assert url in self.data and headers["If-Match"] == self.data[url][1]
            del self.data[url]
            return Response(204)
        if method in {"COPY", "MOVE"}:
            destination = headers["Destination"]
            assert headers["Overwrite"] == "F" and headers["If-Match"] == self.data[url][1]
            if self.destination_race:
                self.data[destination] = b"synthetic other writer", '"synthetic-other"'
            if destination in self.data:
                return Response(412)
            self.data[destination] = self.data[url]
            if method == "MOVE" and not self.move_keeps_source:
                del self.data[url]
            return Response(201)
        raise AssertionError("Unexpected fake-peer method " + method)


@pytest.fixture
def runner(tmp_path, roe):
    tmp_path.chmod(0o700)
    ledger = Ledger(tmp_path / "operations.jsonl")
    peer = Peer()
    result = FixtureRunner(peer, permission(tmp_path, roe, ["PUT", "DELETE", "COPY", "MOVE"]), ledger, 1.0)
    yield result, peer, tmp_path / "operations.jsonl"
    ledger.close()


def test_create_readback_and_conditional_cleanup_touch_only_owned_resource(runner):
    engine, peer, path = runner
    url = engine.create()
    payload = peer.data[url][0]
    assert url.startswith(BASE + "method-probe-") and url != TARGET
    assert engine.owned[url][0] == payload
    engine.cleanup(url)
    assert not peer.data and not engine.owned
    assert [m for m, _, _ in peer.calls] == ["HEAD", "PUT", "GET", "GET", "DELETE", "HEAD"]
    assert all(u == url for _, u, _ in peer.calls)
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert events[1]["phase"] == "intent" and events[-1]["phase"] == "cleaned"
    assert payload.decode() not in path.read_text()


def test_lost_create_acknowledgement_stops_without_retry_or_blind_delete(runner):
    engine, peer, path = runner
    peer.fail_after_put = True
    with pytest.raises(Inconclusive, match="reconcile"):
        engine.create()
    assert [m for m, _, _ in peer.calls] == ["HEAD", "PUT"]
    assert len(peer.data) == 1 and not engine.owned
    assert json.loads(path.read_text().splitlines()[-1])["phase"] == "ambiguous"


@pytest.mark.parametrize("replacement", [(b"synthetic other writer", '"synthetic-v1"'), (None, '"synthetic-v2"')])
def test_changed_fixture_is_never_deleted(runner, replacement):
    engine, peer, _ = runner
    url = engine.create()
    body, etag = replacement
    peer.data[url] = (peer.data[url][0] if body is None else body), etag
    with pytest.raises(Inconclusive, match="ownership"):
        engine.cleanup(url)
    assert all(method != "DELETE" for method, _, _ in peer.calls)
    assert url in peer.data


@pytest.mark.parametrize(
    "method,url,kwargs",
    [
        ("PUT", TARGET, {"data": b"synthetic", "headers": {"If-None-Match": "*"}}),
        ("DELETE", TARGET, {"headers": {"If-Match": '"synthetic"'}}),
        ("HEAD", "https://other.example.test/", {}),
        ("GET", TARGET, {"allow_redirects": True}),
        ("GET", TARGET, {"headers": {"Authorization": "synthetic"}}),
        ("GET", TARGET, {"headers": {"X-Pentest-Nonce": "synthetic\r\ninjection"}}),
        ("POST", TARGET, {}),
    ],
)
def test_transport_admission_blocks_unowned_or_out_of_scope_requests(runner, method, url, kwargs):
    engine, peer, _ = runner
    with pytest.raises(Inconclusive):
        engine.request(method, url, **kwargs)
    assert peer.calls == []


def test_expired_permission_stops_before_request(runner):
    engine, peer, _ = runner
    engine.permission["expires"] = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)
    with pytest.raises(Inconclusive, match="expired"):
        engine.request("HEAD", TARGET)
    assert peer.calls == []


def test_cleaned_identifier_is_not_reused_for_a_second_create(runner):
    engine, peer, _ = runner
    url = engine.create()
    engine.cleanup(url)
    before = len(peer.calls)
    with pytest.raises(Inconclusive, match="Creation"):
        engine.request("PUT", url, data=b"synthetic second creation", headers={"If-None-Match": "*"})
    assert len(peer.calls) == before


def test_weak_etag_never_authorizes_delete(runner):
    engine, peer, _ = runner
    url = engine.create()
    peer.data[url] = peer.data[url][0], 'W/"synthetic-v1"'
    with pytest.raises(Inconclusive, match="strong"):
        engine.cleanup(url)
    assert all(method != "DELETE" for method, _, _ in peer.calls)


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), 0, 31])
def test_runner_rejects_invalid_timeout_before_transport(runner, timeout):
    engine, peer, _ = runner
    with pytest.raises(ValueError, match="timeout"):
        FixtureRunner(peer, engine.permission, engine.ledger, timeout)
    assert peer.calls == []


@pytest.mark.parametrize("method", ["PUT", "DELETE", "COPY", "MOVE"])
def test_file_method_verification_requires_readback_and_complete_cleanup(runner, method):
    engine, peer, path = runner
    result = engine.file_probe(method)
    assert result["method"] == method and result["outcome"] == "verified" and result["cleanup"] == "verified"
    assert not peer.data and not engine.owned
    assert all(url.startswith(BASE + "method-probe-") for _, url, _ in peer.calls)
    assert json.loads(path.read_text().splitlines()[-1])["phase"] == "verified"


@pytest.mark.parametrize("method", ["COPY", "MOVE"])
def test_destination_race_never_overwrites_or_deletes_foreign_data(runner, method):
    engine, peer, _ = runner
    peer.destination_race = True
    with pytest.raises(Inconclusive, match="new destination"):
        engine.file_probe(method)
    assert any(body == b"synthetic other writer" for body, _ in peer.data.values())
    assert all(method != "DELETE" for method, _, _ in peer.calls)


def test_move_must_verify_original_absence_before_claiming_success(runner):
    engine, peer, _ = runner
    peer.move_keeps_source = True
    with pytest.raises(Inconclusive, match="absent"):
        engine.file_probe("MOVE")
    assert len(peer.data) == 2
    assert all(method != "DELETE" for method, _, _ in peer.calls)


@pytest.mark.parametrize("body_kind", ["echo", "generic", "nonce-only", "request-line-only"])
def test_trace_requires_the_fresh_nonce_and_the_request_line(tmp_path, roe, body_kind):
    tmp_path.chmod(0o700)
    peer = Peer()

    def respond(method, url, **kwargs):
        assert method == "TRACE" and url == TARGET
        nonce = kwargs["headers"]["X-Pentest-Nonce"].encode()
        bodies = {
            "echo": b"TRACE /app HTTP/1.1\r\nX-Pentest-Nonce: " + nonce,
            "generic": b"synthetic generic page",
            "nonce-only": nonce,
            "request-line-only": b"TRACE /app HTTP/1.1",
        }
        return Response(200, bodies[body_kind])

    peer.request = respond
    ledger = Ledger(tmp_path / "trace.jsonl")
    try:
        engine = FixtureRunner(peer, permission(tmp_path, roe, ["TRACE"]), ledger, 1)
        if body_kind == "echo":
            result = engine.trace_probe()
            assert result["outcome"] == "verified" and result["proof"] == "request-line-and-nonce-echo"
        else:
            with pytest.raises(Inconclusive, match="nonce"):
                engine.trace_probe()
    finally:
        ledger.close()


def proxy_roe(roe):
    proxy = "http://proxy.example.test:8080/"
    destination = "https://controlled.example.test/proof"
    roe["in_scope_targets"] += [proxy, "https://controlled.example.test/"]
    roe["http_method_probe"].update(
        {
            "target": proxy,
            "allowed_methods": ["CONNECT"],
            "unexpected_methods": [],
            "proxy_destination": destination,
            "controlled_proxy_destination": True,
            "proxy_response_sha256": hashlib.sha256(b"synthetic controlled fixture").hexdigest(),
        }
    )
    return proxy, destination


@pytest.mark.parametrize(
    "status,body,valid",
    [
        (200, b"synthetic controlled fixture", True),
        (200, b"synthetic generic page", False),
        (302, b"synthetic controlled fixture", False),
        (403, b"synthetic controlled fixture", False),
    ],
)
def test_connect_uses_only_approved_https_destination_and_verified_tls(tmp_path, roe, status, body, valid):
    tmp_path.chmod(0o700)
    proxy, destination = proxy_roe(roe)
    grant = permission(tmp_path, roe, ["CONNECT"], proxy)
    peer = Peer()
    calls = []

    def respond(method, url, **kwargs):
        calls.append((method, url))
        assert method == "GET" and url == destination
        assert kwargs["proxies"] == {"https": proxy}
        assert kwargs["verify"] is True and kwargs["allow_redirects"] is False and kwargs["stream"] is True
        assert peer.trust_env is False and peer.auth is None and not peer.cookies
        return Response(status, body)

    peer.request = respond
    ledger = Ledger(tmp_path / "proxy.jsonl")
    try:
        engine = FixtureRunner(peer, grant, ledger, 1)
        if valid:
            result = engine.connect_probe()
            assert result["proof"] == "verified-TLS-controlled-destination"
        else:
            with pytest.raises(Inconclusive):
                engine.connect_probe()
        assert calls == [("GET", destination)]
        events = [json.loads(line) for line in (tmp_path / "proxy.jsonl").read_text().splitlines()]
        assert any(e.get("phase") == "response" and e.get("status") == status for e in events)
        assert body.decode() not in (tmp_path / "proxy.jsonl").read_text()
    finally:
        ledger.close()


@pytest.mark.parametrize(
    "field,value",
    [
        ("proxy_destination", "http://controlled.example.test/proof"),
        ("proxy_destination", "https://outside.example.test/proof"),
        ("controlled_proxy_destination", "true"),
        ("proxy_response_sha256", "not-a-digest"),
    ],
)
def test_connect_permission_rejects_unsupported_or_unattested_destinations(tmp_path, roe, field, value):
    proxy, _ = proxy_roe(roe)
    roe["http_method_probe"][field] = value
    with pytest.raises(ValueError):
        permission(tmp_path, roe, ["CONNECT"], proxy)


def test_allowed_but_unselected_connect_cannot_use_unvalidated_destination(runner):
    engine, peer, _ = runner
    engine.permission["allowed_methods"].append("CONNECT")
    engine.permission["proxy_destination"] = "https://outside.example.test/"
    with pytest.raises(Inconclusive, match="permission"):
        engine.connect_probe()
    assert peer.calls == []


def test_target_404_does_not_authorize_creation_at_the_supplied_target(runner):
    engine, peer, _ = runner
    engine.absent(TARGET)
    before = len(peer.calls)
    with pytest.raises(Inconclusive, match="never the supplied target"):
        engine.request("PUT", TARGET, data=b"synthetic", headers={"If-None-Match": "*"})
    assert len(peer.calls) == before and not peer.data


def test_target_404_cannot_make_it_a_copy_destination(runner):
    engine, peer, _ = runner
    source = engine.create()
    engine.absent(TARGET)
    before = len(peer.calls)
    with pytest.raises(Inconclusive, match="destination"):
        engine.request(
            "COPY", source, headers={"If-Match": engine.owned[source][1], "Destination": TARGET, "Overwrite": "F"}
        )
    assert len(peer.calls) == before and TARGET not in peer.data


@pytest.mark.parametrize(
    "status,body,outcome",
    [
        (200, b"synthetic approved debug fixture", "verified"),
        (200, b"generic success page", "inconclusive"),
        (302, b"synthetic approved debug fixture", "inconclusive"),
        (500, b"synthetic approved debug fixture", "inconclusive"),
        (403, b"access denied", "rejected"),
        (405, b"method not allowed", "rejected"),
    ],
)
def test_debug_requires_exact_approved_fixture_not_success_status(tmp_path, roe, status, body, outcome):
    tmp_path.chmod(0o700)
    roe["http_method_probe"]["allowed_methods"] = ["DEBUG"]
    roe["http_method_probe"]["unexpected_methods"] = []
    roe["http_method_probe"]["debug_response_sha256"] = hashlib.sha256(b"synthetic approved debug fixture").hexdigest()
    grant = permission(tmp_path, roe, ["DEBUG"])
    peer = Peer()
    calls = []

    def respond(method, url, **kwargs):
        calls.append((method, url))
        assert kwargs["allow_redirects"] is False and kwargs["stream"] is True
        return Response(status, body)

    peer.request = respond
    path = tmp_path / "debug.jsonl"
    ledger = Ledger(path)
    try:
        engine = FixtureRunner(peer, grant, ledger, 1)
        if outcome == "inconclusive":
            with pytest.raises(Inconclusive):
                engine.debug_probe()
        else:
            assert engine.debug_probe()["outcome"] == outcome
        assert calls == [("DEBUG", TARGET)]
        assert body.decode() not in path.read_text()
    finally:
        ledger.close()


def test_debug_missing_fixture_permission_never_sends_request(runner):
    engine, peer, _ = runner
    with pytest.raises(Inconclusive, match="digest"):
        engine.debug_probe()
    assert peer.calls == []


def test_allowed_but_unselected_debug_never_sends_request(runner):
    engine, peer, _ = runner
    engine.permission["allowed_methods"].append("DEBUG")
    engine.permission["debug_response_sha256"] = hashlib.sha256(b"synthetic").hexdigest()
    with pytest.raises(Inconclusive, match="selected"):
        engine.debug_probe()
    assert peer.calls == []


DAV_FIXTURE = (
    b'<d:multistatus xmlns:d="DAV:"><d:response><d:href>/app</d:href>'
    b"<d:propstat><d:prop><d:resourcetype/></d:prop>"
    b"<d:status>HTTP/1.1 200 OK</d:status></d:propstat></d:response></d:multistatus>"
)


@pytest.mark.parametrize(
    "status,body,valid",
    [
        (207, DAV_FIXTURE, True),
        (200, DAV_FIXTURE, False),
        (207, b"generic success", False),
        (207, DAV_FIXTURE.replace(b"/app", b"/other"), False),
        (207, DAV_FIXTURE.replace(b"/app", b"https://outside.example.test/app"), False),
        (207, DAV_FIXTURE.replace(b"200 OK", b"403 Forbidden"), False),
        (207, DAV_FIXTURE.replace(b"DAV:", b"urn:fake"), False),
        (207, DAV_FIXTURE.replace(b"<d:resourcetype/>", b""), False),
        (207, b'<!DOCTYPE x [<!ENTITY a "synthetic">]>' + DAV_FIXTURE, False),
        (207, DAV_FIXTURE.decode().encode("utf-16"), False),
        (207, DAV_FIXTURE.replace(b"</d:multistatus>", b"<d:response/></d:multistatus>"), False),
    ],
)
def test_propfind_requires_exact_depth_zero_dav_property_evidence(tmp_path, roe, status, body, valid):
    tmp_path.chmod(0o700)
    roe["http_method_probe"]["allowed_methods"] = ["PROPFIND"]
    roe["http_method_probe"]["unexpected_methods"] = []
    grant = permission(tmp_path, roe, ["PROPFIND"])
    peer = Peer()
    calls = []

    def respond(method, url, **kwargs):
        calls.append((method, url))
        assert kwargs["headers"]["Depth"] == "0"
        assert b"resourcetype" in kwargs["data"]
        assert kwargs["allow_redirects"] is False
        return Response(status, body)

    peer.request = respond
    path = tmp_path / "dav.jsonl"
    ledger = Ledger(path)
    try:
        engine = FixtureRunner(peer, grant, ledger, 1)
        if valid:
            assert engine.propfind_probe()["proof"] == "depth-zero-exact-resource-property"
        else:
            with pytest.raises(Inconclusive):
                engine.propfind_probe()
        assert calls == [("PROPFIND", TARGET)]
        assert "<d:" not in path.read_text()
    finally:
        ledger.close()


class CollectionPeer(Peer):
    """In-memory DAV peer with independent failure and concurrency switches."""

    def __init__(self, failure=None):
        super().__init__()
        self.failure = failure
        self.exists = False
        self.locked = False
        self.inspections = 0
        self.token = "<opaquelocktoken:synthetic-collection-lock>"

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        assert url.startswith(BASE) and url.endswith("/")
        assert kwargs["allow_redirects"] is False and kwargs["stream"] is True
        headers = kwargs.get("headers", {})
        if method == "HEAD":
            return Response(200 if self.exists else 404)
        if method == "MKCOL":
            assert not self.exists and headers["If-None-Match"] == "*"
            self.exists = True
            if self.failure == "lost-create-ack":
                raise OSError("synthetic acknowledgement loss")
            return Response(201)
        if method == "PROPFIND":
            self.inspections += 1
            assert headers["Depth"] == "1"
            body = (
                '<d:multistatus xmlns:d="DAV:"><d:response><d:href>' + url + "</d:href>"
                "<d:propstat><d:prop><d:resourcetype><d:collection/></d:resourcetype>"
                '<d:getetag>"synthetic-v1"</d:getetag></d:prop>'
                "<d:status>HTTP/1.1 200 OK</d:status></d:propstat></d:response>"
            )
            if self.failure == "children-before-lock" or self.failure == "children-after-lock" and self.locked:
                body += "<d:response><d:href>" + url + "foreign-child</d:href></d:response>"
            body += "</d:multistatus>"
            if self.failure == "weak-etag":
                body = body.replace('"synthetic-v1"', 'W/"synthetic-v1"')
            if self.failure == "not-collection":
                body = body.replace("<d:collection/>", "")
            return Response(207, body.encode())
        if method == "LOCK":
            assert self.exists and headers["If-Match"] == '"synthetic-v1"'
            assert headers["Depth"] == "infinity" and headers["Timeout"] == "Second-60"
            if self.failure == "lock-unsupported":
                return Response(405)
            if self.failure == "lost-lock-ack":
                raise OSError("synthetic lock acknowledgement loss")
            nonce = ET.fromstring(kwargs["data"]).findtext("{DAV:}owner")
            self.locked = True
            body = (
                '<d:prop xmlns:d="DAV:"><d:lockdiscovery><d:activelock>'
                "<d:lockscope><d:exclusive/></d:lockscope><d:locktype><d:write/></d:locktype>"
                "<d:depth>infinity</d:depth><d:owner>" + nonce + "</d:owner>"
                "<d:timeout>Second-60</d:timeout><d:locktoken><d:href>" + self.token[1:-1] + "</d:href></d:locktoken>"
                "<d:lockroot><d:href>" + url + "</d:href></d:lockroot>"
                "</d:activelock></d:lockdiscovery></d:prop>"
            )
            replacements = {
                "shared-lock": ("exclusive", "shared"),
                "shallow-lock": (">infinity<", ">0<"),
                "long-lock": ("Second-60", "Second-600"),
                "infinite-lock": ("Second-60", "Infinite"),
                "wrong-owner": (nonce, "foreign-owner"),
                "wrong-root": (url, TARGET),
                "wrong-token": (self.token[1:-1], "opaquelocktoken:other"),
                "xml-entity": ("<d:prop ", '<!DOCTYPE x [<!ENTITY a "bad">]><d:prop '),
            }
            if self.failure in replacements:
                body = body.replace(*replacements[self.failure])
            token = self.token if self.failure != "token-injection" else "<opaquelocktoken:x>\r\nX-Test:bad"
            return Response(200, body.encode(), {"Lock-Token": token})
        if method == "DELETE":
            assert self.locked and self.inspections == 2
            assert headers == {"If-Match": '"synthetic-v1"', "If": "(" + self.token + ")"}
            if self.failure == "cleanup-rejected":
                return Response(412)
            if self.failure == "lost-delete-ack":
                self.exists = False
                raise OSError("synthetic deletion acknowledgement loss")
            self.exists = False
            return Response(204)
        raise AssertionError("Unexpected method " + method)


def collection_permission(tmp_path, roe):
    roe["http_method_probe"]["allowed_methods"] = ["MKCOL", "DELETE", "PROPFIND", "LOCK"]
    roe["http_method_probe"]["unexpected_methods"] = []
    return permission(tmp_path, roe, ["MKCOL"])


def test_mkcol_verifies_empty_collection_under_exclusive_lock_before_cleanup(tmp_path, roe):
    tmp_path.chmod(0o700)
    ledger = Ledger(tmp_path / "collection.jsonl")
    peer = CollectionPeer()
    try:
        engine = FixtureRunner(peer, collection_permission(tmp_path, roe), ledger, 1)
        assert engine.collection_probe()["cleanup"] == "verified"
        assert [m for m, _, _ in peer.calls] == ["HEAD", "MKCOL", "PROPFIND", "LOCK", "PROPFIND", "DELETE", "HEAD"]
        assert not peer.exists and not engine.owned and not engine.collections
        assert peer.token not in (tmp_path / "collection.jsonl").read_text()
    finally:
        ledger.close()


@pytest.mark.parametrize(
    "failure",
    [
        "lost-create-ack",
        "children-before-lock",
        "children-after-lock",
        "weak-etag",
        "not-collection",
        "lock-unsupported",
        "lost-lock-ack",
        "shared-lock",
        "shallow-lock",
        "long-lock",
        "infinite-lock",
        "wrong-owner",
        "wrong-root",
        "wrong-token",
        "xml-entity",
        "token-injection",
        "cleanup-rejected",
        "lost-delete-ack",
    ],
)
def test_mkcol_ambiguity_stops_without_retry_or_unverified_recursive_delete(tmp_path, roe, failure):
    tmp_path.chmod(0o700)
    ledger = Ledger(tmp_path / "collection.jsonl")
    peer = CollectionPeer(failure)
    try:
        engine = FixtureRunner(peer, collection_permission(tmp_path, roe), ledger, 1)
        with pytest.raises(Inconclusive):
            engine.collection_probe()
        methods = [m for m, _, _ in peer.calls]
        assert methods.count("MKCOL") == 1
        assert methods.count("LOCK") <= 1 and methods.count("DELETE") <= 1
        assert methods.count("DELETE") == (1 if failure in {"cleanup-rejected", "lost-delete-ack"} else 0)
        assert "verified" not in [
            json.loads(line)["phase"] for line in (tmp_path / "collection.jsonl").read_text().splitlines()
        ]
    finally:
        ledger.close()


@pytest.mark.parametrize("helper", ["DELETE", "PROPFIND", "LOCK"])
def test_mkcol_requires_each_cleanup_and_inspection_helper_before_transport(tmp_path, roe, helper):
    collection_permission(tmp_path, roe)
    roe["http_method_probe"]["allowed_methods"].remove(helper)
    with pytest.raises(ValueError, match="helper"):
        permission(tmp_path, roe, ["MKCOL"])


def test_mkcol_expired_lock_stops_before_delete(tmp_path, roe, monkeypatch):
    from lib import method_probe

    tmp_path.chmod(0o700)
    clock = [0.0]
    monkeypatch.setattr(method_probe.time, "monotonic", lambda: clock[0])
    peer = CollectionPeer()
    respond = peer.request

    def expire_after_inspection(method, url, **kwargs):
        result = respond(method, url, **kwargs)
        if method == "PROPFIND" and peer.inspections == 2:
            clock[0] = 61.0
        return result

    peer.request = expire_after_inspection
    ledger = Ledger(tmp_path / "expired-lock.jsonl")
    try:
        engine = FixtureRunner(peer, collection_permission(tmp_path, roe), ledger, 1)
        with pytest.raises(Inconclusive, match="expired"):
            engine.collection_probe()
        assert peer.exists and all(m != "DELETE" for m, _, _ in peer.calls)
    finally:
        ledger.close()


def test_collection_cannot_be_deleted_using_only_a_file_etag(runner):
    engine, peer, _ = runner
    url = engine.create()
    engine.collections.add(url)
    before = len(peer.calls)
    with pytest.raises(Inconclusive, match="exclusive write lock"):
        engine.request("DELETE", url, headers={"If-Match": engine.owned[url][1]})
    assert len(peer.calls) == before and url in peer.data


def test_unselected_mkcol_cannot_create_any_resource(runner):
    engine, peer, _ = runner
    with pytest.raises(Inconclusive, match="selected"):
        engine.collection_probe()
    assert peer.calls == []


@pytest.fixture
def active_probe():
    script = Path(__file__).resolve().parents[1] / "skills/probing-dangerous-http-methods/scripts/probe_methods.py"
    spec = importlib.util.spec_from_file_location("active_method_cli", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("method", ["PUT", "DELETE", "COPY", "MOVE", "MKCOL"])
def test_actual_cli_write_opt_in_uses_only_disposable_resources(
    active_probe, tmp_path, roe, monkeypatch, capsys, method
):
    tmp_path.chmod(0o700)
    if method == "MKCOL":
        collection_permission(tmp_path, roe)
        peer = CollectionPeer()
    else:
        permission(tmp_path, roe, [method])
        peer = Peer()
    peer.close = lambda: None
    monkeypatch.setattr(active_probe, "make_session", lambda **kwargs: peer)
    result = active_probe.main(
        [
            TARGET,
            "--authorized",
            "--roe",
            str(tmp_path / "synthetic-roe.json"),
            "--active-method",
            method,
            "--ledger",
            str(tmp_path / "cli.jsonl"),
            "--format",
            "json",
        ]
    )
    assert result == (1 if method == "PUT" else 0)
    assert peer.calls and all(url.startswith(BASE) and url != TARGET for _, url, _ in peer.calls)
    assert method in [m for m, _, _ in peer.calls]
    findings = json.loads(capsys.readouterr().out)
    assert findings[0]["evidence"]["cleanup"] == "verified"


def test_actual_cli_policy_gate_survives_critical_display_filter(active_probe, tmp_path, roe, monkeypatch, capsys):
    tmp_path.chmod(0o700)
    permission(tmp_path, roe, ["PUT"])
    peer = Peer()
    peer.close = lambda: None
    monkeypatch.setattr(active_probe, "make_session", lambda **kwargs: peer)
    result = active_probe.main(
        [
            TARGET,
            "--authorized",
            "--roe",
            str(tmp_path / "synthetic-roe.json"),
            "--active-method",
            "PUT",
            "--ledger",
            str(tmp_path / "cli.jsonl"),
            "--format",
            "json",
            "--min-severity",
            "critical",
        ]
    )
    assert result == 1 and json.loads(capsys.readouterr().out) == []


def test_actual_cli_lost_write_ack_stops_remaining_selected_methods(active_probe, tmp_path, roe, monkeypatch, capsys):
    tmp_path.chmod(0o700)
    permission(tmp_path, roe, ["PUT", "MOVE"])
    peer = Peer()
    peer.fail_after_put = True
    peer.close = lambda: None
    monkeypatch.setattr(active_probe, "make_session", lambda **kwargs: peer)
    result = active_probe.main(
        [
            TARGET,
            "--authorized",
            "--roe",
            str(tmp_path / "synthetic-roe.json"),
            "--active-method",
            "PUT",
            "--active-method",
            "MOVE",
            "--ledger",
            str(tmp_path / "cli.jsonl"),
            "--format",
            "json",
            "--min-severity",
            "critical",
        ]
    )
    assert result == 2 and json.loads(capsys.readouterr().out) == []
    assert [m for m, _, _ in peer.calls] == ["HEAD", "PUT"]
    assert peer.data


@pytest.mark.parametrize(
    "failure",
    [
        "missing-roe",
        "bad-roe",
        "no-attestation",
        "unapproved-method",
        "existing-ledger",
        "is-api",
        "ledger-is-output",
        "output-alias",
    ],
)
def test_actual_cli_rejects_bad_active_contract_before_session_creation(
    active_probe, tmp_path, roe, monkeypatch, failure
):
    tmp_path.chmod(0o700)
    permission(tmp_path, roe, ["PUT"])
    ledger = tmp_path / "cli.jsonl"
    args = [
        TARGET,
        "--active-method",
        "PUT",
        "--authorized",
        "--roe",
        str(tmp_path / "synthetic-roe.json"),
        "--ledger",
        str(ledger),
    ]
    if failure == "missing-roe":
        index = args.index("--roe")
        del args[index : index + 2]
    elif failure == "bad-roe":
        (tmp_path / "synthetic-roe.json").write_text("{}")
    elif failure == "no-attestation":
        args.remove("--authorized")
    elif failure == "unapproved-method":
        args[args.index("PUT")] = "CONNECT"
    elif failure == "existing-ledger":
        ledger.write_text("prior evidence")
    elif failure == "ledger-is-output":
        args.extend(["--output", str(ledger)])
    elif failure == "output-alias":
        alias = tmp_path / "report.json"
        alias.symlink_to(ledger)
        args.extend(["--output", str(alias)])
    else:
        args.append("--is-api")
    calls = []
    monkeypatch.setattr(active_probe, "make_session", lambda **kwargs: calls.append(kwargs))
    with pytest.raises(SystemExit) as error:
        active_probe.main(args)
    assert error.value.code == 2 and calls == []
    if failure == "existing-ledger":
        assert ledger.read_text() == "prior evidence"


@pytest.mark.parametrize("method", ["TRACE", "DEBUG", "PROPFIND", "CONNECT"])
def test_actual_cli_dispatches_readlike_and_controlled_proxy_adapters(
    active_probe, tmp_path, roe, monkeypatch, capsys, method
):
    tmp_path.chmod(0o700)
    target = TARGET
    fixture = b"synthetic controlled fixture"
    if method == "CONNECT":
        target, destination = proxy_roe(roe)
    else:
        roe["http_method_probe"]["allowed_methods"] = [method]
        roe["http_method_probe"]["unexpected_methods"] = []
        if method == "DEBUG":
            roe["http_method_probe"]["debug_response_sha256"] = hashlib.sha256(fixture).hexdigest()
    permission(tmp_path, roe, [method], target)
    peer = Peer()
    calls = []

    def respond(verb, url, **kwargs):
        calls.append((verb, url))
        assert peer.trust_env is False and peer.auth is None and not peer.cookies
        assert kwargs["allow_redirects"] is False and kwargs["stream"] is True
        if method == "CONNECT":
            assert (verb, url) == ("GET", destination)
            assert kwargs["verify"] is True and kwargs["proxies"] == {"https": target}
            return Response(200, fixture)
        assert (verb, url) == (method, target)
        if method == "TRACE":
            return Response(
                200, ("TRACE /app HTTP/1.1\r\nX-Pentest-Nonce: " + kwargs["headers"]["X-Pentest-Nonce"]).encode()
            )
        if method == "PROPFIND":
            assert kwargs["headers"]["Depth"] == "0"
            return Response(207, DAV_FIXTURE)
        return Response(200, fixture)

    peer.request = respond
    peer.close = lambda: None
    monkeypatch.setattr(active_probe, "make_session", lambda **kwargs: peer)
    result = active_probe.main(
        [
            target,
            "--authorized",
            "--roe",
            str(tmp_path / "synthetic-roe.json"),
            "--active-method",
            method,
            "--ledger",
            str(tmp_path / "cli.jsonl"),
            "--format",
            "json",
        ]
    )
    assert result == 0 and len(calls) == 1
    assert json.loads(capsys.readouterr().out)[0]["evidence"]["outcome"] == "verified"


def test_ledger_parent_symlink_is_rejected_without_creating_file(tmp_path):
    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    alias = tmp_path / "alias"
    alias.symlink_to(private, target_is_directory=True)
    with pytest.raises(OSError):
        Ledger(alias / "operations.jsonl")
    assert not list(private.iterdir())


def test_ledger_pins_verified_directory_across_parent_path_replacement(tmp_path, monkeypatch):
    from lib import method_probe

    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    held = tmp_path / "verified-original"
    original_open = method_probe.os.open
    replaced = []

    def replace_parent_before_leaf(path, flags, mode=0o600, **kwargs):
        if Path(path).name == "operations.jsonl":
            assert isinstance(kwargs.get("dir_fd"), int)
            private.rename(held)
            private.mkdir(mode=0o700)
            replaced.append(True)
        return original_open(path, flags, mode, **kwargs)

    monkeypatch.setattr(method_probe.os, "open", replace_parent_before_leaf)
    ledger = Ledger(private / "operations.jsonl")
    ledger.close()
    assert replaced == [True] and not (private / "operations.jsonl").exists()
    assert stat.S_IMODE((held / "operations.jsonl").stat().st_mode) == 0o600
    assert json.loads((held / "operations.jsonl").read_text())["phase"] == "started"
