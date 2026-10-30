"""Actual CLI probes use fake sessions only; no HTTP, DNS or target fixtures."""

import importlib.util
import json
from pathlib import Path

import pytest

PACK = Path(__file__).resolve().parents[1]


@pytest.fixture
def probe():
    path = PACK / "skills/probing-dangerous-http-methods/scripts/probe_methods.py"
    spec = importlib.util.spec_from_file_location("method_probe_safety", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Response:
    def __init__(self, status=200, allow="GET, HEAD, OPTIONS, PUT, DELETE, TRACE"):
        self.status_code = status
        self.headers = {} if allow is None else {"Allow": allow}
        self.closed = False
        self.allow_body = False

    @property
    def content(self):
        if self.allow_body:
            return b""
        raise AssertionError("OPTIONS discovery must not download a response body")

    @property
    def text(self):
        if self.allow_body:
            return ""
        raise AssertionError("OPTIONS discovery must not download a response body")

    def close(self):
        self.closed = True


class Session:
    def __init__(self, response):
        self.response = response
        self.calls = []
        self.headers = {"Authorization": "synthetic ambient header"}
        self.cookies = {"synthetic": "ambient"}
        self.trust_env = True
        self.auth = "synthetic ambient auth"
        self.closed = False

    def request(self, method, *args, **kwargs):
        self.calls.append((method, args, kwargs))
        raise AssertionError(f"Unapproved method invoked: {method}")

    def options(self, url, **kwargs):
        self.calls.append(("OPTIONS", url, kwargs))
        assert self.trust_env is False
        assert self.auth is None
        assert "Authorization" not in self.headers
        assert not self.cookies
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    def close(self):
        self.closed = True


def invoke(probe, monkeypatch, response, *extra):
    session = Session(response)
    monkeypatch.setattr(probe, "make_session", lambda **kwargs: session)
    result = probe.main(["https://fixture.example.test/a", "--authorized", "--format", "json", *extra])
    return result, session


def test_default_performs_only_anonymous_bounded_options(probe, monkeypatch, capsys):
    response = Response()
    result, session = invoke(probe, monkeypatch, response)
    assert result == 0
    assert session.calls == [
        (
            "OPTIONS",
            "https://fixture.example.test/a",
            {
                "timeout": 10.0,
                "allow_redirects": False,
                "stream": True,
            },
        )
    ]
    assert response.closed and session.closed
    findings = json.loads(capsys.readouterr().out)
    assert len(findings) == 1
    assert findings[0]["severity"] == "info"
    assert findings[0]["evidence"]["advertised_methods"] == ["DELETE", "GET", "HEAD", "OPTIONS", "PUT", "TRACE"]
    assert "no active capability was tested" in findings[0]["detail"]


@pytest.mark.parametrize(
    "response",
    [
        None,
        OSError("synthetic failure"),
        Response(302),
        Response(401),
        Response(403),
        Response(404),
        Response(405),
        Response(500),
        Response(200, None),
        Response(200, "*"),
        Response(200, "GET,,PUT"),
    ],
)
def test_missing_or_inconclusive_evidence_fails_before_display_filter(probe, monkeypatch, capsys, response):
    result, session = invoke(probe, monkeypatch, response, "--min-severity", "critical")
    assert result == 2
    assert json.loads(capsys.readouterr().out) == []
    assert len(session.calls) == 1 and session.closed


@pytest.mark.parametrize("timeout", ["nan", "inf", "-1", "0", "31"])
def test_invalid_timeout_prevents_session_creation(probe, monkeypatch, timeout):
    monkeypatch.setattr(probe, "make_session", lambda **kwargs: pytest.fail("Session created"))
    with pytest.raises(SystemExit) as exc:
        probe.main(["https://fixture.example.test", "--authorized", "--timeout", timeout])
    assert exc.value.code == 2


@pytest.mark.parametrize("status", [200, 302, 401, 403, 404, 500])
def test_status_alone_does_not_prove_trace_or_proxy_capability(probe, status):
    for method in ("TRACE", "CONNECT"):
        response = Response(status)
        response.allow_body = True
        findings = probe._grade_response(
            method,
            response,
            {403, 404, 405},
            probe.Severity.HIGH,
            "historical claim",
            "synthetic target",
            is_xst=method == "TRACE",
        )
        assert findings and all(f.severity is probe.Severity.INFO for f in findings)
        assert all("HttpOnly" not in f.detail and "XHR" not in f.detail for f in findings)
