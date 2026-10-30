"""Local CLI regressions for ROE gates and scope handoff artifacts.

Only fictional files are used. No scanner, signature tool, DNS or network call.
"""

from __future__ import annotations

from copy import deepcopy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

from lib.engagement import classify_target, load_mapping, parse_timestamp, scope_contains, scopes_overlap

PACK = Path(__file__).resolve().parents[1]


def load_script(skill: str, name: str):
    spec = importlib.util.spec_from_file_location(name, PACK / "skills" / skill / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def authz():
    return load_script("confirming-pentest-authorization", "check_authorization")


@pytest.fixture
def scope():
    return load_script("defining-pentest-scope", "define_scope")


@pytest.fixture
def roe(sample_roe_dict):
    data = deepcopy(sample_roe_dict)
    data["signature_block"]["signed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    return data


def run_auth(authz, tmp_path, data, extra=()):
    path = tmp_path / "fictional-roe.json"
    path.write_text(json.dumps(data))
    allowed = tmp_path / "allowed"
    allowed.write_text("jane.doe@example.test\n")
    return authz.main(["--roe", str(path), "--allowed", str(allowed), "--format", "json", *extra])


def run_scope(scope, tmp_path, data, extra=()):
    path = tmp_path / "fictional-scope.json"
    path.write_text(json.dumps(data))
    return scope.main(["--roe", str(path), "--format", "json", *extra])


@pytest.mark.parametrize("field", ["authorizer", "time_window", "signature_block", "emergency_contact"])
@pytest.mark.parametrize("value", ["not-a-mapping", ["not-a-mapping"], True])
def test_required_block_types_fail(authz, tmp_path, roe, field, value, capsys):
    roe[field] = value
    assert run_auth(authz, tmp_path, roe) != 0
    assert any(f["severity"] == "critical" for f in json.loads(capsys.readouterr().out))


@pytest.mark.parametrize("value", ["not-a-time", "2026-01-01T00:00:00", "2026-01-01", 42, None])
def test_invalid_window_times_fail(authz, tmp_path, roe, value):
    roe["time_window"]["start"] = value
    assert run_auth(authz, tmp_path, roe) != 0


def test_window_order_fails(authz, tmp_path, roe):
    roe["time_window"] = {"start": "2099-01-02T00:00:00Z", "end": "2099-01-01T00:00:00Z"}
    assert run_auth(authz, tmp_path, roe) != 0


def test_display_filter_cannot_hide_expiry_from_exit_code(authz, tmp_path, roe, capsys):
    roe["time_window"] = {"start": "1999-01-01T00:00:00Z", "end": "2000-01-01T00:00:00Z"}
    assert run_auth(authz, tmp_path, roe, ["--min-severity", "critical"]) == 1
    assert json.loads(capsys.readouterr().out) == []


@pytest.mark.parametrize(
    "target, permitted", [("api.example.test", True), ("notexample.test", False), ("example.test", False)]
)
def test_wildcard_label_boundary(authz, tmp_path, roe, target, permitted):
    roe["in_scope_targets"] = ["*.example.test"]
    roe["out_of_scope_targets"] = []
    assert (run_auth(authz, tmp_path, roe, ["--check-target", target]) == 0) is permitted


def test_exclusion_overrides_wildcard_inclusion(authz, tmp_path, roe):
    roe["in_scope_targets"] = ["*.example.test"]
    roe["out_of_scope_targets"] = ["payments.example.test"]
    assert run_auth(authz, tmp_path, roe, ["--check-target", "payments.example.test"]) == 1


def test_requested_range_may_not_include_excluded_subnet(authz, tmp_path, roe):
    roe["in_scope_targets"] = ["203.0.113.0/24"]
    roe["out_of_scope_targets"] = ["203.0.113.128/25"]
    assert run_auth(authz, tmp_path, roe, ["--check-target", "203.0.113.0/24"]) == 1


def test_requested_allowlist_must_exist(authz, tmp_path, roe):
    assert run_auth(authz, tmp_path, roe, ["--allowed", str(tmp_path / "missing")]) != 0


def test_default_missing_allowlist_does_not_claim_identity_verification(authz, tmp_path, roe, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "roe.json"
    path.write_text(json.dumps(roe))
    assert authz.main(["--roe", str(path), "--format", "json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert any(f["title"] == "Signer allowlist not provided" for f in report)
    assert not any(f["title"] == "engagement is authorized" for f in report)


@pytest.mark.parametrize(
    "target", ["same.example.test", "aws:123456789012", "okta:example", "https://app.example.test/private"]
)
def test_literal_exclusions_block_artifact_creation(scope, tmp_path, target):
    allow, targets = tmp_path / "allowed.txt", tmp_path / "targets.json"
    assert (
        run_scope(
            scope,
            tmp_path,
            {"in_scope_targets": [target], "out_of_scope_targets": [target]},
            ["--emit-allowlist", str(allow), "--emit-targets", str(targets)],
        )
        == 1
    )
    assert not allow.exists() and not targets.exists()


def test_failed_overlap_preserves_previous_handoff(scope, tmp_path):
    allow, targets = tmp_path / "allowed.txt", tmp_path / "targets.json"
    allow.write_text("previous-approved\n")
    targets.write_text("previous-approved\n")
    data = {"in_scope_targets": ["203.0.113.0/24"], "out_of_scope_targets": ["203.0.113.128/25"]}
    assert (
        run_scope(
            scope,
            tmp_path,
            data,
            ["--min-severity", "critical", "--emit-allowlist", str(allow), "--emit-targets", str(targets)],
        )
        == 1
    )
    assert allow.read_text() == targets.read_text() == "previous-approved\n"


@pytest.mark.parametrize("target", ["::/0", "0.0.0.0/0"])
def test_unbounded_scope_is_not_emitted(scope, tmp_path, target):
    allow = tmp_path / "allow.txt"
    assert run_scope(scope, tmp_path, {"in_scope_targets": [target]}, ["--emit-allowlist", str(allow)]) == 1
    assert not allow.exists()


def test_unsupported_exclusion_cannot_be_ignored(scope, tmp_path):
    assert (
        run_scope(
            scope,
            tmp_path,
            {"in_scope_targets": ["app.example.test"], "out_of_scope_targets": [{"unsupported": "entry"}]},
        )
        == 1
    )


def test_missing_extension_fails(scope, tmp_path, roe):
    assert run_scope(scope, tmp_path, roe, ["--extension", str(tmp_path / "missing.json")]) != 0


def test_unsigned_unreferenced_extension_fails(scope, tmp_path, roe):
    extension = tmp_path / "extension.json"
    extension.write_text(json.dumps({"in_scope_targets": ["extra.example.test"]}))
    assert run_scope(scope, tmp_path, roe, ["--extension", str(extension)]) != 0


def test_valid_structural_extension_adds_only_declared_targets(scope, tmp_path, roe):
    extension = tmp_path / "extension.json"
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    extension.write_text(
        json.dumps(
            {
                "amendment_id": "AMEND-1",
                "amendment_to": roe["engagement_id"],
                "amendment_date": now,
                "signature_block": roe["signature_block"],
                "in_scope_targets": ["extra.example.test"],
            }
        )
    )
    targets = tmp_path / "targets.json"
    assert run_scope(scope, tmp_path, roe, ["--extension", str(extension), "--emit-targets", str(targets)]) == 0
    assert "extra.example.test" in [x["normalized"] for x in json.loads(targets.read_text())]


def test_valid_scope_emits_bounded_handoff(scope, tmp_path):
    allow = tmp_path / "allow.txt"
    assert run_scope(scope, tmp_path, {"in_scope_targets": ["203.0.113.12/24"]}, ["--emit-allowlist", str(allow)]) == 0
    assert allow.read_text() == "203.0.113.0/24\n"


@pytest.mark.parametrize(
    "entry",
    [
        {"url": "example.test"},
        {"host": "203.0.113.0/24"},
        {"host": "app.example.test", "cidr": "203.0.113.0/24"},
        "*.127.0.0.1",
    ],
)
def test_ambiguous_target_forms_are_rejected(entry):
    assert classify_target(entry)[2] is None


def test_url_path_scope_uses_segment_boundaries():
    assert scope_contains("https://app.example.test/api", "https://app.example.test/api/item")
    assert not scope_contains("https://app.example.test/api", "https://app.example.test/api-other")
    assert not scope_contains("https://app.example.test/api", "https://app.example.test/api/%2e%2e/private")
    assert scopes_overlap("*.example.test", "https://app.example.test/private")


def test_invalid_timestamp_overflow_is_a_failed_parse():
    assert parse_timestamp("9999-12-31T23:59:59-12:00") is None


def test_json_remains_available_without_yaml(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "yaml", None)
    path = tmp_path / "roe.json"
    path.write_text('{"engagement_id":"FICTIONAL"}')
    assert load_mapping(path) == {"engagement_id": "FICTIONAL"}
    path.write_text("engagement_id: FICTIONAL\n")
    with pytest.raises(ValueError, match="PyYAML"):
        load_mapping(path)


@pytest.mark.parametrize("checker", ["authorization", "scope"])
def test_process_exit_blocks_handoff_even_with_display_filter(tmp_path, roe, checker):
    if checker == "authorization":
        skill, script = "confirming-pentest-authorization", "check_authorization.py"
        roe["time_window"] = {"start": "1999-01-01T00:00:00Z", "end": "2000-01-01T00:00:00Z"}
    else:
        skill, script = "defining-pentest-scope", "define_scope.py"
        roe["out_of_scope_targets"] = deepcopy(roe["in_scope_targets"])
    path = tmp_path / "roe.json"
    path.write_text(json.dumps(roe))
    result = subprocess.run(
        [
            sys.executable,
            str(PACK / "skills" / skill / "scripts" / script),
            "--roe",
            str(path),
            "--format",
            "json",
            "--min-severity",
            "critical",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert isinstance(json.loads(result.stdout), list)
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("mode", ["empty", "dangling", "unreadable"])
def test_existing_default_signer_file_cannot_silently_disable_identity_check(authz, tmp_path, roe, monkeypatch, mode):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "roe.json"
    path.write_text(json.dumps(roe))
    signer_file = tmp_path / ".allowed-authorizers"
    if mode == "empty":
        signer_file.write_text("")
    elif mode == "dangling":
        signer_file.symlink_to(tmp_path / "missing-target")
    else:

        def denied(_path):
            raise PermissionError("fictional denied read")

        monkeypatch.setattr(authz, "load_allowed", denied)
    assert authz.main(["--roe", str(path), "--format", "json"]) == 2


def test_multiple_trailing_dns_dots_are_not_normalized_into_permission():
    assert classify_target("app.example.test..")[2] is None
