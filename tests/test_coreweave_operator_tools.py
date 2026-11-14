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


# ---------------------------------------------------------------------------
# Round 2 accuracy regressions (#1732): formats seen in public NCCL / Xid logs.
# ---------------------------------------------------------------------------
NCCL_222_TCP = """node0:101:101 [0] NCCL INFO NET/IB : No device found.
node0:101:101 [0] NCCL INFO NET/IB : Using [RO]; OOB eth0:10.0.0.4<0>
node0:101:101 [0] NCCL INFO NET/Socket : Using [0]eth0:10.0.0.4<0>
node0:101:101 [0] NCCL INFO Using network Socket
"""


def test_nccl_222_tcp_fallback_is_socket_not_mixed():
    result = fabric.diagnose(NCCL_222_TCP)
    assert result["transport"] == "Socket"
    assert result["rdma_engaged"] == "no"


def test_nccl_ib_requires_a_real_device():
    result = fabric.diagnose("NCCL INFO NET/IB : Using [0]mlx5_0:1/IB [1]mlx5_1:1/IB ; OOB ib0:10.0.0.1<0>")
    assert result["transport"] == "IB"
    roce = fabric.diagnose("NCCL INFO NET/IB : Using [0]mlx5_0:1/RoCE ; OOB eth0:10.0.0.1<0>")
    assert roce["transport"] == "IB"


def test_unprefixed_pasted_nccl_lines_are_read():
    assert fabric.diagnose("NET/IB : Using [0]mlx5_0:1/IB ; OOB ib0:10.0.0.1<0>")["transport"] == "IB"
    assert fabric.diagnose("[0] Using network Socket")["transport"] == "Socket"


def test_ib_disable_set_by_environment_is_recognised():
    result = fabric.diagnose("NCCL INFO NCCL_IB_DISABLE set by environment to 1.\nNCCL INFO Using network Socket")
    assert result["transport"] == "Socket"
    assert any("NCCL_IB_DISABLE" in item for item in result["missing_conditions"])


@pytest.mark.parametrize(
    "log",
    [
        "NCCL INFO Using network IBext_v8",
        "NCCL INFO Using network IBext_v6",
        "NCCL INFO NET/IBext : Using [0]mlx5_0:1/IB ; OOB ib0:10.0.0.1<0>",
        "NCCL INFO NET/IBext_v8 : Using [0]mlx5_0:1/IB ; OOB ib0:10.0.0.1<0>",
    ],
)
def test_external_ib_plugins_are_ib(log):
    assert fabric.diagnose(log)["transport"] == "IB"


def test_external_ib_plugin_gdrdma_is_detected():
    result = fabric.diagnose(
        "NCCL INFO Using network IBext_v8\nNCCL INFO Channel 00/0 : 0[0] -> 8[0] [send] via NET/IBext_v8/0/GDRDMA"
    )
    assert result["gpu_direct_rdma_confirmed"]


def test_single_node_run_reports_rdma_not_applicable():
    log = (
        "NCCL INFO Using network IB\n"
        "NCCL INFO Channel 00/0 : 0[0] -> 1[1] via P2P/IPC\n"
        "NCCL INFO comm 0x55 rank 0 nranks 8 cudaDev 0 nvmlDev 0 busId 1b000 commId 0xab - Init COMPLETE\n"
        "NCCL INFO ncclCommInitRank comm 0x55 rank 0 nRanks 8 nNodes 1 localRanks 8 localRank 0 MNNVL 0\n"
    )
    assert fabric.diagnose(log)["rdma_engaged"] == "not-applicable"


def test_multi_node_run_is_not_single_node():
    log = "NCCL INFO Using network IB\nNCCL INFO Channel 00/0 : 0[0] -> 8[0] [send] via NET/IB/0/GDRDMA"
    assert fabric.diagnose(log)["rdma_engaged"] == "yes"


def test_kubectl_describe_state_is_not_an_ib_port():
    describe = "Containers:\n  trainer:\n    State:          Waiting\n      Reason:       ContainerCreating\n"
    assert fabric.detect_ibstat(describe) == ("absent", [])


def test_ibstat_port_block_is_still_read():
    ibstat = "CA 'mlx5_0'\n\tCA type: MT4123\n\tPort 1:\n\t\tState: Down\n\t\tPhysical state: Polling\n"
    status, notes = fabric.detect_ibstat(ibstat)
    assert status == "down" and notes


XID_154_RESET = (
    "NVRM: Xid (PCI:0000:01:00): 154, GPU recovery action changed from 0x0 (None) to 0x1 (GPU Reset Required)"
)
XID_154_REBOOT = (
    "NVRM: Xid (PCI:0000:01:00): 154, GPU recovery action changed from 0x0 (None) to 0x2 (Node Reboot Required)"
)


def test_xid_154_recovery_action_sets_verdict():
    assert triage.triage_from_blob(XID_154_RESET)["action"] == "reset-gpu"
    assert triage.triage_from_blob(XID_154_REBOOT)["action"] == "reboot-node"


def test_xid_154_recovery_action_governs_co_occurring_codes():
    blob = "NVRM: Xid (PCI:0000:01:00): 94, pid=1, Contained: SM\n" + XID_154_REBOOT
    result = triage.triage_from_blob(blob)
    assert result["action"] == "reboot-node"
    assert 94 in result["co_occurring_xids"]


@pytest.mark.parametrize("unknown", [145, 999])
def test_unknown_code_does_not_override_known_code(unknown):
    blob = f"NVRM: Xid (PCI:0000:01:00): {unknown}, x\nNVRM: Xid (PCI:0000:01:00): 94, Contained"
    assert triage.triage_from_blob(blob)["xid"] == 94


def test_xid_64_is_reset_and_support_not_rma():
    result = triage.classify_xid(64)
    assert result["action"] == "reset-gpu"
    assert "support" in result["why"].lower()


def test_remap_failure_alone_does_not_recommend_rma():
    result = triage.apply_remap_override(triage.classify_xid(64), pending=False, remap_failure=True)
    assert result["action"] != "rma"
    assert "field diagnostic" in result["why"].lower()


def test_xid_45_is_follow_on_not_governing():
    blob = "NVRM: Xid (PCI:0000:01:00): 45, pid=1, Ch 00000010\nNVRM: Xid (PCI:0000:01:00): 31, pid=1, MMU Fault"
    result = triage.triage_from_blob(blob)
    assert result["xid"] == 31
    assert 45 in result["co_occurring_xids"]


def test_xid_45_alone_points_at_fabric_manager():
    result = triage.classify_xid(45)
    assert "fabric manager" in result["why"].lower()


def test_remapped_rows_section_from_real_nvidia_smi_is_read():
    dump = (
        "    Remapped Rows\n"
        "        Correctable Error                 : 0\n"
        "        Uncorrectable Error               : 1\n"
        "        Pending                           : Yes\n"
        "        Remapping Failure Occurred        : No\n"
    )
    assert triage.parse_blob(dump)["pending"] is True
    assert triage.triage_from_blob("Xid 63\n" + dump)["action"] == "reset-gpu"


def test_multi_gpu_without_pci_prefix_is_split():
    blob = "NVRM: Xid (0000:03:00): 94, Contained\nNVRM: Xid (0000:04:00): 79, fallen off the bus"
    assert triage.triage_from_blob(blob)["classification"] == "Multiple GPU identities in input"


@pytest.mark.parametrize("blob", ["XID 79 detected", "event Xid=79", "nvrm: xid (PCI:0000:04:00): 79, off the bus"])
def test_xid_code_extraction_is_case_and_separator_tolerant(blob):
    assert triage.parse_blob(blob)["xids"] == [79]


def test_redacted_pci_tag_still_yields_code():
    assert triage.parse_blob("NVRM: Xid (PCI:<redacted>): 79, GPU has fallen off the bus")["xids"] == [79]
    assert triage.parse_blob("NVRM: Xid [REDACTED]: 79, GPU has fallen off the bus")["xids"] == [79]
    assert triage.parse_blob("NVRM: Xid ...: 13, Graphics Exception")["xids"] == [13]
