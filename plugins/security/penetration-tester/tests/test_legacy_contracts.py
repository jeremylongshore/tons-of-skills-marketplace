"""Actual legacy entry points with fabricated data and blocked external I/O.

Exercises retained CLI contracts with fabricated findings and explicit inert
process/session stubs; no scanner installation or live target is permitted.
"""

import importlib.util
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
from types import SimpleNamespace

import pytest
import requests

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = ROOT / "plugins/security/penetration-tester/skills/performing-penetration-testing/scripts"


@pytest.fixture(autouse=True)
def deny_external_io(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("External process/network I/O is forbidden in these fixtures")

    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(requests.sessions.Session, "request", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


@pytest.fixture
def load():
    def load_module(name):
        module_name = "legacy_contract_" + name
        spec = importlib.util.spec_from_file_location(module_name, SCRIPTS / (name + ".py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    return load_module


def exit_from_main(module):
    try:
        result = module.main()
    except SystemExit as exc:
        return exc.code
    return result


def finding(**overrides):
    return {
        "file": "synthetic-app.py",
        "line": 3,
        "severity": "critical",
        "category": "hardcoded-secret",
        "title": "Synthetic secret pattern",
        "detail": "short synthetic evidence",
        **overrides,
    }


def test_duplicate_with_longer_low_detail_cannot_erase_critical(load):
    module = load("code_security_scanner")
    merged = module.merge_findings([finding()], [finding(severity="low", detail="longer synthetic context " * 20)])
    assert merged[0]["severity"] == "critical"


def test_distinct_issue_categories_at_one_line_survive(load):
    module = load("code_security_scanner")
    merged = module.merge_findings(
        [finding()], [finding(category="command-injection", title="Synthetic command pattern")]
    )
    assert {row["category"] for row in merged} == {"hardcoded-secret", "command-injection"}


def test_regex_secret_is_redacted_in_findings_stdout_and_json(load, tmp_path, capsys):
    module = load("code_security_scanner")
    secret = "FixtureOnlyPass123456!"
    (tmp_path / "app.py").write_text('password = "' + secret + '"\n')
    rows = module.run_regex_scan(tmp_path, None, False)
    assert rows, "The synthetic secret fixture must exercise a real matching rule"
    report = tmp_path / "report.json"
    module.generate_report(tmp_path, rows, report)
    captured = capsys.readouterr()
    assert secret not in json.dumps(rows)
    assert secret not in captured.out + captured.err + report.read_text()


def test_selected_missing_bandit_is_incomplete_exit2(load, tmp_path, monkeypatch, capsys):
    module = load("code_security_scanner")
    monkeypatch.setattr(shutil, "which", lambda executable: None)

    def missing_tool(argv, **kwargs):
        assert argv[0] == "bandit" and "install" not in argv
        raise FileNotFoundError("Synthetic absent Bandit executable")

    monkeypatch.setattr(subprocess, "run", missing_tool)
    monkeypatch.setattr(sys, "argv", ["code_security_scanner", str(tmp_path), "--tools", "bandit"])
    assert exit_from_main(module) == 2
    assert "No security issues found" not in capsys.readouterr().out


def test_severity_presentation_filter_cannot_hide_a_high_gate(load, tmp_path, monkeypatch, capsys):
    module = load("code_security_scanner")
    monkeypatch.setattr(module, "run_regex_scan", lambda *args, **kwargs: [finding(severity="high")])
    monkeypatch.setattr(
        sys, "argv", ["code_security_scanner", str(tmp_path), "--tools", "regex", "--severity", "critical"]
    )
    assert exit_from_main(module) == 1


def test_npm_error_shaped_json_is_not_a_clean_completed_audit(load, tmp_path, monkeypatch):
    module = load("dependency_auditor")
    (tmp_path / "package.json").write_text('{"name":"synthetic-fixture","version":"1.0.0"}')
    calls = []

    def respond(argv, **kwargs):
        calls.append(argv)
        if argv == ["npm", "--version"]:
            return subprocess.CompletedProcess(argv, 0, "11.0.0", "")
        assert argv == ["npm", "audit", "--json"]
        return subprocess.CompletedProcess(
            argv, 1, json.dumps({"error": {"code": "EAUDITNOLOCK", "summary": "Synthetic missing lockfile"}}), ""
        )

    monkeypatch.setattr(subprocess, "run", respond)
    report = tmp_path / "dependency.json"
    monkeypatch.setattr(
        sys, "argv", ["dependency_auditor", str(tmp_path), "--scanners", "npm", "--output", str(report)]
    )
    assert exit_from_main(module) == 2
    assert calls and json.loads(report.read_text()).get("errors")


def test_failed_web_check_is_incomplete_without_numeric_risk_score(load, tmp_path, monkeypatch):
    module = load("security_scanner")
    session = SimpleNamespace(head=lambda *args, **kwargs: SimpleNamespace(status_code=200))
    monkeypatch.setattr(module, "create_session", lambda **kwargs: session)

    def failed(*args, **kwargs):
        raise RuntimeError("Synthetic selected-check failure")

    monkeypatch.setattr(module, "scan_security_headers", failed)
    report = tmp_path / "web.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["security_scanner", "https://fixture.example.test", "--checks", "headers", "--output", str(report)],
    )
    assert exit_from_main(module) == 2
    data = json.loads(report.read_text())
    assert data["errors"] and data.get("risk_score") is None


def test_direct_code_report_redacts_sensitive_finding_context(load, tmp_path, capsys):
    module = load("code_security_scanner")
    secret = "FixtureOnlyContext123456!"
    rows = [finding(detail=secret, confidence="high", tool="regex", remediation="inspect locally")]
    report = tmp_path / "direct-code.json"
    module.generate_report(tmp_path, rows, report)
    captured = capsys.readouterr()
    assert secret not in captured.out + captured.err + report.read_text()


@pytest.mark.parametrize(
    "payload,status",
    [
        ("not-json", 0),
        ("{}", 0),
        ('{"results":[],"errors":[{"reason":"synthetic failure"}]}', 0),
        ('{"results":[]}', 2),
        ('{"results":[{"issue_severity":"UNKNOWN"}]}', 1),
    ],
)
def test_bandit_invalid_or_failed_results_are_incomplete(load, tmp_path, monkeypatch, payload, status):
    module = load("code_security_scanner")
    monkeypatch.setattr(
        subprocess, "run", lambda argv, **kwargs: subprocess.CompletedProcess(argv, status, payload, "")
    )
    report = tmp_path / "invalid-bandit.json"
    monkeypatch.setattr(
        sys, "argv", ["code_security_scanner", str(tmp_path), "--tools", "bandit", "--output", str(report)]
    )
    assert exit_from_main(module) == 2
    data = json.loads(report.read_text())
    assert data["status"] == "incomplete" and data["errors"] and data["exit_code"] == 2


def test_complete_empty_bandit_result_preserves_success(load, tmp_path, monkeypatch):
    module = load("code_security_scanner")
    monkeypatch.setattr(
        subprocess, "run", lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, '{"results":[],"errors":[]}', "")
    )
    monkeypatch.setattr(sys, "argv", ["code_security_scanner", str(tmp_path), "--tools", "bandit"])
    assert exit_from_main(module) == 0


def test_unreadable_source_cannot_be_silently_treated_as_binary(load, tmp_path, monkeypatch):
    import builtins

    module = load("code_security_scanner")
    source = tmp_path / "app.py"
    source.write_text('print("synthetic fixture")\n')
    original = builtins.open

    def denied(path, *args, **kwargs):
        if Path(path) == source:
            raise PermissionError("Synthetic unreadable source")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", denied)
    monkeypatch.setattr(sys, "argv", ["code_security_scanner", str(tmp_path), "--tools", "regex"])
    assert exit_from_main(module) == 2


def test_missing_pip_audit_never_installs_or_falls_back_to_ambient_environment(load, tmp_path, monkeypatch):
    module = load("dependency_auditor")
    (tmp_path / "requirements.txt").write_text("fixture-package==1.0.0\n")
    calls = []

    def unavailable(argv, **kwargs):
        calls.append(argv)
        assert argv[0] == "pip-audit" and "install" not in argv and "outdated" not in argv
        raise FileNotFoundError("Synthetic absent pip-audit")

    monkeypatch.setattr(subprocess, "run", unavailable)
    report = tmp_path / "pip.json"
    monkeypatch.setattr(
        sys, "argv", ["dependency_auditor", str(tmp_path), "--scanners", "pip", "--output", str(report)]
    )
    assert exit_from_main(module) == 2
    assert len(calls) == 1 and json.loads(report.read_text())["errors"]


def test_python_project_without_requirements_or_explicit_environment_fails_before_process(load, tmp_path, monkeypatch):
    module = load("dependency_auditor")
    (tmp_path / "pyproject.toml").write_text('[project]\nname="fixture"\n')
    calls = []

    def forbidden(argv, **kwargs):
        calls.append(argv)
        raise AssertionError("No interpreter should be selected implicitly")

    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(sys, "argv", ["dependency_auditor", str(tmp_path), "--scanners", "pip"])
    assert exit_from_main(module) == 2 and calls == []


def test_requirements_mode_is_project_bound_without_pip_dependency_resolution(load, tmp_path, monkeypatch):
    module = load("dependency_auditor")
    requirement = tmp_path / "requirements.txt"
    requirement.write_text("fixture-package==1.0.0\n")
    calls = []

    def respond(argv, **kwargs):
        calls.append(argv)
        assert argv[0] == "pip-audit"
        assert "--no-deps" in argv and "--disable-pip" in argv and "--strict" in argv
        assert argv[argv.index("--requirement") + 1] == str(requirement)
        assert kwargs["cwd"] == str(tmp_path)
        return subprocess.CompletedProcess(argv, 0, '{"dependencies":[]}', "")

    monkeypatch.setattr(subprocess, "run", respond)
    monkeypatch.setattr(sys, "argv", ["dependency_auditor", str(tmp_path), "--scanners", "pip"])
    assert exit_from_main(module) == 0 and len(calls) == 1


def test_designated_python_preserves_venv_symlink_path_and_binds_both_checks(load, tmp_path, monkeypatch):
    module = load("dependency_auditor")
    interpreter = tmp_path / "venv" / "bin" / "python"
    interpreter.parent.mkdir(parents=True)
    interpreter.symlink_to(sys.executable)
    calls = []

    def respond(argv, **kwargs):
        calls.append(argv)
        assert argv[0] == str(interpreter) and kwargs["cwd"] == str(tmp_path)
        if argv[1:4] == ["-I", "-m", "pip_audit"]:
            return subprocess.CompletedProcess(argv, 0, '{"dependencies":[]}', "")
        assert argv[1:] == ["-I", "-m", "pip", "check"]
        return subprocess.CompletedProcess(argv, 0, "No broken requirements found.", "")

    monkeypatch.setattr(subprocess, "run", respond)
    report = tmp_path / "bound-environment.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "dependency_auditor",
            str(tmp_path),
            "--scanners",
            "pip",
            "--python",
            str(interpreter),
            "--output",
            str(report),
        ],
    )
    assert exit_from_main(module) == 0 and len(calls) == 2
    assert json.loads(report.read_text())["audit_inputs"]["python"] == {
        "mode": "designated-environment",
        "interpreter": str(interpreter),
        "isolated": True,
    }


@pytest.mark.parametrize("severity", [None, "high"])
def test_pip_advisory_severity_is_preserved_or_explicitly_unknown(load, severity):
    module = load("dependency_auditor")
    vuln = {"id": "CVE-2026-11111"}
    if severity is not None:
        vuln["severity"] = severity
    rows = module._parse_pip_audit_output(json.dumps([{"name": "fixture-package", "version": "1", "vulns": [vuln]}]))
    assert rows[0]["severity"] == (severity or "unknown")


def test_unknown_severity_remains_visible_and_incomplete_under_critical_filter(load, tmp_path, monkeypatch):
    module = load("dependency_auditor")
    (tmp_path / "requirements.txt").write_text("fixture-package==1.0.0\n")
    payload = json.dumps([{"name": "fixture-package", "version": "1", "vulns": [{"id": "CVE-2026-11111"}]}])
    monkeypatch.setattr(subprocess, "run", lambda argv, **kwargs: subprocess.CompletedProcess(argv, 1, payload, ""))
    report = tmp_path / "unknown.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "dependency_auditor",
            str(tmp_path),
            "--scanners",
            "pip",
            "--min-severity",
            "critical",
            "--output",
            str(report),
        ],
    )
    assert exit_from_main(module) == 2
    data = json.loads(report.read_text())
    assert data["findings"][0]["severity"] == "unknown" and data["errors"]


def test_npm_high_finding_gate_survives_critical_filter(load, tmp_path, monkeypatch):
    module = load("dependency_auditor")
    (tmp_path / "package.json").write_text('{"name":"fixture","version":"1.0.0"}')
    payload = json.dumps({"vulnerabilities": {"fixture-dependency": {"severity": "high", "via": []}}})

    def respond(argv, **kwargs):
        return subprocess.CompletedProcess(
            argv, 0 if argv == ["npm", "--version"] else 1, "11" if argv == ["npm", "--version"] else payload, ""
        )

    monkeypatch.setattr(subprocess, "run", respond)
    report = tmp_path / "filtered.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "dependency_auditor",
            str(tmp_path),
            "--scanners",
            "npm",
            "--min-severity",
            "critical",
            "--output",
            str(report),
        ],
    )
    assert exit_from_main(module) == 1
    data = json.loads(report.read_text())
    assert data["findings"] == [] and data["total_unfiltered_findings"] == 1 and data["exit_code"] == 1


@pytest.mark.parametrize("check", ["headers", "endpoints", "methods", "cors"])
def test_failed_selected_web_transport_is_incomplete_without_clean_risk_score(load, tmp_path, monkeypatch, check):
    module = load("security_scanner")

    def unavailable(*args, **kwargs):
        raise requests.ConnectionError("Synthetic unavailable peer")

    session = SimpleNamespace(head=lambda *args, **kwargs: None, get=unavailable, options=unavailable)
    monkeypatch.setattr(module, "create_session", lambda **kwargs: session)
    report = tmp_path / "transport.json"
    monkeypatch.setattr(
        sys, "argv", ["security_scanner", "https://fixture.example.test", "--checks", check, "--output", str(report)]
    )
    assert exit_from_main(module) == 2
    data = json.loads(report.read_text())
    assert data["status"] == "incomplete" and data["risk_score"] is None and data["errors"]


def test_partial_web_findings_are_preserved_when_later_transport_fails(load, tmp_path, monkeypatch):
    module = load("security_scanner")
    partial = module.Finding(
        check="headers",
        severity="high",
        title="Synthetic finding",
        detail="Synthetic evidence",
        remediation="Inspect locally",
    )

    def interrupted(*args, **kwargs):
        raise module.CheckIncomplete("Synthetic interruption", [partial])

    monkeypatch.setattr(module, "create_session", lambda **kwargs: SimpleNamespace(head=lambda *args, **kwargs: None))
    monkeypatch.setattr(module, "scan_security_headers", interrupted)
    report = tmp_path / "partial.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["security_scanner", "https://fixture.example.test", "--checks", "headers", "--output", str(report)],
    )
    assert exit_from_main(module) == 2
    data = json.loads(report.read_text())
    assert data["findings"][0]["severity"] == "high" and data["risk_score"] is None


def test_legacy_options_advertisement_is_info_without_body_read_or_active_methods(load):
    module = load("security_scanner")
    calls = []

    class Response:
        status_code = 200
        headers = {"Allow": "GET, TRACE, CONNECT, PUT"}
        closed = False

        @property
        def content(self):
            raise AssertionError("Discovery must not read the body")

        def close(self):
            self.closed = True

    response = Response()

    def options(url, **kwargs):
        calls.append((url, kwargs))
        assert kwargs["allow_redirects"] is False and kwargs["stream"] is True
        return response

    rows = module.check_http_methods("https://fixture.example.test", SimpleNamespace(options=options))
    assert len(calls) == 1 and len(rows) == 1 and rows[0].severity == "info" and response.closed


@pytest.mark.parametrize("status,allow", [(302, "GET"), (403, "GET"), (200, ""), (200, "GET;TRACE"), (200, "X" * 4097)])
def test_legacy_options_missing_or_unusable_evidence_is_incomplete(load, status, allow):
    module = load("security_scanner")
    response = SimpleNamespace(status_code=status, headers={"Allow": allow}, close=lambda: None)
    peer = SimpleNamespace(options=lambda *args, **kwargs: response)
    with pytest.raises(module.CheckIncomplete):
        module.check_http_methods("https://fixture.example.test", peer)


@pytest.mark.parametrize(
    "url,extra",
    [
        ("https://fixture.example.test", ["--timeout", "0"]),
        ("https://fixture.example.test", ["--timeout", "-1"]),
        ("https://[broken", []),
        ("https://fixture.example.test:99999", []),
    ],
)
def test_bad_web_input_fails_before_transport_creation(load, monkeypatch, url, extra):
    module = load("security_scanner")
    calls = []
    monkeypatch.setattr(module, "create_session", lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr(sys, "argv", ["security_scanner", url, "--checks", "headers", *extra])
    assert exit_from_main(module) == 2 and calls == []
