"""Offline evidence classification for early-cluster network and source checks."""

import importlib.util
import socket
import subprocess
from types import SimpleNamespace
from pathlib import Path

import pytest

from lib.finding import Severity

PACK = Path(__file__).resolve().parents[1]
TARGET = "https://app.example.test"


@pytest.fixture(autouse=True)
def deny_external_io(monkeypatch):
    def denied(*args, **kwargs):
        pytest.fail("Parser fixtures must not invoke networking or subprocesses")

    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket.socket, "connect_ex", denied)
    monkeypatch.setattr(subprocess, "Popen", denied)


def load(skill, script):
    path = PACK / "skills" / skill / "scripts" / script
    spec = importlib.util.spec_from_file_location(skill.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "header,https,severities",
    [
        (None, False, []),
        (None, True, [Severity.HIGH]),
        ("max-age=0", True, [Severity.MEDIUM]),
        ("max-age=31536000; includeSubDomains; preload", True, []),
        ("max-age=31536000; preload", True, [Severity.LOW]),
    ],
)
def test_hsts_transport_and_policy(header, https, severities):
    module = load("checking-http-security-headers", "check_headers.py")
    headers = {} if header is None else {"Strict-Transport-Security": header}
    findings = module._check_hsts(headers, TARGET, https)
    assert [finding.severity for finding in findings] == severities
    assert all(finding.target == TARGET for finding in findings)


@pytest.mark.parametrize("version", ["SSLv3", "TLSv1", "TLSv1.1"])
def test_obsolete_tls_is_reported(version):
    module = load("analyzing-tls-config", "analyze_tls.py")
    findings = module._check_protocol(version, TARGET)
    assert len(findings) == 1
    assert findings[0].severity == Severity.HIGH
    assert version in findings[0].title


@pytest.mark.parametrize("version", ["TLSv1.2", "TLSv1.3"])
def test_modern_tls_has_no_obsolete_protocol_finding(version):
    module = load("analyzing-tls-config", "analyze_tls.py")
    assert module._check_protocol(version, TARGET) == []


@pytest.mark.parametrize(
    "body,expected",
    [
        ("<html><title>Index of /backups</title></html>", True),
        ('<?xml version="1.0"?><ListBucketResult><Contents/></ListBucketResult>', True),
        ("<html><title>Welcome</title></html>", False),
        ("", False),
        ("x" * 4096 + "<title>Index of /backups</title>", False),
    ],
)
def test_directory_listing_fingerprints_and_inspection_bound(body, expected):
    module = load("detecting-directory-listing", "probe_directory_listing.py")
    matched, framework = module._is_autoindex(body)
    assert matched is expected
    assert bool(framework) is expected


@pytest.mark.parametrize(
    "body,content_type,expected",
    [
        ("[core]\nrepositoryformatversion = 0", "text/plain", True),
        ("<html>SPA fallback</html>", "text/html", False),
        ("unrelated text", "text/plain", False),
        ("x" * 2048 + "[core]", "text/plain", False),
    ],
)
def test_secret_file_requires_expected_fingerprint(body, content_type, expected):
    module = load("detecting-exposed-secrets-files", "probe_secrets.py")
    assert module._verify_fingerprint(body, r"\[core\]", content_type) is expected


@pytest.mark.parametrize(
    "content_type,size,expected",
    [
        ("application/octet-stream", 100001, True),
        ("application/octet-stream", 100000, False),
        ("application/octet-stream", 0, False),
        ("text/html; charset=utf-8", 200000, False),
        ("TEXT/HTML", 200000, False),
    ],
)
def test_debug_binary_signal_requires_size_and_non_html(content_type, size, expected):
    module = load("detecting-debug-endpoints", "probe_debug.py")
    assert module._verify_fingerprint("", None, content_type, size) is expected


@pytest.mark.parametrize(
    "body,expected",
    [("phpinfo()", True), ("Welcome", False), ("x" * 4096 + "phpinfo()", False)],
)
def test_debug_text_fingerprint_inspection_bound(body, expected):
    module = load("detecting-debug-endpoints", "probe_debug.py")
    assert module._verify_fingerprint(body, r"phpinfo\(\)", "text/html", len(body)) is expected


SOURCE_CASES = [
    (
        "detecting-sql-injection-patterns",
        "scan_sqli.py",
        'cursor.execute(f"SELECT * FROM users WHERE id={user_id}")',
        'cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))',
    ),
    (
        "detecting-command-injection-patterns",
        "scan_cmdi.py",
        'os.system(f"echo {user_input}")',
        'subprocess.run(["echo", user_input], shell=False)',
    ),
    (
        "detecting-insecure-deserialization",
        "scan_deserialization.py",
        "pickle.loads(user_input)",
        "json.loads(user_input)",
    ),
    ("detecting-eval-exec-usage", "scan_eval.py", "eval(user_input)", "ast.literal_eval(user_input)"),
]


@pytest.mark.parametrize("skill,script,unsafe,safe", SOURCE_CASES)
def test_source_scanners_report_location_without_executing(tmp_path, skill, script, unsafe, safe):
    module = load(skill, script)
    source = tmp_path / "app.py"
    source.write_text("# synthetic source, never executed\n" + unsafe + "\n")
    findings = module.scan_file(source, tmp_path, {"python"})
    assert findings
    assert all(finding.target == "app.py:2" for finding in findings)
    assert any(finding.severity == Severity.CRITICAL for finding in findings)
    source.write_text(safe + "\n")
    assert module.scan_file(source, tmp_path, {"python"}) == []


@pytest.mark.parametrize("skill,script,unsafe,safe", SOURCE_CASES)
def test_source_scanners_respect_language_filter(tmp_path, skill, script, unsafe, safe):
    module = load(skill, script)
    source = tmp_path / "app.py"
    source.write_text(unsafe + "\n")
    assert module.scan_file(source, tmp_path, {"javascript"}) == []


@pytest.mark.parametrize("skill,script,unsafe,safe", SOURCE_CASES)
def test_source_scanners_skip_missing_files(tmp_path, skill, script, unsafe, safe):
    module = load(skill, script)
    assert module.scan_file(tmp_path / "missing.py", tmp_path, {"python"}) == []


@pytest.mark.parametrize(
    "text,expected", [("", False), ("OCSP response: no response sent", False), ("OCSP response: successful", True)]
)
def test_certificate_staple_output(text, expected):
    module = load("detecting-ssl-cert-issues", "check_cert_chain.py")
    assert module._has_ocsp_response(text) is expected


def test_certificate_chain_keeps_complete_blocks_in_order():
    module = load("detecting-ssl-cert-issues", "check_cert_chain.py")
    blocks = [
        "-----BEGIN CERTIFICATE-----\n" + label + "\n-----END CERTIFICATE-----"
        for label in ("leaf-fixture", "issuer-fixture")
    ]
    output = "diagnostic preamble\n" + "\nnoise\n".join(blocks) + "\n-----BEGIN CERTIFICATE-----\ntruncated"
    assert module._parse_chain(output) == blocks
    assert module._parse_chain("no certificates") == []


@pytest.mark.parametrize(
    "header,value,severity",
    [
        ("Server", "nginx", Severity.LOW),
        ("Server", "nginx/1.24", Severity.MEDIUM),
        ("X-AspNet-Version", "4.0", Severity.HIGH),
    ],
)
def test_server_disclosure_distinguishes_product_and_version(header, value, severity):
    module = load("fingerprinting-server-software", "fingerprint_server.py")
    findings = module._check_version_headers({header: value}, TARGET, "fixture")
    assert len(findings) == 1
    assert findings[0].severity == severity
    assert findings[0].target == TARGET
    assert module._check_version_headers({}, TARGET, "fixture") == []


@pytest.mark.parametrize("credentials,severity", [("true", Severity.CRITICAL), ("false", Severity.HIGH)])
def test_cors_attacker_reflection(credentials, severity):
    module = load("auditing-cors-policy", "audit_cors.py")
    response = SimpleNamespace(
        headers={"Access-Control-Allow-Origin": module.ATTACKER_ORIGIN, "Access-Control-Allow-Credentials": credentials}
    )
    findings = module._check_reflection(response, None, TARGET)
    assert len(findings) == 1
    assert findings[0].severity == severity
    response.headers["Access-Control-Allow-Origin"] = "https://trusted.example.test"
    assert module._check_reflection(response, None, TARGET) == []
    assert module._check_reflection(None, None, TARGET) == []


@pytest.mark.parametrize("credentials,expected", [("true", True), ("false", False)])
def test_cors_wildcard_credential_combination(credentials, expected):
    module = load("auditing-cors-policy", "audit_cors.py")
    response = SimpleNamespace(
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": credentials}
    )
    assert bool(module._check_baseline(response, TARGET)) is expected
    assert module._check_baseline(None, TARGET) == []


@pytest.mark.parametrize("value,entropy", [("", 0), ("aaaa", 0), ("abcd", 2)])
def test_secret_entropy_known_distributions(value, entropy):
    module = load("scanning-for-hardcoded-secrets", "scan_secrets.py")
    assert module.shannon_entropy(value) == entropy


def test_secret_context_findings_never_contain_complete_value(tmp_path):
    module = load("scanning-for-hardcoded-secrets", "scan_secrets.py")
    # Synthetic high-entropy text; no provider credential is generated or used.
    value = "".join(chr(i) for i in range(65, 91)) + "0123456789"
    source = tmp_path / "config.py"
    source.write_text('password = "' + value + '"\n')
    findings = module.scan_file(source, tmp_path, include_provider=False)
    assert findings
    for finding in findings:
        assert value not in str(finding.to_dict())
        assert module.redact(value) in finding.detail
        assert finding.target == "config.py:1"
    assert module.redact("short") == "***"
    assert module.scan_file(source, tmp_path, include_provider=False, include_context=False) == []


@pytest.mark.parametrize(
    "filename,allow,expected", [("checksum.py", False, True), ("checksum.py", True, False), ("app.py", True, True)]
)
def test_weak_crypto_checksum_exception_is_explicit(tmp_path, filename, allow, expected):
    module = load("detecting-weak-cryptography", "scan_weak_crypto.py")
    source = tmp_path / filename
    source.write_text("hashlib.md5(data)\n")
    findings = module.scan_file(source, tmp_path, {"python"}, allow)
    assert bool(findings) is expected
    source.write_text("hashlib.sha256(data)\n")
    assert module.scan_file(source, tmp_path, {"python"}, allow) == []
