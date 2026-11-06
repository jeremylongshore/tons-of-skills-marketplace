"""Cost plans never turn absent prices or fabricated receipts into execution authority."""

import copy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "plugins/saas-packs/coreweave-pack/shared/review-cost-plan.py"
spec = importlib.util.spec_from_file_location("cw_gate", PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
NOW = datetime(2026, 11, 5, 12, tzinfo=timezone.utc)


def plan():
    return {
        "schema": "coreweave-cost-plan/v1",
        "owner": "fixture-owner",
        "organization": "fixture-org",
        "context": "fixture-cks",
        "namespace": "fixture",
        "currency": "USD",
        "rate_source": "synthetic fixture; not a vendor price",
        "valid_from": "2026-11-05T11:00:00Z",
        "expires_at": "2026-11-05T13:00:00Z",
        "all_charge_categories_reviewed": True,
        "budget_ceiling": "20",
        "resources": [
            {
                "id": "fixture/job/smoke",
                "kind": "Job",
                "name": "smoke",
                "action": "create",
                "artifact_sha256": "a" * 64,
                "gpu_type": "fixture-gpu",
                "gpu_count": 2,
                "gpu_hourly_rate": "1.25",
                "duration_hours": 4,
                "other_charges": [{"category": "storage", "basis": "fixture", "amount": "0.50"}],
                "teardown_command": "kubectl --context=fixture-cks -n fixture delete job smoke",
                "retained_data": "retain existing volumes",
            }
        ],
    }


def approval(p):
    return {
        "plan_sha256": gate.digest(p),
        "approver": p["owner"],
        "decision": "confirm",
        "confirmed_at": "2026-11-05T11:30:00Z",
    }


def test_cost_includes_other_charges_without_auto_authorization():
    r = gate.review(plan(), now=NOW)
    assert r["estimated_total"] == "10.50"
    assert r["status"] == "needs_human_confirmation"
    assert r["resources"][0]["gpu_count"] == 2


def test_matching_receipt_is_not_authenticated_authority():
    p = plan()
    r = gate.review(p, approval(p), NOW)
    assert r["status"] == "supplied_confirmation_matches"
    assert "not authorization" in r["authority"]


@pytest.mark.parametrize(
    "key",
    [
        "gpu_count",
        "gpu_hourly_rate",
        "duration_hours",
        "other_charges",
        "teardown_command",
        "retained_data",
        "artifact_sha256",
    ],
)
def test_missing_resource_input_blocks(key):
    p = plan()
    del p["resources"][0][key]
    with pytest.raises(ValueError):
        gate.review(p, now=NOW)


@pytest.mark.parametrize("bad", [None, True, "NaN", "-1", "Infinity", "1e100", "not a rate"])
def test_invalid_rate_blocks(bad):
    p = plan()
    p["resources"][0]["gpu_hourly_rate"] = bad
    with pytest.raises(ValueError):
        gate.review(p, now=NOW)


@pytest.mark.parametrize("field,value", [("context", "other"), ("namespace", "other"), ("budget_ceiling", "19")])
def test_target_or_budget_change_invalidates_receipt(field, value):
    p = plan()
    a = approval(p)
    p[field] = value
    with pytest.raises(ValueError):
        gate.review(p, a, NOW)


def test_artifact_change_invalidates_receipt():
    p = plan()
    a = approval(p)
    p["resources"][0]["artifact_sha256"] = "b" * 64
    with pytest.raises(ValueError):
        gate.review(p, a, NOW)


@pytest.mark.parametrize("mutation", ["expired", "overbudget", "duplicate", "unreviewed", "wrong-owner", "denied"])
def test_plan_and_approval_fail_closed(mutation):
    p = plan()
    a = approval(p)
    if mutation == "expired":
        p["expires_at"] = "2026-11-05T11:59:59Z"
    if mutation == "overbudget":
        p["budget_ceiling"] = 9
    if mutation == "duplicate":
        p["resources"].append(copy.deepcopy(p["resources"][0]))
    if mutation == "unreviewed":
        p["all_charge_categories_reviewed"] = False
    if mutation == "wrong-owner":
        a["approver"] = "not-owner"
    if mutation == "denied":
        a["decision"] = "deny"
    with pytest.raises(ValueError):
        gate.review(p, a if mutation in ("wrong-owner", "denied") else None, NOW)


def test_duplicate_json_and_cli_error_do_not_echo_input(tmp_path):
    f = tmp_path / "plan.json"
    f.write_text('{"schema":"secret-canary", "schema":"second"}')
    r = subprocess.run([sys.executable, str(PATH), "--plan", str(f)], capture_output=True, text=True)
    assert r.returncode == 2
    assert "secret-canary" not in r.stdout + r.stderr
    assert json.loads(r.stdout)["status"] == "blocked"


def test_installed_cost_gate_copies_are_identical():
    r = subprocess.run(
        [sys.executable, str(PATH.parents[1] / "scripts/sync-cost-gates.py"), "--check"], capture_output=True
    )
    assert r.returncode == 0, r.stdout
