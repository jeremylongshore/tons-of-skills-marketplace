#!/usr/bin/env python3
"""Bounded HTTP method discovery and explicit owner-approved fixture probes.

Default operation is anonymous OPTIONS discovery only. Active methods require
separate ROE permission, explicit selection and an exclusive private ledger.
A verified capability is a policy violation only when the owner attests that it
is unexpected. Status codes alone do not establish exploitation or compliance.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parents[3]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib.authz_check import require_authorization  # noqa: E402
from lib.engagement import classify_target  # noqa: E402
from lib.finding import Finding, Severity  # noqa: E402
from lib.http_client import make_session  # noqa: E402
from lib.method_probe import ACTIVE_METHODS, FixtureRunner, Inconclusive, Ledger, validate_permission  # noqa: E402
from lib.report import emit, exit_code  # noqa: E402

SKILL_ID = "probing-dangerous-http-methods"


def _grade_response(
    method: str, resp, expected_fail: set, severity: Severity, title: str, target: str, is_xst: bool = False
) -> list[Finding]:
    if resp is None:
        return [_observation(method, target, "inconclusive", "No response evidence was obtained.")]
    if resp.status_code in (401, 403):
        return [
            _observation(
                method, target, "access-controlled", "The request was rejected by an access control.", resp.status_code
            )
        ]
    if 300 <= resp.status_code < 400:
        return [
            _observation(
                method, target, "inconclusive", "A redirect was returned and was not followed.", resp.status_code
            )
        ]
    if resp.status_code in (405, 501):
        return [
            _observation(
                method,
                target,
                "rejected",
                "This request was rejected; this does not establish policy on other resources.",
                resp.status_code,
            )
        ]
    if resp.status_code in expected_fail:
        return [
            _observation(
                method,
                target,
                "inconclusive",
                "The status does not establish whether this method is implemented.",
                resp.status_code,
            )
        ]
    if resp.status_code >= 500:
        return [
            Finding(
                skill_id=SKILL_ID,
                title=f"{method} returns {resp.status_code} (error handling concern)",
                severity=Severity.INFO,
                target=target,
                detail=(
                    f"The {method} method returned {resp.status_code}. "
                    "The response alone does not establish implementation, "
                    "a crash, or an exposed capability."
                ),
                remediation="Inspect the scoped error and intended method policy before changing server configuration.",
                evidence=(("method", method), ("outcome", "inconclusive"), ("status_code", resp.status_code)),
            )
        ]
    # Active capability findings need a verified request/response fixture, not
    # the status-only heuristic used by the historical implementation.
    return [
        _observation(
            method,
            target,
            "inconclusive",
            "A status alone does not demonstrate the method's effect or an exploit.",
            resp.status_code,
        )
    ]


def _observation(method: str, target: str, outcome: str, detail: str, status: int | None = None) -> Finding:
    evidence = (("method", method), ("outcome", outcome))
    if status is not None:
        evidence += (("status_code", status),)
    return Finding(
        skill_id=SKILL_ID,
        title=f"{method}: {outcome}",
        severity=Severity.INFO,
        target=target,
        detail=detail,
        remediation="Review the scoped response and the approved method policy; untested capability is not a clean security verdict.",
        evidence=evidence,
    )


def _check_options(sess, url: str, timeout: float, target: str) -> list[Finding]:
    try:
        resp = sess.options(url, timeout=timeout, allow_redirects=False, stream=True)
    except Exception:
        return [
            _observation(
                "OPTIONS", target, "inconclusive", "The discovery request failed; no capability evidence was obtained."
            )
        ]
    if resp is None:
        return [_observation("OPTIONS", target, "inconclusive", "The discovery request produced no response.")]
    try:
        status = resp.status_code
        if not 200 <= status < 300:
            label = "access-controlled" if status in (401, 403) else "inconclusive"
            return [
                _observation(
                    "OPTIONS",
                    target,
                    label,
                    "Discovery was rejected or redirected. No redirect was followed and no other method was tested.",
                    status,
                )
            ]
        allow = resp.headers.get("Allow", "")
        if not isinstance(allow, str) or not allow.strip() or len(allow) > 1024:
            return [
                _observation(
                    "OPTIONS",
                    target,
                    "inconclusive",
                    "A bounded Allow header was not available; enabled methods remain unknown.",
                    status,
                )
            ]
        methods = [m.strip().upper() for m in allow.split(",")]
        if any(
            not m
            or len(m) > 32
            or not all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&'*+-.^_`|~" for c in m)
            or m == "*"
            for m in methods
        ):
            return [
                _observation(
                    "OPTIONS",
                    target,
                    "inconclusive",
                    "The Allow header has unsupported or malformed method tokens.",
                    status,
                )
            ]
        return [
            Finding(
                skill_id=SKILL_ID,
                title="OPTIONS advertised method observation",
                severity=Severity.INFO,
                target=target,
                detail="The server advertises these methods. Advertisement does not demonstrate access, write effects, proxying, or XST; no active capability was tested.",
                remediation="Compare the advertised list with the owner-approved policy before planning active verification.",
                evidence=(
                    ("method", "OPTIONS"),
                    ("outcome", "observed"),
                    ("status_code", status),
                    ("advertised_methods", tuple(sorted(set(methods)))),
                ),
            )
        ]
    finally:
        resp.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="OPTIONS discovery and explicitly scoped disposable method experiments"
    )
    parser.add_argument("url")
    parser.add_argument("--authorized", action="store_true")
    parser.add_argument("--output", default=None)
    parser.add_argument("--format", choices=("json", "jsonl", "markdown"), default="markdown")
    parser.add_argument("--min-severity", choices=("critical", "high", "medium", "low", "info"), default="info")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument(
        "--is-api", action="store_true", help="Legacy discovery-only hint; cannot override active ROE policy"
    )
    parser.add_argument("--active-method", action="append", choices=sorted(ACTIVE_METHODS), default=[])
    parser.add_argument("--roe", type=Path, help="Owner-approved ROE with exact method and fixture permission")
    parser.add_argument("--ledger", type=Path, help="New exclusive ledger in an existing private directory")
    args = parser.parse_args(argv)

    if not math.isfinite(args.timeout) or not 0 < args.timeout <= 30:
        parser.error("--timeout must be finite and greater than zero, at most 30 seconds")
    _, kind, normalized = classify_target(args.url)
    if kind != "url" or normalized is None:
        parser.error(
            "URL must be an explicit HTTP(S) target without credentials, queries, fragments or ambiguous paths"
        )

    require_authorization(args.url, args.authorized)

    ledger = None
    grant = None
    if args.active_method:
        if not args.authorized or args.roe is None or args.ledger is None:
            parser.error("Active probes require --authorized, --roe and a new --ledger")
        if args.is_api:
            parser.error("--is-api cannot override active ROE policy; use attested unexpected_methods")
        try:
            if args.output is not None and Path(args.output).resolve() == args.ledger.resolve():
                parser.error("--output must not overwrite the private operation ledger")
            grant = validate_permission(args.roe, normalized, args.active_method)
            ledger = Ledger(args.ledger)
        except (ValueError, OSError) as exc:
            parser.error("Active probe permission or private ledger validation failed: " + type(exc).__name__)
    elif args.roe is not None or args.ledger is not None:
        parser.error("--roe and --ledger require explicit --active-method selection")

    try:
        sess = make_session(timeout=args.timeout)
    except Exception:
        if ledger is not None:
            ledger.close()
        raise
    # Discovery is anonymous and direct: do not inherit netrc credentials,
    # ambient proxies, or response cookies into a subsequent operation.
    sess.trust_env = False
    sess.auth = None
    sess.headers.pop("Authorization", None)
    sess.cookies.clear()
    target = args.url
    findings: list[Finding] = []
    gate = 0

    try:
        if grant is None:
            findings.extend(_check_options(sess, normalized, args.timeout, target))
            incomplete = any(dict(f.evidence).get("outcome") != "observed" for f in findings)
            gate = 2 if incomplete else exit_code(findings)
        else:
            runner = FixtureRunner(sess, grant, ledger, args.timeout)
            for method in args.active_method:
                try:
                    if method in {"PUT", "DELETE", "COPY", "MOVE"}:
                        result = runner.file_probe(method)
                    else:
                        adapter = {
                            "MKCOL": runner.collection_probe,
                            "TRACE": runner.trace_probe,
                            "CONNECT": runner.connect_probe,
                            "DEBUG": runner.debug_probe,
                            "PROPFIND": runner.propfind_probe,
                        }[method]
                        result = adapter()
                except (Inconclusive, OSError) as exc:
                    findings.append(
                        _observation(
                            method,
                            target,
                            "inconclusive",
                            str(exc)
                            if isinstance(exc, Inconclusive)
                            else "Private ledger persistence failed; reconcile before any further request.",
                        )
                    )
                    gate = 2
                    break
                violation = result["outcome"] == "verified" and method in grant.get("unexpected_methods", [])
                findings.append(
                    Finding(
                        skill_id=SKILL_ID,
                        title=f"{method}: {'owner-policy violation' if violation else result['outcome']}",
                        severity=Severity.HIGH if violation else Severity.INFO,
                        target=target,
                        detail="Bounded anonymous fixture verification; this result does not establish browser exploitation, arbitrary proxying or compliance.",
                        remediation="Compare the bounded capability with the owner-approved method policy; preserve the private ledger.",
                        evidence=tuple(result.items()),
                    )
                )
                if violation:
                    gate = 1
    finally:
        sess.close()
        if ledger is not None:
            ledger.close()

    floor = Severity(args.min_severity)
    findings = [f for f in findings if f.severity.numeric >= floor.numeric]

    emit(findings, args.output, args.format, target)
    return gate


if __name__ == "__main__":
    sys.exit(main())
