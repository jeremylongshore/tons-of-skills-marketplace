"""Exercise bundled CLIs with local fake tools, never package registries/installers."""

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


SCRIPTS = (
    Path(__file__).resolve().parents[1] / "plugins/security/dependency-checker/skills/analyzing-dependencies/scripts"
)
TOOLS = (
    "npm",
    "pip",
    "pip3",
    "pip-audit",
    "safety",
    "composer",
    "bundle",
    "bundle-audit",
    "bundler-audit",
    "cargo",
    "cargo-audit",
    "gem",
    "pip-licenses",
)


def npm_report(severity="high"):
    return {
        "auditReportVersion": 2,
        "metadata": {"vulnerabilities": {"total": 1}},
        "vulnerabilities": {
            "fixture-package": {
                "name": "fixture-package",
                "severity": severity,
                "range": "<2.0.0",
                "via": [{"source": 17, "title": "Fictional fixture advisory", "severity": severity}],
                "nodes": ["node_modules/fixture-package"],
                "fixAvailable": False,
            }
        },
    }


@pytest.fixture
def sandbox(tmp_path):
    binaries = tmp_path / "bin"
    binaries.mkdir()
    calls = tmp_path / "tool-calls.jsonl"
    stub = f"""#!{sys.executable}
import json, os, pathlib, sys, time
name = pathlib.Path(sys.argv[0]).name
with open(os.environ['CHECKER_FIXTURE_CALLS'], 'a') as log:
    log.write(json.dumps([name, *sys.argv[1:]]) + '\\n')
case = json.loads(os.environ['CHECKER_FIXTURE_TOOLS']).get(name, {{'code': 99}})
if '--version' in sys.argv:
    print('fixture-tool 1.0')
    sys.exit(0)
time.sleep(case.get('sleep', 0))
sys.stdout.write(case.get('stdout', ''))
sys.stdout.write('x' * case.get('stdout_repeat', 0))
sys.stderr.write('x' * case.get('stderr_repeat', 0))
sys.stderr.write(case.get('stderr', ''))
sys.exit(case.get('code', 0))
"""
    for name in TOOLS:
        path = binaries / name
        path.write_text(stub)
        path.chmod(0o700)
    # Only explicit fake audit tools are on PATH. These utilities cannot audit,
    # install packages, or contact a registry; they support the old Bash control.
    for name in ("python3", "basename", "dirname", "cat", "head", "jq", "grep"):
        program = sys.executable if name == "python3" else shutil.which(name)
        if program:
            (binaries / name).symlink_to(program)
    env = {
        "PATH": str(binaries),
        "DEPENDENCY_CHECK_PYTHON": sys.executable,
        "CHECKER_FIXTURE_CALLS": str(calls),
        "CHECKER_FIXTURE_TOOLS": "{}",
    }
    return tmp_path, env, calls


def configure(sandbox, **tools):
    root, env, _ = sandbox
    env["CHECKER_FIXTURE_TOOLS"] = json.dumps(tools)
    (root / "package.json").write_text(
        json.dumps(
            {
                "name": "fictional-fixture",
                "version": "0.0.0",
                "dependencies": {"fixture-package": "1.0.0"},
            }
        )
    )
    (root / "package-lock.json").write_text('{"lockfileVersion": 3}')
    return root, env


def invoke(sandbox, script, *args):
    root, env, _ = sandbox
    prefix = ["/bin/bash"] if script.endswith(".sh") else [sys.executable]
    return subprocess.run(
        [*prefix, str(SCRIPTS / script), *args],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_npm_findings_are_not_appended_with_a_second_json_document(sandbox):
    configure(sandbox, npm={"code": 1, "stdout": json.dumps(npm_report())})
    result = invoke(sandbox, "dependency_check.sh", "--tool", "npm", "--format", "json")
    assert result.returncode == 1, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["complete"] is True
    assert report["summary"]["unfiltered_total"] >= 1


def test_npm_engine_failure_is_incomplete_not_clean(sandbox):
    configure(sandbox, npm={"code": 42, "stderr": "fictional-private-token-do-not-echo"})
    result = invoke(sandbox, "dependency_check.sh", "--tool", "npm", "--format", "json")
    assert result.returncode == 2, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["complete"] is False
    assert report["errors"]
    assert "fictional-private-token-do-not-echo" not in result.stdout + result.stderr


def test_license_enumeration_failure_is_not_an_empty_compliance_pass(sandbox):
    configure(sandbox, npm={"code": 42, "stderr": "fictional failed enumeration"})
    result = invoke(sandbox, "license_compliance_checker.py", "--strict", "--format", "json")
    assert result.returncode == 2, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["summary"]["complete"] is False
    assert report["errors"]


def test_formatter_rejects_an_engine_error_object(sandbox):
    root, _, _ = sandbox
    path = root / "error-report.json"
    path.write_text('{"error":{"code":"FICTIONAL_ENGINE_UNAVAILABLE"}}')
    result = invoke(sandbox, "vulnerability_report_parser.py", "--input", str(path))
    assert result.returncode != 0
    assert "No vulnerabilities found" not in result.stdout


@pytest.mark.parametrize(
    "payload",
    [
        '{"vulnerabilities": [], "vulnerabilities": []}',
        '{"vulnerabilities": [], "untrusted": NaN}',
        '{"vulnerabilities": []} {"vulnerabilities": []}',
        '{"vulnerabilities": [], "untrusted": 1e999}',
    ],
)
def test_ambiguous_json_is_never_a_clean_report(sandbox, payload):
    root, _, _ = sandbox
    path = root / "report.json"
    path.write_text(payload)
    result = invoke(sandbox, "vulnerability_report_parser.py", "--input", str(path))
    assert result.returncode != 0


def test_filtered_report_cannot_be_reformatted_into_a_clean_gate(sandbox):
    root, _, _ = sandbox
    configure(sandbox, npm={"code": 1, "stdout": json.dumps(npm_report("low"))})
    first = invoke(sandbox, "dependency_check.sh", "--tool", "npm", "--format", "json", "--severity", "critical")
    assert first.returncode == 1, first.stderr
    report = json.loads(first.stdout)
    assert report["summary"]["hidden_by_filter"] == 1
    path = root / "filtered.json"
    path.write_text(first.stdout)
    second = invoke(
        sandbox, "vulnerability_report_parser.py", "--input", str(path), "--format", "json", "--fail-on-findings"
    )
    assert second.returncode != 0
    assert json.loads(second.stdout)["complete"] is False


def test_python_license_inventory_ignores_project_selection_config(sandbox):
    root, _, _ = sandbox
    (root / "pyproject.toml").write_text('[tool.pip-licenses]\npackages = ["omit-everything"]\n')
    selected = root / "selected-python"
    selected.write_text(f"""#!{sys.executable}
import json, pathlib, sys
assert sys.argv[1:] == ['-m', 'piplicenses', '--python', sys.argv[0], '--format=json']
assert not pathlib.Path('pyproject.toml').exists()
print(json.dumps([{{'Name': 'fictional-package', 'Version': '1', 'License': 'MIT'}}]))
""")
    selected.chmod(0o700)
    result = invoke(sandbox, "license_compliance_checker.py", "--python", str(selected), "--format", "json")
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["summary"]["complete"] is True


BACKENDS = [
    (
        "npm",
        "npm",
        "package.json",
        "package-lock.json",
        {"metadata": {"vulnerabilities": {"total": 0}}, "vulnerabilities": {}},
        npm_report(),
    ),
    (
        "pip",
        "pip-audit",
        "requirements.txt",
        None,
        {"dependencies": [], "fixes": []},
        {
            "dependencies": [
                {"name": "fictional", "version": "1", "vulns": [{"id": "FIXTURE-1", "fix_versions": ["2"]}]}
            ]
        },
    ),
    (
        "composer",
        "composer",
        "composer.json",
        "composer.lock",
        {"advisories": []},
        {"advisories": {"fixture/package": [{"advisoryId": "FIXTURE-1", "title": "Fictional advisory"}]}},
    ),
    (
        "bundler",
        "bundle-audit",
        "Gemfile",
        "Gemfile.lock",
        {"version": "1", "created_at": "2026-10-25", "results": []},
        {
            "version": "1",
            "created_at": "2026-10-25",
            "results": [
                {
                    "type": "unpatched_gem",
                    "gem": {"name": "fictional", "version": "1"},
                    "advisory": {"id": "FIXTURE-1", "title": "Fictional advisory", "patched_versions": [">= 2"]},
                }
            ],
        },
    ),
    (
        "cargo",
        "cargo",
        "Cargo.toml",
        "Cargo.lock",
        {"vulnerabilities": {"found": False, "count": 0, "list": []}},
        {
            "vulnerabilities": {
                "found": True,
                "count": 1,
                "list": [
                    {
                        "package": {"name": "fictional", "version": "1"},
                        "advisory": {"id": "FIXTURE-1", "title": "Fictional advisory"},
                        "versions": {"patched": [">=2"]},
                    }
                ],
            }
        },
    ),
]


@pytest.mark.parametrize("backend,binary,manifest,lock,clean,findings", BACKENDS)
@pytest.mark.parametrize("outcome", ["clean", "findings", "failed", "malformed", "contradictory", "timeout", "missing"])
def test_every_backend_reports_observed_outcome(sandbox, backend, binary, manifest, lock, clean, findings, outcome):
    root, env, calls = sandbox
    (root / manifest).write_text("fixture-package==1.0" if backend == "pip" else "{}")
    if lock:
        (root / lock).write_text("{}")
    case = {"code": 0, "stdout": json.dumps(clean)}
    expected = 0
    if outcome == "findings":
        case = {"code": 1, "stdout": json.dumps(findings)}
        expected = 1
    elif outcome == "failed":
        case = {"code": 42, "stderr": "fictional-secret-never-echo"}
        expected = 2
    elif outcome == "malformed":
        case = {"code": 0, "stdout": "{broken"}
        expected = 2
    elif outcome == "contradictory":
        case = {"code": 1, "stdout": json.dumps(clean)}
        expected = 2
    elif outcome == "timeout":
        case = {"sleep": 2}
        expected = 2
    elif outcome == "missing":
        (root / "bin" / binary).unlink()
        if backend == "bundler":
            (root / "bin" / "bundler-audit").unlink()
        expected = 2
    env["CHECKER_FIXTURE_TOOLS"] = json.dumps({binary: case})
    result = invoke(sandbox, "dependency_check.sh", "--tool", backend, "--format", "json", "--timeout", "0.2")
    assert result.returncode == expected, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["complete"] is (expected != 2)
    assert "fictional-secret-never-echo" not in result.stdout + result.stderr
    if expected == 1:
        assert report["summary"]["unfiltered_total"] >= 1
    if calls.exists():
        commands = [json.loads(line) for line in calls.read_text().splitlines()]
        assert len(commands) == 1
        assert not any(arg in ("install", "fix", "--update") for arg in commands[0])
        if backend == "pip":
            assert "--no-deps" in commands[0] and "--disable-pip" in commands[0]


@pytest.mark.parametrize(
    "license_value,expected", [("MIT", 0), ("MIT AND GPL-3.0-only", 1), ("LicenseRef-private", 1), (None, 1)]
)
def test_license_metadata_requires_review_for_unresolved_expressions(sandbox, license_value, expected):
    configure(
        sandbox,
        npm={
            "code": 0,
            "stdout": json.dumps({"dependencies": {"fixture-package": {"version": "1", "license": license_value}}}),
        },
    )
    result = invoke(sandbox, "license_compliance_checker.py", "--format", "json")
    assert result.returncode == expected, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["summary"]["complete"] is True
    assert report["summary"]["legal_compatibility_verified"] is False


def format_payload(sandbox, payload, *arguments):
    root, _, _ = sandbox
    path = root / "input.json"
    path.write_text(json.dumps(payload))
    return invoke(sandbox, "vulnerability_report_parser.py", "--input", str(path), *arguments)


def test_unknown_severity_stays_visible_at_critical_filter(sandbox):
    payload = {"dependencies": [{"name": "fictional", "version": "1", "vulns": [{"id": "FIXTURE-1"}]}]}
    result = format_payload(sandbox, payload, "--format", "json", "--severity", "critical", "--fail-on-findings")
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["vulnerabilities"][0]["severity"] == "UNKNOWN"
    assert report["summary"]["hidden_by_filter"] == 0


def test_skipped_python_package_keeps_partial_findings_incomplete(sandbox):
    payload = {
        "dependencies": [
            {"name": "fictional", "version": "1", "vulns": [{"id": "FIXTURE-1"}]},
            {"name": "private-fixture", "skip_reason": "fictional-private-token-do-not-echo"},
        ]
    }
    result = format_payload(sandbox, payload, "--format", "json")
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["complete"] is False
    assert report["summary"]["unfiltered_total"] == 1
    assert "fictional-private-token-do-not-echo" not in result.stdout + result.stderr


@pytest.mark.parametrize(
    "field,expected",
    [("abandoned", 1), ("ignored-advisories", 1), ("filter", 1), ("cooldown", 1), ("unreachable-repositories", 2)],
)
def test_composer_non_advisory_outcomes(sandbox, field, expected):
    root, env, _ = sandbox
    (root / "composer.json").write_text("{}")
    (root / "composer.lock").write_text("{}")
    env["CHECKER_FIXTURE_TOOLS"] = json.dumps(
        {"composer": {"code": 1, "stdout": json.dumps({"advisories": [], field: {"fixture": "review"}})}}
    )
    result = invoke(sandbox, "dependency_check.sh", "--tool", "composer", "--format", "json")
    assert result.returncode == expected
    assert json.loads(result.stdout)["complete"] is (expected == 1)


@pytest.mark.parametrize(
    "block",
    [
        {"found": True, "count": 0, "list": []},
        {"found": False, "count": 1, "list": []},
        {"found": False, "count": False, "list": []},
        {"found": 0, "count": 0, "list": []},
    ],
)
def test_cargo_contradictory_or_mistyped_counts_are_incomplete(sandbox, block):
    result = format_payload(sandbox, {"vulnerabilities": block}, "--format", "json")
    assert result.returncode == 1
    assert json.loads(result.stdout)["complete"] is False


def test_multiple_ecosystems_retain_findings_when_one_tool_fails(sandbox):
    root, env = configure(sandbox, npm={"code": 1, "stdout": json.dumps(npm_report())}, cargo={"code": 42})
    (root / "Cargo.toml").write_text("")
    (root / "Cargo.lock").write_text("")
    result = invoke(sandbox, "dependency_check.sh", "--format", "json")
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["summary"]["unfiltered_total"] == 1
    assert [tool["complete"] for tool in report["tools"]] == [True, False]


def test_output_file_is_private_atomic_and_leaves_stdout_empty(sandbox):
    root, _, _ = sandbox
    destination = root / "report.json"
    destination.write_text("old report")
    destination.chmod(0o644)
    result = format_payload(sandbox, {"vulnerabilities": []}, "--format", "json", "--output", str(destination))
    assert result.returncode == 0
    assert result.stdout == ""
    assert json.loads(destination.read_text())["complete"] is True
    assert destination.stat().st_mode & 0o777 == 0o600
    assert list(root.glob(".dependency-report-*")) == []


def test_output_symlink_does_not_overwrite_target(sandbox):
    root, _, _ = sandbox
    target = root / "target"
    target.write_text("preserve")
    link = root / "report.json"
    link.symlink_to(target)
    result = format_payload(sandbox, {"vulnerabilities": []}, "--format", "json", "--output", str(link))
    assert result.returncode == 1
    assert target.read_text() == "preserve"
    assert link.is_symlink()


def test_output_failure_does_not_become_clean(sandbox):
    root, _, _ = sandbox
    result = format_payload(sandbox, {"vulnerabilities": []}, "--output", str(root / "absent" / "report.json"))
    assert result.returncode == 1
    assert result.stdout == ""
    assert not (root / "absent").exists()


def test_csv_preserves_commas_quotes_and_neutralizes_formula_prefix(sandbox):
    import csv
    import io

    payload = {
        "vulnerabilities": [
            {"name": "=fictional,package", "description": 'Quoted "title", with comma', "severity": "high"}
        ]
    }
    result = format_payload(sandbox, payload, "--format", "csv", "--fail-on-findings")
    assert result.returncode == 1
    rows = list(csv.reader(io.StringIO(result.stdout)))
    assert rows[1][0] == "'=fictional,package"
    assert rows[1][4] == 'Quoted "title", with comma'


def test_terminal_and_markdown_payloads_are_rendered_as_data(sandbox):
    payload = {
        "vulnerabilities": [
            {"name": "fixture\x1b[31m", "description": "<script>fictional</script>|\x1b[2J", "severity": "high"}
        ]
    }
    result = format_payload(sandbox, payload, "--format", "markdown")
    assert result.returncode == 0
    assert "\x1b" not in result.stdout
    assert "<script>" not in result.stdout
    assert "&lt;script&gt;" in result.stdout
    assert "\\|" in result.stdout


def test_missing_declared_license_dependency_is_incomplete(sandbox):
    configure(sandbox, npm={"code": 0, "stdout": '{"dependencies": {}}'})
    result = invoke(sandbox, "license_compliance_checker.py", "--format", "json")
    assert result.returncode == 2
    assert json.loads(result.stdout)["summary"]["complete"] is False


def test_nested_license_metadata_is_not_omitted(sandbox):
    tree = {
        "dependencies": {
            "fixture-package": {
                "version": "1",
                "license": "MIT",
                "dependencies": {"nested": {"version": "2", "license": "Unknown"}},
            }
        }
    }
    configure(sandbox, npm={"code": 0, "stdout": json.dumps(tree)})
    result = invoke(sandbox, "license_compliance_checker.py", "--format", "json")
    assert result.returncode == 1
    assert json.loads(result.stdout)["summary"]["total_dependencies"] == 2


def test_python_inventory_never_guesses_an_environment(sandbox):
    root, _, calls = sandbox
    (root / "requirements.txt").write_text("fixture-package==1")
    result = invoke(sandbox, "license_compliance_checker.py", "--format", "json")
    assert result.returncode == 2
    assert not calls.exists()


def test_formatter_keeps_findings_exit_zero_unless_gate_requested(sandbox):
    result = format_payload(sandbox, npm_report(), "--format", "json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "findings"


def test_normalized_roundtrip_preserves_finding_details(sandbox):
    original = {
        "vulnerabilities": [
            {
                "name": "fictional",
                "severity": "high",
                "affected_range": "<2",
                "kind": "dependency-policy",
                "remediation": "Review actual advisory",
                "source_id": "FIXTURE-1",
            }
        ]
    }
    first = format_payload(sandbox, original, "--format", "json")
    second = format_payload(sandbox, json.loads(first.stdout), "--format", "json")
    assert first.returncode == second.returncode == 0
    assert json.loads(first.stdout)["vulnerabilities"] == json.loads(second.stdout)["vulnerabilities"]


def test_markdown_does_not_create_links_or_inline_instructions_from_titles(sandbox):
    result = format_payload(
        sandbox,
        {
            "vulnerabilities": [
                {
                    "name": "fictional",
                    "description": "[click](https://example.invalid/) ![track](https://example.invalid/image) `code`",
                    "severity": "high",
                }
            ]
        },
        "--format",
        "markdown",
    )
    assert result.returncode == 0
    assert "\\[click\\]" in result.stdout
    assert "\\`code\\`" in result.stdout


def test_legacy_empty_pip_report_is_complete_in_selected_pip_scope(sandbox):
    root, env, _ = sandbox
    (root / "requirements.txt").write_text("")
    env["CHECKER_FIXTURE_TOOLS"] = json.dumps({"pip-audit": {"code": 0, "stdout": "[]"}})
    result = invoke(sandbox, "dependency_check.sh", "--tool", "pip", "--format", "json")
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["complete"] is True


@pytest.mark.parametrize("counts", [{"total": 0, "high": 1}, {"total": True}, {"total": -1}])
def test_npm_invalid_or_contradictory_severity_counts(sandbox, counts):
    result = format_payload(
        sandbox, {"metadata": {"vulnerabilities": counts}, "vulnerabilities": {}}, "--format", "json"
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["complete"] is False


@pytest.mark.parametrize("field,size", [("stdout_repeat", 32 * 1024 * 1024 + 1), ("stderr_repeat", 1024 * 1024 + 1)])
def test_engine_output_limit_is_incomplete_without_echoing_output(sandbox, field, size):
    configure(sandbox, npm={"code": 0, field: size})
    result = invoke(sandbox, "dependency_check.sh", "--tool", "npm", "--format", "json")
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["complete"] is False
    assert len(result.stdout) < 10000
    assert result.stderr == ""


@pytest.mark.parametrize(
    "summary",
    [
        {"total": 0, "unfiltered_total": 1, "hidden_by_filter": 0},
        {"total": False, "unfiltered_total": 0, "hidden_by_filter": 0},
        {"total": 0, "unfiltered_total": 0, "hidden_by_filter": -1},
    ],
)
def test_normalized_inconsistent_counts_do_not_clear_gate(sandbox, summary):
    payload = {"schema_version": 1, "complete": True, "summary": summary, "vulnerabilities": []}
    result = format_payload(sandbox, payload, "--format", "json", "--fail-on-findings")
    assert result.returncode == 1
    assert json.loads(result.stdout)["complete"] is False
