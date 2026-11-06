"""Offline operator regressions: bad evidence must not become health or billing certainty."""

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins/saas-packs/coreweave-pack/skills"


def module(name, skill, filename):
    path = SKILLS / skill / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


fabric = module("cw_fabric_review", "coreweave-fabric-diagnostics", "fabric-check.py")
triage = module("cw_xid_review", "coreweave-gpu-node-forensics", "triage.py")
cost = module("cw_cost_review", "coreweave-gpu-cost-leak-hunter", "rank-and-report.py")


def finding(**values):
    return dict(
        category="Idle-looking allocation",
        root_cause="Phase not verified",
        fix="Review owner evidence",
        usage_gpu_hours=100,
        rate_usd_per_gpu_hour=2,
        **values,
    )


@pytest.mark.parametrize(
    "resources",
    [
        "resources: {limits: {rdma/ib: 1}}",
        "resources: {limits: {rdma/ib: 1.0}}",
        "resources:\n  limits:\n    rdma/ib: 1\n",
        'resources: {requests: {rdma/ib: "1"}, limits: {rdma/ib: "1"}}',
    ],
)
def test_rdma_limit_defaults_request(resources):
    assert fabric.resource_findings(resources) == ([], True)


@pytest.mark.parametrize(
    "resources",
    [
        "resources: {requests: {rdma/ib: 1}}",
        "resources: {limits: {rdma/ib: 0}}",
        "resources: {limits: {rdma/ib: true}}",
        "resources: {limits: {rdma/ib: 1}, requests: {rdma/ib: 0}}",
        "resources: {limits: [1]}",
        "resources: [",
    ],
)
def test_invalid_rdma_resource_is_not_accepted(resources):
    assert fabric.resource_findings(resources)[0]


def test_resources_are_not_merged_between_containers():
    text = """spec:
  containers:
  - name: trainer
    resources:
      requests: {rdma/ib: 1}
  - name: sidecar
    resources:
      limits: {rdma/ib: 1}
"""
    problems, seen = fabric.resource_findings(text)
    assert seen and len(problems) == 1


@pytest.mark.parametrize(
    "log",
    [
        "NCCL WARN NET/IB : ibv_open_device failed",
        "NCCL INFO Bootstrap : Using eth0:10.0.0.1",
        "GDRDMA not enabled",
        "# resources: {limits: {rdma/ib: 1}}",
    ],
)
def test_no_positive_transport_means_unknown(log):
    result = fabric.diagnose(log)
    assert result["transport"] == "unknown"
    assert not result["gpu_direct_rdma_confirmed"]


def test_ib_and_gdr_are_separate_signals():
    assert not fabric.diagnose("NCCL INFO Using network IB")["gpu_direct_rdma_confirmed"]
    result = fabric.diagnose("NCCL INFO Using network IB\nNCCL INFO NET/IB : GPU Direct RDMA Enabled")
    assert result["gpu_direct_rdma_confirmed"]


def test_mixed_runs_remain_qualified():
    result = fabric.diagnose("NCCL INFO Using network IB\nNCCL INFO Using network Socket")
    assert result["transport"] == "mixed"
    assert "separate ranks" in result["verdict"]


def test_inactive_port_is_not_active_substring():
    assert fabric.detect_ibstat("State: Inactive\nPhysical state: Polling")[0] == "down"


def test_unknown_xid_does_not_trigger_reset():
    result = triage.classify_xid(999)
    assert result["action"] == "investigate" and result["confidence"] == "low"
    assert result["recommendation_only"]


@pytest.mark.parametrize("xid", [13, 31, 43, 45, 48, 64, 74, 79, 94, 95, 119, 120])
def test_xid_recommendations_require_platform_confirmation(xid):
    result = triage.classify_xid(xid)
    assert result["requires_confirmation"] and result["recommendation_only"]
    if result["action"] in triage._HARDWARE_ACTIONS:
        assert "Do NOT manually uncordon" in result["cordon_rule"]


def test_xid_containment_is_not_global_health():
    result = triage.classify_xid(94)
    assert result["action"] == "reschedule"
    assert "not proof the node is healthy" in result["why"]
    assert triage.classify_xid(95)["action"] == "reset-gpu"


def test_multi_gpu_evidence_not_combined():
    result = triage.triage_from_blob("NVRM: Xid (PCI:0000:3b:00): 94\nNVRM: Xid (PCI:0000:65:00): 79")
    assert result["action"] == "investigate"


def test_remap_does_not_soften_pcie_bus_failure():
    result = triage.apply_remap_override(triage.classify_xid(79), True, False)
    assert result["action"] == "reboot-node"
    assert result["unverified"]


def test_unrelated_pending_field_does_not_infer_reset():
    result = triage.triage_from_blob("Xid 63\nOther subsystem\n    Pending: Yes")
    assert result["action"] == "watch"


@pytest.mark.parametrize("value", [None, True, -1, "NaN", "Infinity", "unknown", "1e309"])
def test_invalid_financial_data_is_not_zero(value):
    with pytest.raises(ValueError):
        cost.parse_usd(value)


def test_missing_kind_defaults_to_estimate():
    report = cost.build_report([finding()], None, "2026-11-05")
    assert "Telemetry and pricing estimates" in report
    assert "Billing-backed supplied amounts" not in report
    assert "do not add them together" in report


@pytest.mark.parametrize(
    "changes",
    [
        {"kind": "confirmed"},
        {"kind": "confirmed", "billing_evidence": "owner-reference"},
        {"kind": "certain"},
        {"discount_frac": 1.1},
        {"discount_frac": 0.1, "reprice_rate_usd_per_gpu_hour": 1},
        {"waste_30d_usd": 5, "discount_frac": 0.1},
    ],
)
def test_unsupported_financial_claim_is_rejected(changes):
    with pytest.raises(ValueError):
        cost.build_report([finding(**changes)], None, "2026-11-05")


def test_confirmed_amount_requires_direct_amount_and_evidence():
    report = cost.build_report(
        [finding(kind="confirmed", waste_30d_usd=200, billing_evidence="reviewed invoice row")], None, None
    )
    assert "Billing-backed supplied amounts" in report
    assert "not independent verification" in report


@pytest.mark.parametrize("raw", ["{}", "null", '{"leaks": {}}', '{"categories": 1}'])
def test_bad_report_shape_does_not_become_empty_findings(raw):
    with pytest.raises(ValueError):
        cost._load(raw)


def test_invalid_cost_cli_preserves_previous_report(tmp_path):
    output = tmp_path / "report.md"
    output.write_text("last good report")
    proc = subprocess.run(
        [sys.executable, cost.__file__, "--out", str(output)],
        input=json.dumps([finding(kind="confirmed")]),
        text=True,
        capture_output=True,
    )
    assert proc.returncode != 0 and output.read_text() == "last good report"


def test_report_cells_cannot_inject_html_or_table_rows():
    row = finding()
    row["category"] = "<script>bad</script>|extra\nrow"
    report = cost.build_report([row], None, None)
    assert "<script>" not in report and "&#124;" in report


def test_ci_deploy_secret_cleanup_on_failed_rollout(tmp_path):
    source = (SKILLS / "coreweave-ci-integration/SKILL.md").read_text()
    workflow = yaml.load(re.search(r"```yaml\n(.*?)```", source, re.S).group(1), Loader=yaml.BaseLoader)
    staging = workflow["jobs"]["staging"]
    assert staging["environment"] == "coreweave-staging"
    assert "github.event_name == 'push'" in staging["if"]
    assert "github.ref == 'refs/heads/main'" in staging["if"]
    for step in workflow["jobs"]["unit-tests"]["steps"]:
        assert "secrets." not in json.dumps(step)
    deploy = next(step for step in staging["steps"] if step.get("name") == "Apply approved staging manifest")
    executable = tmp_path / "kubectl"
    executable.write_text("""#!/usr/bin/env python3
import os,stat,sys
from pathlib import Path
p=Path(os.environ['KUBECONFIG'])
assert stat.S_IMODE(p.stat().st_mode)==0o600
assert p.read_text()=='fixture-credential'
assert '--context=fixture-context' in sys.argv
assert '--namespace=fixture-namespace' in sys.argv
raise SystemExit(7 if 'rollout' in sys.argv else 0)
""")
    executable.chmod(0o700)
    env = {
        **os.environ,
        "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"],
        "RUNNER_TEMP": str(tmp_path),
        "KUBECONFIG_B64": "Zml4dHVyZS1jcmVkZW50aWFs",
        "CW_CONTEXT": "fixture-context",
        "CW_NAMESPACE": "fixture-namespace",
        "CW_DEPLOYMENT": "fixture-app",
    }
    proc = subprocess.run(["bash", "-c", deploy["run"]], env=env, text=True, capture_output=True)
    assert proc.returncode == 7
    assert not list(tmp_path.glob("coreweave-kubeconfig.*"))
    assert "fixture-credential" not in proc.stdout + proc.stderr


@pytest.mark.parametrize("value", ["1,2", "$$3", "1$2", "1,000,00"])
def test_malformed_currency_does_not_change_magnitude(value):
    with pytest.raises(ValueError):
        cost.parse_usd(value)


@pytest.mark.parametrize(
    "args", [["--xid", "94", "--pending", "maybe"], ["--xid", "-1"], ["--pending", "yes", "--blob", "-"]]
)
def test_ambiguous_cli_flags_are_rejected(args):
    result = subprocess.run([sys.executable, triage.__file__, *args], input="Xid 94", text=True, capture_output=True)
    assert result.returncode != 0
    assert not result.stdout.strip()
