"""
HTTP Security Scanner - Automated web application security assessment tool.

Performs authorized active HTTP/TLS checks against a target URL including:
- Security header analysis (CSP, HSTS, X-Frame-Options, etc.)
- SSL/TLS certificate validation and expiry checking
- Common path exposure probing (git, env, admin panels)
- Bounded OPTIONS method-advertisement inspection (no write-method probes)
- CORS policy analysis and misconfiguration detection

Usage:
    python3 security_scanner.py https://example.com
    python3 security_scanner.py https://example.com --output report.json
    python3 security_scanner.py https://example.com --checks headers,ssl,cors
    python3 security_scanner.py https://example.com --timeout 15 --verbose

This tool is intended for authorized security testing only. Always obtain
written permission before scanning any target you do not own.

Requires: Python 3.9+, requests library
"""

from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print(
        "Error: 'requests' library is required. Install with: pip install requests",
        file=sys.stderr,
    )
    sys.exit(2)

__version__ = "2.0.0"

USER_AGENT = "SecurityScanner/2.0 (authorized-testing)"

SEVERITY_WEIGHTS = {
    "critical": 25,
    "high": 15,
    "medium": 8,
    "low": 3,
    "info": 0,
}

ALL_CHECKS = ["headers", "ssl", "endpoints", "methods", "cors"]


@dataclass
class Finding:
    """A single security finding from a scan check."""

    check: str
    severity: str
    title: str
    detail: str
    remediation: str

    def __post_init__(self) -> None:
        valid = ("critical", "high", "medium", "low", "info")
        if self.severity not in valid:
            raise ValueError(f"Invalid severity '{self.severity}', must be one of {valid}")


@dataclass
class ScanResult:
    """Aggregated results from all scan checks."""

    target: str
    scan_start: str
    scan_end: str = ""
    duration_seconds: float = 0.0
    checks_performed: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class CheckIncomplete(Exception):
    """A selected check failed; preserve any partial findings without a clean verdict."""

    def __init__(self, message: str, findings=None):
        super().__init__(message)
        self.findings = list(findings or [])


def _log(message: str, verbose: bool = True) -> None:
    """Print a status message to stderr."""
    if verbose:
        print(f"[*] {message}", file=sys.stderr)


def _log_error(message: str) -> None:
    """Print an error message to stderr."""
    print(f"[!] {message}", file=sys.stderr)


def create_session(timeout: int = 10) -> requests.Session:
    """Create a requests session with retry logic and custom headers."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    )

    retry_strategy = Retry(
        total=2,
        backoff_factor=0.5,
        status_forcelist=[502, 503, 504],
        allowed_methods=["GET", "HEAD", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # Store timeout on session for convenience; callers pass it per-request
    session.timeout = timeout  # type: ignore[attr-defined]
    return session


# ---------------------------------------------------------------------------
# Check 1: Security Headers
# ---------------------------------------------------------------------------


def scan_security_headers(url: str, session: requests.Session) -> list[Finding]:
    """Analyze HTTP response security headers for misconfigurations and missing headers."""
    findings: list[Finding] = []
    timeout: int = getattr(session, "timeout", 10)

    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
    except requests.RequestException as _transport_error:
        raise CheckIncomplete(
            "Selected scan_security_headers request failed: " + type(_transport_error).__name__, findings
        ) from _transport_error

    headers = resp.headers

    # --- Content-Security-Policy ---
    csp = headers.get("Content-Security-Policy")
    if not csp:
        findings.append(
            Finding(
                check="headers",
                severity="high",
                title="Missing Content-Security-Policy header",
                detail="No CSP header was found in the response. This leaves the application "
                "vulnerable to cross-site scripting and data injection attacks.",
                remediation="Implement a Content-Security-Policy header. Start with a restrictive "
                "policy such as \"default-src 'self'\" and expand as needed.",
            )
        )
    else:
        if "'unsafe-inline'" in csp:
            findings.append(
                Finding(
                    check="headers",
                    severity="medium",
                    title="CSP allows unsafe-inline",
                    detail=f"The Content-Security-Policy contains 'unsafe-inline', which weakens "
                    f"XSS protections. Value: {csp[:200]}",
                    remediation="Replace 'unsafe-inline' with nonce-based or hash-based CSP directives.",
                )
            )
        if "'unsafe-eval'" in csp:
            findings.append(
                Finding(
                    check="headers",
                    severity="medium",
                    title="CSP allows unsafe-eval",
                    detail=f"The Content-Security-Policy contains 'unsafe-eval', allowing dynamic "
                    f"code execution. Value: {csp[:200]}",
                    remediation="Remove 'unsafe-eval' from CSP and refactor code to avoid eval().",
                )
            )
        if "default-src" not in csp and "script-src" not in csp:
            findings.append(
                Finding(
                    check="headers",
                    severity="medium",
                    title="CSP missing default-src or script-src directive",
                    detail="The CSP header does not define a default-src or script-src directive, "
                    "which may leave resource loading unrestricted.",
                    remediation="Add a 'default-src' directive as a fallback for all resource types.",
                )
            )

    # --- Strict-Transport-Security ---
    hsts = headers.get("Strict-Transport-Security")
    if not hsts:
        severity = "high" if url.startswith("https") else "medium"
        findings.append(
            Finding(
                check="headers",
                severity=severity,
                title="Missing Strict-Transport-Security (HSTS) header",
                detail="The server does not send an HSTS header. Clients may connect over "
                "insecure HTTP, enabling man-in-the-middle attacks.",
                remediation="Add the header: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
            )
        )
    else:
        hsts_lower = hsts.lower()
        # Check max-age value
        max_age_val = 0
        for part in hsts_lower.split(";"):
            part = part.strip()
            if part.startswith("max-age="):
                try:
                    max_age_val = int(part.split("=", 1)[1].strip())
                except ValueError:
                    max_age_val = 0
        if max_age_val < 31536000:
            findings.append(
                Finding(
                    check="headers",
                    severity="medium",
                    title="HSTS max-age is too short",
                    detail=f"HSTS max-age is {max_age_val} seconds (recommended minimum is "
                    f"31536000 / 1 year). Current value: {hsts}",
                    remediation="Set max-age to at least 31536000 (one year).",
                )
            )
        if "includesubdomains" not in hsts_lower:
            findings.append(
                Finding(
                    check="headers",
                    severity="low",
                    title="HSTS missing includeSubDomains directive",
                    detail=f"The HSTS header does not include the includeSubDomains directive. "
                    f"Subdomains may still be accessed over HTTP. Value: {hsts}",
                    remediation="Add 'includeSubDomains' to the HSTS header.",
                )
            )

    # --- X-Frame-Options ---
    xfo = headers.get("X-Frame-Options")
    if not xfo:
        # Only flag if CSP frame-ancestors is also missing
        if not csp or "frame-ancestors" not in (csp or ""):
            findings.append(
                Finding(
                    check="headers",
                    severity="medium",
                    title="Missing X-Frame-Options header",
                    detail="Neither X-Frame-Options nor CSP frame-ancestors is set. "
                    "The page may be embedded in frames, enabling clickjacking.",
                    remediation="Set X-Frame-Options to DENY or SAMEORIGIN, or use CSP frame-ancestors directive.",
                )
            )

    # --- X-Content-Type-Options ---
    xcto = headers.get("X-Content-Type-Options")
    if not xcto:
        findings.append(
            Finding(
                check="headers",
                severity="medium",
                title="Missing X-Content-Type-Options header",
                detail="Without this header, browsers may MIME-sniff responses, potentially "
                "interpreting files as executable content.",
                remediation="Set the header: X-Content-Type-Options: nosniff",
            )
        )
    elif xcto.strip().lower() != "nosniff":
        findings.append(
            Finding(
                check="headers",
                severity="medium",
                title="X-Content-Type-Options has unexpected value",
                detail=f"Expected 'nosniff' but got '{xcto}'. The header may not function correctly.",
                remediation="Set the value to exactly 'nosniff'.",
            )
        )

    # --- Referrer-Policy ---
    rp = headers.get("Referrer-Policy")
    if not rp:
        findings.append(
            Finding(
                check="headers",
                severity="low",
                title="Missing Referrer-Policy header",
                detail="Without a Referrer-Policy, the browser sends the full URL as referrer "
                "to other sites, potentially leaking sensitive URL parameters.",
                remediation="Set Referrer-Policy to 'strict-origin-when-cross-origin' or 'no-referrer'.",
            )
        )

    # --- Permissions-Policy ---
    pp = headers.get("Permissions-Policy")
    if not pp:
        findings.append(
            Finding(
                check="headers",
                severity="low",
                title="Missing Permissions-Policy header",
                detail="No Permissions-Policy header found. Browser features like camera, "
                "microphone, and geolocation are not explicitly restricted.",
                remediation="Add a Permissions-Policy header to restrict unnecessary browser features, "
                "e.g., Permissions-Policy: camera=(), microphone=(), geolocation=()",
            )
        )

    # --- X-XSS-Protection (deprecated) ---
    xxp = headers.get("X-XSS-Protection")
    if xxp:
        findings.append(
            Finding(
                check="headers",
                severity="info",
                title="X-XSS-Protection header present (deprecated)",
                detail=f"The X-XSS-Protection header is set to '{xxp}'. This header is deprecated "
                f"in modern browsers and the XSS auditor has been removed. Relying on it "
                f"provides a false sense of security.",
                remediation="Remove X-XSS-Protection and rely on a strong Content-Security-Policy instead.",
            )
        )

    # --- Server header version disclosure ---
    server = headers.get("Server")
    if server and any(ch.isdigit() for ch in server):
        findings.append(
            Finding(
                check="headers",
                severity="low",
                title="Server header discloses version information",
                detail=f"The Server header value '{server}' contains version numbers, "
                f"which aids attackers in identifying known vulnerabilities.",
                remediation="Configure the web server to suppress or generalize the Server header.",
            )
        )

    if not findings:
        findings.append(
            Finding(
                check="headers",
                severity="info",
                title="All recommended security headers are present",
                detail="The response includes the standard set of security headers.",
                remediation="Continue monitoring headers as security best practices evolve.",
            )
        )

    return findings


# ---------------------------------------------------------------------------
# Check 2: SSL/TLS Certificate
# ---------------------------------------------------------------------------


def check_ssl_tls(url: str) -> list[Finding]:
    """Validate SSL/TLS certificate properties for the target host."""
    findings: list[Finding] = []
    parsed = urlparse(url)

    if parsed.scheme != "https":
        findings.append(
            Finding(
                check="ssl",
                severity="high",
                title="Target does not use HTTPS",
                detail=f"The target URL uses the '{parsed.scheme}' scheme. All traffic "
                f"is transmitted in plaintext, vulnerable to interception.",
                remediation="Configure the server to use HTTPS with a valid TLS certificate.",
            )
        )
        return findings

    hostname = parsed.hostname or ""
    port = parsed.port or 443

    context = ssl.create_default_context()

    try:
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
                cert = tls_sock.getpeercert()
                protocol_version = tls_sock.version()

                if not cert:
                    findings.append(
                        Finding(
                            check="ssl",
                            severity="critical",
                            title="No certificate returned by server",
                            detail="The TLS handshake completed but no certificate was presented.",
                            remediation="Ensure the server is configured with a valid TLS certificate.",
                        )
                    )
                    return findings

                # Protocol version
                if protocol_version:
                    findings.append(
                        Finding(
                            check="ssl",
                            severity="info",
                            title=f"TLS protocol version: {protocol_version}",
                            detail=f"The server negotiated {protocol_version}.",
                            remediation="Ensure TLS 1.2 or higher is used; disable TLS 1.0 and 1.1.",
                        )
                    )
                    if protocol_version in ("TLSv1", "TLSv1.1"):
                        findings.append(
                            Finding(
                                check="ssl",
                                severity="high",
                                title=f"Outdated TLS protocol: {protocol_version}",
                                detail=f"{protocol_version} is deprecated and has known vulnerabilities.",
                                remediation="Disable TLS 1.0 and TLS 1.1. Use TLS 1.2 or TLS 1.3.",
                            )
                        )

                # Certificate expiry
                not_after_str = cert.get("notAfter", "")
                if not_after_str:
                    # Python ssl cert dates use format: 'Mon DD HH:MM:SS YYYY GMT'
                    try:
                        not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                        not_after = not_after.replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        days_remaining = (not_after - now).days

                        if days_remaining < 0:
                            findings.append(
                                Finding(
                                    check="ssl",
                                    severity="critical",
                                    title="SSL certificate has expired",
                                    detail=f"The certificate expired on {not_after_str} "
                                    f"({abs(days_remaining)} days ago).",
                                    remediation="Renew the SSL/TLS certificate immediately.",
                                )
                            )
                        elif days_remaining < 7:
                            findings.append(
                                Finding(
                                    check="ssl",
                                    severity="critical",
                                    title=f"SSL certificate expires in {days_remaining} days",
                                    detail=f"The certificate expires on {not_after_str}. "
                                    f"Immediate renewal is required.",
                                    remediation="Renew the SSL/TLS certificate before expiry.",
                                )
                            )
                        elif days_remaining < 30:
                            findings.append(
                                Finding(
                                    check="ssl",
                                    severity="high",
                                    title=f"SSL certificate expires in {days_remaining} days",
                                    detail=f"The certificate expires on {not_after_str}. "
                                    f"Plan renewal soon to avoid service disruption.",
                                    remediation="Renew the SSL/TLS certificate within the next two weeks.",
                                )
                            )
                        else:
                            findings.append(
                                Finding(
                                    check="ssl",
                                    severity="info",
                                    title=f"SSL certificate valid for {days_remaining} days",
                                    detail=f"The certificate expires on {not_after_str}.",
                                    remediation="Monitor certificate expiry and renew before it lapses.",
                                )
                            )
                    except ValueError:
                        findings.append(
                            Finding(
                                check="ssl",
                                severity="medium",
                                title="Unable to parse certificate expiry date",
                                detail=f"Certificate notAfter value: '{not_after_str}' could not be parsed.",
                                remediation="Manually verify the certificate expiry date.",
                            )
                        )

                # Subject and issuer info
                subject_parts = []
                for rdn in cert.get("subject", ()):
                    for attr_name, attr_value in rdn:
                        subject_parts.append(f"{attr_name}={attr_value}")
                subject_str = ", ".join(subject_parts) if subject_parts else "unknown"

                issuer_parts = []
                for rdn in cert.get("issuer", ()):
                    for attr_name, attr_value in rdn:
                        issuer_parts.append(f"{attr_name}={attr_value}")
                issuer_str = ", ".join(issuer_parts) if issuer_parts else "unknown"

                findings.append(
                    Finding(
                        check="ssl",
                        severity="info",
                        title="Certificate subject and issuer",
                        detail=f"Subject: {subject_str} | Issuer: {issuer_str}",
                        remediation="Verify the certificate is issued by a trusted certificate authority.",
                    )
                )

                # SAN (Subject Alternative Names)
                san_list = cert.get("subjectAltName", ())
                san_names = [val for typ, val in san_list if typ == "DNS"]
                if san_names:
                    findings.append(
                        Finding(
                            check="ssl",
                            severity="info",
                            title=f"Certificate covers {len(san_names)} domain(s)",
                            detail=f"SANs: {', '.join(san_names[:10])}"
                            + (f" ... and {len(san_names) - 10} more" if len(san_names) > 10 else ""),
                            remediation="Ensure all required domains are listed in the certificate SANs.",
                        )
                    )

    except ssl.SSLCertVerificationError as exc:
        findings.append(
            Finding(
                check="ssl",
                severity="critical",
                title="SSL certificate verification failed",
                detail=f"Certificate validation error: {exc}",
                remediation="Replace the certificate with one issued by a trusted CA. "
                "Ensure the certificate chain is complete.",
            )
        )
    except ssl.SSLError as _tls_error:
        raise CheckIncomplete("Selected TLS transport failed: " + type(_tls_error).__name__, findings) from _tls_error
    except socket.timeout as _tls_error:
        raise CheckIncomplete("Selected TLS transport failed: " + type(_tls_error).__name__, findings) from _tls_error
    except OSError as _tls_error:
        raise CheckIncomplete("Selected TLS transport failed: " + type(_tls_error).__name__, findings) from _tls_error

    return findings


# ---------------------------------------------------------------------------
# Check 3: Common Path Exposures
# ---------------------------------------------------------------------------

_SENSITIVE_PATHS = [
    ("/.git/HEAD", "Git repository metadata", "critical"),
    ("/.git/config", "Git configuration file", "critical"),
    ("/.env", "Environment variables file", "critical"),
    ("/server-status", "Apache server status page", "high"),
    ("/server-info", "Apache server info page", "high"),
    ("/admin", "Admin panel", "medium"),
    ("/wp-admin", "WordPress admin panel", "medium"),
    ("/phpmyadmin", "phpMyAdmin database interface", "high"),
    ("/elmah.axd", ".NET error log handler", "high"),
    ("/actuator", "Spring Boot actuator endpoint", "high"),
    ("/debug", "Debug interface", "high"),
]

_DIRECTORY_LISTING_INDICATORS = [
    "Index of /",
    "Directory listing for",
    "Parent Directory",
    "[To Parent Directory]",
]


def probe_common_exposures(url: str, session: requests.Session) -> list[Finding]:
    """Probe for commonly exposed files, directories, and admin interfaces."""
    findings: list[Finding] = []
    timeout: int = getattr(session, "timeout", 10)
    base = url.rstrip("/")

    # --- Sensitive path probing ---
    for path, description, severity in _SENSITIVE_PATHS:
        target = base + path
        try:
            resp = session.get(target, timeout=timeout, allow_redirects=False)
            if resp.status_code == 200:
                # Verify it is not a generic error page or redirect by checking content length
                content_length = len(resp.content)
                if content_length > 0:
                    findings.append(
                        Finding(
                            check="endpoints",
                            severity=severity,
                            title=f"Exposed: {description} ({path})",
                            detail=f"HTTP 200 returned for {target} with {content_length} bytes. "
                            f"This resource should not be publicly accessible.",
                            remediation=f"Block access to {path} via web server configuration. "
                            f"Return 403 or 404 for this path.",
                        )
                    )
            elif resp.status_code in (401, 403):
                findings.append(
                    Finding(
                        check="endpoints",
                        severity="info",
                        title=f"Path exists but access denied: {path}",
                        detail=f"HTTP {resp.status_code} returned for {target}. "
                        f"The path exists but requires authentication.",
                        remediation=f"Consider returning 404 instead of {resp.status_code} "
                        f"to avoid confirming the path exists.",
                    )
                )
        except requests.RequestException as _transport_error:
            raise CheckIncomplete(
                "Selected probe_common_exposures request failed: " + type(_transport_error).__name__, findings
            ) from _transport_error

    # --- robots.txt analysis ---
    try:
        resp = session.get(base + "/robots.txt", timeout=timeout, allow_redirects=True)
        if resp.status_code == 200 and "disallow" in resp.text.lower():
            findings.append(
                Finding(
                    check="endpoints",
                    severity="info",
                    title="robots.txt found",
                    detail=f"The robots.txt file is accessible at {base}/robots.txt.",
                    remediation="Review robots.txt entries. Disallowed paths may reveal "
                    "sensitive directories that warrant additional access controls.",
                )
            )
            # Parse interesting disallows
            interesting_disallows = []
            for line in resp.text.splitlines():
                line_stripped = line.strip().lower()
                if line_stripped.startswith("disallow:"):
                    path_part = line.strip().split(":", 1)[1].strip()
                    if path_part and path_part != "/":
                        sensitive_keywords = [
                            "admin",
                            "api",
                            "config",
                            "backup",
                            "private",
                            "internal",
                            "secret",
                            "debug",
                            "staging",
                            "test",
                            "tmp",
                            "upload",
                            "database",
                            "db",
                            "cgi-bin",
                        ]
                        if any(kw in path_part.lower() for kw in sensitive_keywords):
                            interesting_disallows.append(path_part)
            if interesting_disallows:
                findings.append(
                    Finding(
                        check="endpoints",
                        severity="low",
                        title="robots.txt reveals potentially sensitive paths",
                        detail=f"Interesting disallowed paths: {', '.join(interesting_disallows[:10])}",
                        remediation="Ensure disallowed paths have proper access controls beyond "
                        "robots.txt, which is advisory only and publicly readable.",
                    )
                )
    except requests.RequestException as _transport_error:
        raise CheckIncomplete(
            "Selected probe_common_exposures request failed: " + type(_transport_error).__name__, findings
        ) from _transport_error

    # --- security.txt ---
    for sec_path in ["/.well-known/security.txt", "/security.txt"]:
        try:
            resp = session.get(base + sec_path, timeout=timeout, allow_redirects=True)
            if resp.status_code == 200 and "contact:" in resp.text.lower():
                findings.append(
                    Finding(
                        check="endpoints",
                        severity="info",
                        title="security.txt found",
                        detail=f"A security.txt file is accessible at {base}{sec_path}. "
                        f"This is a good security practice (RFC 9116).",
                        remediation="Ensure the security.txt contact information is current.",
                    )
                )
                break  # Only report once
        except requests.RequestException as _transport_error:
            raise CheckIncomplete(
                "Selected probe_common_exposures request failed: " + type(_transport_error).__name__, findings
            ) from _transport_error

    # --- Directory listing detection ---
    try:
        resp = session.get(base + "/", timeout=timeout, allow_redirects=True)
        content_sample = resp.text[:2000] if resp.text else ""
        for indicator in _DIRECTORY_LISTING_INDICATORS:
            if indicator.lower() in content_sample.lower():
                findings.append(
                    Finding(
                        check="endpoints",
                        severity="high",
                        title="Directory listing is enabled",
                        detail=f"The root path appears to expose a directory listing "
                        f"(detected indicator: '{indicator}').",
                        remediation="Disable directory listing in the web server configuration. "
                        "For Apache: 'Options -Indexes'. For Nginx: remove 'autoindex on'.",
                    )
                )
                break
    except requests.RequestException as _transport_error:
        raise CheckIncomplete(
            "Selected probe_common_exposures request failed: " + type(_transport_error).__name__, findings
        ) from _transport_error

    # --- Server header version disclosure ---
    try:
        resp = session.get(base + "/", timeout=timeout, allow_redirects=True)
        server_header = resp.headers.get("Server", "")
        x_powered = resp.headers.get("X-Powered-By", "")
        if server_header and any(ch.isdigit() for ch in server_header):
            findings.append(
                Finding(
                    check="endpoints",
                    severity="low",
                    title="Server version disclosure",
                    detail=f"The Server header reveals: '{server_header}'.",
                    remediation="Suppress version information in the Server header.",
                )
            )
        if x_powered:
            findings.append(
                Finding(
                    check="endpoints",
                    severity="low",
                    title="X-Powered-By header exposes technology stack",
                    detail=f"The X-Powered-By header reveals: '{x_powered}'.",
                    remediation="Remove the X-Powered-By header from server responses.",
                )
            )
    except requests.RequestException as _transport_error:
        raise CheckIncomplete(
            "Selected probe_common_exposures request failed: " + type(_transport_error).__name__, findings
        ) from _transport_error

    if not findings:
        findings.append(
            Finding(
                check="endpoints",
                severity="info",
                title="No common exposures detected",
                detail="None of the probed paths returned accessible content.",
                remediation="Continue monitoring for accidental exposure of sensitive paths.",
            )
        )

    return findings


# ---------------------------------------------------------------------------
# Check 4: HTTP Methods
# ---------------------------------------------------------------------------


def check_http_methods(url: str, session: requests.Session) -> list[Finding]:
    """Observe bounded method advertisement; never infer execution or XST."""
    timeout = getattr(session, "timeout", 10)
    response = None
    try:
        response = session.options(url, timeout=timeout, allow_redirects=False, stream=True)
        if not 200 <= response.status_code < 300:
            raise CheckIncomplete("Method discovery was redirected, rejected or failed")
        raw = response.headers.get("Allow", "")
        if not isinstance(raw, str) or not raw or len(raw) > 4096:
            raise CheckIncomplete("Method discovery lacked a bounded Allow header")
        methods = [part.strip() for part in raw.split(",")]
        if len(methods) > 64 or any(
            not part or not part.isascii() or not all(c.isalpha() or c in "!#$%&'*+-.^_`|~0123456789" for c in part)
            for part in methods
        ):
            raise CheckIncomplete("Method discovery contained malformed method tokens")
        return [
            Finding(
                check="methods",
                severity="info",
                title="Advertised HTTP methods",
                detail=", ".join(sorted(set(methods)))
                + ". Advertisement does not demonstrate a write, TRACE echo, browser exploitation or proxy forwarding.",
                remediation="Compare with owner policy; use separately approved narrow operator experiments for capability proof.",
            )
        ]
    except requests.RequestException as exc:
        raise CheckIncomplete("Method discovery transport failed: " + type(exc).__name__) from exc
    finally:
        if response is not None:
            response.close()


# ---------------------------------------------------------------------------
# Check 5: CORS Policy
# ---------------------------------------------------------------------------


def check_cors_policy(url: str, session: requests.Session) -> list[Finding]:
    """Analyze CORS configuration for misconfigurations that allow unauthorized access."""
    findings: list[Finding] = []
    timeout: int = getattr(session, "timeout", 10)

    test_origin = "https://evil.example.com"

    try:
        headers = {"Origin": test_origin}
        resp = session.get(url, headers=headers, timeout=timeout, allow_redirects=True)

        acao = resp.headers.get("Access-Control-Allow-Origin", "")
        acac = resp.headers.get("Access-Control-Allow-Credentials", "").lower()

        if not acao:
            findings.append(
                Finding(
                    check="cors",
                    severity="info",
                    title="No CORS headers in response",
                    detail="The server did not return an Access-Control-Allow-Origin header. "
                    "Cross-origin requests from browsers will be blocked by default.",
                    remediation="This is the secure default. Only add CORS headers if cross-origin "
                    "access is intentionally required.",
                )
            )
        elif acao == "*":
            if acac == "true":
                findings.append(
                    Finding(
                        check="cors",
                        severity="critical",
                        title="CORS: Wildcard origin with credentials allowed",
                        detail="Access-Control-Allow-Origin is set to '*' and "
                        "Access-Control-Allow-Credentials is 'true'. While browsers block "
                        "this combination, server-side misconfiguration indicates a flawed "
                        "CORS implementation that could be exploited.",
                        remediation="Never combine wildcard origin with Allow-Credentials. "
                        "Implement an origin allowlist and validate requests against it.",
                    )
                )
            else:
                findings.append(
                    Finding(
                        check="cors",
                        severity="medium",
                        title="CORS: Wildcard origin configured",
                        detail="Access-Control-Allow-Origin is set to '*', allowing any website "
                        "to make cross-origin requests. If the API serves sensitive data "
                        "or requires authentication, this is a security risk.",
                        remediation="Replace the wildcard with specific trusted origins. "
                        "Use an allowlist approach for cross-origin access.",
                    )
                )
        elif acao.lower() == test_origin.lower():
            severity = "critical" if acac == "true" else "high"
            cred_note = " with credentials" if acac == "true" else ""
            findings.append(
                Finding(
                    check="cors",
                    severity=severity,
                    title=f"CORS: Origin reflection detected{cred_note}",
                    detail=f"The server reflected the arbitrary origin '{test_origin}' in the "
                    f"Access-Control-Allow-Origin header{cred_note}. This means any "
                    f"website can make authenticated cross-origin requests.",
                    remediation="Implement a strict origin allowlist. Never reflect the Origin "
                    "header value without validation against a list of trusted domains.",
                )
            )
        else:
            findings.append(
                Finding(
                    check="cors",
                    severity="info",
                    title=f"CORS: Specific origin configured ({acao})",
                    detail=f"The server returned a specific origin '{acao}' in the CORS header, "
                    f"not reflecting the test origin. This indicates proper origin validation.",
                    remediation="Periodically review the allowed origins to ensure they are still trusted.",
                )
            )

        # Check for overly permissive methods in preflight
        acam = resp.headers.get("Access-Control-Allow-Methods", "")
        if acam and acao:
            allowed_methods = {m.strip().upper() for m in acam.split(",") if m.strip()}
            risky = allowed_methods & {"PUT", "DELETE", "PATCH"}
            if risky:
                findings.append(
                    Finding(
                        check="cors",
                        severity="low",
                        title=f"CORS allows state-changing methods: {', '.join(sorted(risky))}",
                        detail=f"Cross-origin requests are permitted to use {', '.join(sorted(risky))} "
                        f"methods. Ensure these endpoints have proper authentication.",
                        remediation="Only expose the minimum set of HTTP methods required for "
                        "legitimate cross-origin requests.",
                    )
                )

    except requests.RequestException as _transport_error:
        raise CheckIncomplete(
            "Selected check_cors_policy request failed: " + type(_transport_error).__name__, findings
        ) from _transport_error

    return findings


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------


def _calculate_risk_score(findings: list[Finding]) -> int:
    """Calculate a security risk score from 0 (worst) to 100 (best).

    Starts at 100 and subtracts points for each finding based on severity.
    Info-level findings do not affect the score.
    """
    deductions = 0
    for f in findings:
        deductions += SEVERITY_WEIGHTS.get(f.severity, 0)
    score = max(0, 100 - deductions)
    return score


def _severity_sort_key(severity: str) -> int:
    """Return sort order for severities (critical first)."""
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    return order.get(severity, 5)


def generate_report(
    url: str,
    results: ScanResult,
    output_path: Optional[str] = None,
) -> str:
    """Generate a security scan report in Markdown format and optionally write JSON.

    Args:
        url: The target URL that was scanned.
        results: The aggregated scan results.
        output_path: If provided, write a JSON report to this file path.

    Returns:
        The Markdown-formatted report string.
    """
    # Count findings by severity
    severity_counts: dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
    }
    for f in results.findings:
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

    total_findings = len(results.findings)
    risk_score = None if results.errors else _calculate_risk_score(results.findings)

    # Risk rating label
    if risk_score is None:
        risk_label = "INCOMPLETE"
    elif risk_score >= 90:
        risk_label = "LOW RISK"
    elif risk_score >= 70:
        risk_label = "MODERATE RISK"
    elif risk_score >= 50:
        risk_label = "HIGH RISK"
    else:
        risk_label = "CRITICAL RISK"

    # Build Markdown report
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("  SECURITY SCAN REPORT")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Target:     {url}")
    lines.append(f"Scan start: {results.scan_start}")
    lines.append(f"Scan end:   {results.scan_end}")
    lines.append(f"Duration:   {results.duration_seconds:.1f} seconds")
    lines.append(f"Checks:     {', '.join(results.checks_performed)}")
    lines.append("")
    lines.append("-" * 72)
    lines.append(
        "  RISK SCORE: not assessed (INCOMPLETE)"
        if risk_score is None
        else f"  RISK SCORE: {risk_score}/100 ({risk_label})"
    )
    lines.append("-" * 72)
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"  Total findings: {total_findings}")
    lines.append(f"  Critical:       {severity_counts['critical']}")
    lines.append(f"  High:           {severity_counts['high']}")
    lines.append(f"  Medium:         {severity_counts['medium']}")
    lines.append(f"  Low:            {severity_counts['low']}")
    lines.append(f"  Informational:  {severity_counts['info']}")
    lines.append("")

    if results.errors:
        lines.append("## Scan Errors")
        lines.append("")
        for err in results.errors:
            lines.append(f"  - {err}")
        lines.append("")

    # Detailed findings sorted by severity
    lines.append("## Detailed Findings")
    lines.append("")

    sorted_findings = sorted(results.findings, key=lambda f: _severity_sort_key(f.severity))

    for i, finding in enumerate(sorted_findings, 1):
        sev_upper = finding.severity.upper()
        lines.append(f"### [{sev_upper}] {finding.title}")
        lines.append("")
        lines.append(f"  Check:       {finding.check}")
        lines.append(f"  Severity:    {sev_upper}")
        lines.append(f"  Detail:      {finding.detail}")
        lines.append(f"  Remediation: {finding.remediation}")
        lines.append("")

    lines.append("=" * 72)
    lines.append(f"  End of report. {total_findings} finding(s) across {len(results.checks_performed)} check(s).")
    lines.append("=" * 72)

    report_text = "\n".join(lines)

    # JSON output
    if output_path:
        json_data = {
            "scanner": f"SecurityScanner/{__version__}",
            "target": url,
            "scan_start": results.scan_start,
            "scan_end": results.scan_end,
            "duration_seconds": results.duration_seconds,
            "checks_performed": results.checks_performed,
            "risk_score": risk_score,
            "risk_label": risk_label,
            "severity_counts": severity_counts,
            "total_findings": total_findings,
            "findings": [asdict(f) for f in sorted_findings],
            "errors": results.errors,
            "status": "incomplete" if results.errors else "complete",
        }
        try:
            with open(output_path, "w", encoding="utf-8") as fh:
                json.dump(json_data, fh, indent=2, ensure_ascii=False)
            _log(f"JSON report written to: {output_path}")
        except OSError as exc:
            raise CheckIncomplete("Requested report could not be persisted: " + type(exc).__name__) from exc

    return report_text


# ---------------------------------------------------------------------------
# CLI / Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Parse arguments and execute the security scan.

    Returns:
        Exit code: 0 if no critical/high findings, 1 otherwise, 2 on error.
    """
    parser = argparse.ArgumentParser(
        prog="security_scanner",
        description=(
            "HTTP Security Scanner - Automated web application security assessment. "
            "Performs non-intrusive checks against a target URL to identify "
            "misconfigurations and security weaknesses."
        ),
        epilog=(
            "Examples:\n"
            "  %(prog)s https://example.com\n"
            "  %(prog)s https://example.com --output report.json\n"
            "  %(prog)s https://example.com --checks headers,ssl,cors\n"
            "  %(prog)s https://example.com --timeout 15 --verbose\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "url",
        help="Target URL to scan (must include scheme, e.g., https://example.com)",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Write JSON report to the specified file path",
    )
    parser.add_argument(
        "--checks",
        "-c",
        metavar="LIST",
        default=",".join(ALL_CHECKS),
        help=(f"Comma-separated list of checks to run. Available: {', '.join(ALL_CHECKS)}. Default: all"),
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=10,
        metavar="SECONDS",
        help="Request timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print progress messages to stderr",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Validate URL
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    try:
        parsed = urlparse(args.url)
        _ = parsed.port
    except ValueError:
        _log_error("Invalid URL syntax or port")
        return 2
    if parsed.scheme not in ("http", "https"):
        _log_error(f"Invalid URL scheme: '{parsed.scheme}'. Use http:// or https://")
        return 2
    if not parsed.hostname:
        _log_error("Invalid URL: no hostname found.")
        return 2

    # Parse requested checks
    requested = [c.strip().lower() for c in args.checks.split(",") if c.strip()]
    invalid_checks = [c for c in requested if c not in ALL_CHECKS]
    if invalid_checks or not requested or len(requested) != len(set(requested)):
        _log_error(f"Unknown check(s): {', '.join(invalid_checks)}. Available: {', '.join(ALL_CHECKS)}")
        return 2

    # Initialize
    url = args.url.rstrip("/")
    session = create_session(timeout=args.timeout)
    scan_start = datetime.now(timezone.utc)

    result = ScanResult(
        target=url,
        scan_start=scan_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    _log(f"SecurityScanner v{__version__} starting scan of {url}", args.verbose)
    _log(f"Checks: {', '.join(requested)}", args.verbose)
    _log(f"Timeout: {args.timeout}s", args.verbose)
    _log("", args.verbose)

    # Connectivity pre-check
    try:
        session.head(url, timeout=args.timeout, allow_redirects=True)
    except requests.ConnectionError:
        _log_error(f"Cannot connect to {url}. Verify the URL and network connectivity.")
        return 2
    except requests.Timeout:
        _log_error(f"Connection to {url} timed out after {args.timeout} seconds.")
        return 2
    except requests.RequestException as exc:
        _log_error("Connectivity pre-check failed: " + type(exc).__name__)
        return 2

    # Execute checks
    check_map: dict[str, tuple[str, object]] = {
        "headers": ("Security Headers", lambda: scan_security_headers(url, session)),
        "ssl": ("SSL/TLS Certificate", lambda: check_ssl_tls(url)),
        "endpoints": ("Common Exposures", lambda: probe_common_exposures(url, session)),
        "methods": ("HTTP Methods", lambda: check_http_methods(url, session)),
        "cors": ("CORS Policy", lambda: check_cors_policy(url, session)),
    }

    for check_name in requested:
        label, check_fn = check_map[check_name]
        _log(f"Running check: {label}...", args.verbose)
        try:
            findings = check_fn()
            result.findings.extend(findings)
            result.checks_performed.append(check_name)
            _log(f"  {label}: {len(findings)} finding(s)", args.verbose)
        except Exception as exc:
            error_msg = f"Check '{check_name}' incomplete: " + (
                str(exc) if isinstance(exc, CheckIncomplete) else type(exc).__name__
            )
            _log_error(error_msg)
            result.errors.append(error_msg)
            if isinstance(exc, CheckIncomplete):
                result.findings.extend(exc.findings)

    # Finalize timing
    scan_end = datetime.now(timezone.utc)
    result.scan_end = scan_end.strftime("%Y-%m-%dT%H:%M:%SZ")
    result.duration_seconds = round((scan_end - scan_start).total_seconds(), 2)

    _log("", args.verbose)
    _log(f"Scan complete. {len(result.findings)} finding(s) in {result.duration_seconds}s", args.verbose)
    _log("", args.verbose)

    # Generate and print report
    try:
        report = generate_report(url, result, output_path=args.output)
    except CheckIncomplete as exc:
        _log_error(str(exc))
        return 2
    print(report)

    if result.errors:
        return 2

    # Determine exit code
    critical_or_high = sum(1 for f in result.findings if f.severity in ("critical", "high"))
    if critical_or_high > 0:
        _log(f"Exiting with code 1: {critical_or_high} critical/high finding(s)", args.verbose)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
