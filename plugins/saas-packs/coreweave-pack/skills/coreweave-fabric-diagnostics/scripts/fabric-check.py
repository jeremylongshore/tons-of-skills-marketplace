#!/usr/bin/env python3
"""Offline NCCL evidence review; transport observations are not a universal health verdict.

CoreWeave documents rdma/ib in limits; Kubernetes defaults omitted requests from
limits. Inspect each resources block independently, including YAML flow mappings.
Requires PyYAML. No cluster commands, drivers, benchmarks or mutations are executed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation

import yaml


# NCCL net plugin names: built-in IB plus external IBext / IBext_vN (SHARP/COLLNET).
_IB_NET = r"IB(?:ext(?:_v\d+)?)?"
# NCCL >= 2.22 prints "NET/IB : Using [RO]; OOB <if>" with an EMPTY device list on TCP
# fallback, so IB selection needs a real "[n]dev:port/IB|RoCE" device entry.
_IB_SELECTED = re.compile(
    rf"Using network {_IB_NET}\b|NET/{_IB_NET}\s*:\s*Using\s+\[\d+\]\S+:\d+/(?:IB|RoCE)\b|via NET/{_IB_NET}/",
    re.I,
)
_SOCKET_SELECTED = re.compile(r"Using network Socket\b|NET/Socket\s*:\s*Using\b|via NET/Socket/", re.I)
_GDR = re.compile(rf"GPU Direct RDMA Enabled\b|via NET/{_IB_NET}/\S*/GDRDMA\b", re.I)
_IB_FAILURE = re.compile(rf"\b(?:WARN|ERROR)\b.*?(?:ibv_|NET/{_IB_NET}\b)", re.I)
_IB_DISABLED = re.compile(r"NCCL_IB_DISABLE\s+set by environment to\s+1\b|NCCL_IB_DISABLE\s*[:=]\s*[\'\"]?1\b", re.I)
_NET_CHANNEL = re.compile(r"\bvia NET/", re.I)
_LOCAL_CHANNEL = re.compile(r"\bvia (?:P2P|SHM)\b", re.I)
_NNODES = re.compile(r"\bnNodes\s+(\d+)\b", re.I)


def detect_transport(text: str) -> tuple[str, bool, bool]:
    # Pasted logs often lose the "host:pid [rank] NCCL INFO" prefix, so every line
    # is read; WARN/ERROR lines never count as positive transport evidence.
    lines = text.splitlines()
    info = [line for line in lines if not re.search(r"\b(?:WARN|ERROR)\b", line, re.I)]
    ib = any(_IB_SELECTED.search(line) for line in info)
    socket = any(_SOCKET_SELECTED.search(line) for line in info)
    gdr = any(_GDR.search(line) for line in info)
    failed = any(_IB_FAILURE.search(line) for line in lines)
    return ("mixed" if ib and socket else "IB" if ib else "Socket" if socket else "unknown", gdr, failed)


def detect_single_node(text: str) -> bool:
    """True when the log shows no inter-node traffic: nNodes 1, or only P2P/SHM channels."""
    if _NET_CHANNEL.search(text):
        return False
    nodes = _NNODES.findall(text)
    if nodes:
        return all(count == "1" for count in nodes)
    return bool(_LOCAL_CHANNEL.search(text))


def resource_findings(text: str) -> tuple[list[str], bool]:
    """Parse only resources blocks; never combine a sidecar request with another limit."""
    lines = text.splitlines()
    findings = []
    seen = False
    for index, line in enumerate(lines):
        if not re.match(r"^\s*resources\s*:", line):
            continue
        seen = True
        indent = len(line) - len(line.lstrip())
        block = [line[indent:]]
        for following in lines[index + 1 :]:
            if following.strip() and len(following) - len(following.lstrip()) <= indent:
                break
            block.append(following[indent:])
        try:
            resources = yaml.safe_load("\n".join(block)).get("resources")
            if not isinstance(resources, dict):
                raise ValueError("resources must be a mapping")
            limits = resources.get("limits") or {}
            resource_requests = resources.get("requests") or {}
            if not isinstance(limits, dict) or not isinstance(resource_requests, dict):
                raise ValueError("requests and limits must be mappings")
            limit = limits.get("rdma/ib")
            request = resource_requests.get("rdma/ib")

            # This resource is a documented boolean allocation flag (1), not a count.
            def valid(value):
                if value is None or isinstance(value, bool):
                    return False
                try:
                    quantity = Decimal(str(value))
                except InvalidOperation:
                    return False
                return quantity.is_finite() and quantity == 1

            if not valid(limit):
                findings.append(
                    f"resources block {index + 1}: rdma/ib limit is absent or not 1; verify this is the communicating container"
                )
            elif request is not None and not valid(request):
                findings.append(
                    f"resources block {index + 1}: rdma/ib request must match limit 1; omitted requests default from limits"
                )
        except (yaml.YAMLError, ValueError, TypeError, AttributeError):
            findings.append(
                f"resources block {index + 1}: could not parse resource evidence; inspect the actual admitted Pod"
            )
    return findings, seen


# IB logical port states (ibstat). kubectl describe also prints "State:" lines
# (Running/Waiting/Terminated); those are not port evidence and are ignored.
_IB_PORT_STATES = {"down", "init", "initializing", "armed", "active", "active defer", "inactive"}


def detect_ibstat(text: str) -> tuple[str, list[str]]:
    states = [
        state.strip()
        for state in re.findall(r"^\s*State:\s*(.+)$", text, re.M)
        if state.strip().lower() in _IB_PORT_STATES
    ]
    states += [m.upper() for m in re.findall(r"^\s*state:\s*PORT_(\w+)", text, re.M | re.I)]
    physical = re.findall(r"^\s*Physical state:\s*(.+)$", text, re.M)
    notes = [f"IB port State: {state}" for state in states if state.lower() != "active"]
    notes += [
        f"IB Physical state: {state.strip()}"
        for state in physical
        if state.strip().lower().replace(" ", "") != "linkup"
    ]
    return ("down" if notes else "ok" if states or physical else "absent", notes)


def detect_busbw(text: str) -> float | None:
    match = re.search(r"avg\s+bus\s+bandwidth\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
    return float(match.group(1)) if match else None


def diagnose(text: str) -> dict:
    transport, gdr, failed = detect_transport(text)
    missing, manifest_seen = resource_findings(text)
    _, degraded = detect_ibstat(text)
    if _IB_DISABLED.search(text):
        missing.append("NCCL_IB_DISABLE=1 disables the IB transport; review the effective environment")
    single_node = detect_single_node(text)
    rdma = {"IB": "yes", "Socket": "no", "mixed": "partial", "unknown": "unknown"}[transport]
    if single_node:
        rdma = "not-applicable"
    verdict = {
        "IB": "InfiniBand transport observed; GPU Direct RDMA needs its own positive log evidence.",
        "Socket": "TCP socket transport observed; investigate whether this is an unintended fallback for the selected run.",
        "mixed": "Both transports observed; separate ranks, channels and run timestamps before concluding that one run is degraded.",
        "unknown": "Insufficient positive transport evidence; a warning or bootstrap line is not proof of the data path.",
    }[transport]
    if single_node:
        verdict = (
            "Single-node run: no traffic crossed the network, so RDMA engagement is not applicable. "
            "Collect a multi-node run before judging the transport."
        )
    return {
        "rdma_engaged": rdma,
        "single_node": single_node,
        "transport": transport,
        "gpu_direct_rdma_confirmed": gdr and transport in ("IB", "mixed"),
        "manifest_evidence_present": manifest_seen,
        "missing_conditions": missing,
        "degraded_signals": degraded,
        "observed_avg_busbw_gbps": detect_busbw(text),
        "ib_attempt_failed_in_log": failed,
        "verdict": verdict,
        "fix": [
            "Check InfiniBand-capable Node Pool and the communicating container: set rdma/ib: 1 in limits; omitted requests default from limits. Explicit requests must match.",
            "Review NCCL/OFED userspace and effective NCCL_IB_HCA and NCCL_SOCKET_IFNAME against current platform documentation; operator-managed settings may not appear in the pasted spec.",
            "Collect NCCL_DEBUG=INFO from the same ranks and run; distinguish transport selection from positive GPU Direct RDMA evidence.",
            "Compare busbw with a measured baseline matching topology, image, versions, message sizes and GPU count; no universal pass/fail bandwidth or slowdown multiplier is assumed.",
            "Escalate device or port failures to the platform owner; do not install host drivers, reset hardware or override a managed health cordon.",
        ],
    }


def render(result: dict) -> str:
    lines = [
        f"VERDICT: {result['verdict']}",
        f"Transport: {result['transport']}",
        f"GPU Direct RDMA confirmed: {result['gpu_direct_rdma_confirmed']}",
    ]
    lines += [f"Evidence gap: {item}" for item in result["missing_conditions"]]
    lines += [f"Port observation: {item}" for item in result["degraded_signals"]]
    if result["observed_avg_busbw_gbps"] is not None:
        lines.append(f"Observed busbw: {result['observed_avg_busbw_gbps']} GB/s [unverified vs baseline]")
    lines += [f"{i}. {step}" for i, step in enumerate(result["fix"], 1)]
    return "\n".join(lines)


def self_test() -> int:
    assert diagnose("NCCL INFO Using network Socket")["transport"] == "Socket"
    assert diagnose("NCCL INFO Using network IB")["transport"] == "IB"
    assert not diagnose("NCCL INFO Using network IB")["gpu_direct_rdma_confirmed"]
    assert diagnose("NCCL WARN NET/IB : ibv_open_device failed")["transport"] == "unknown"
    assert resource_findings("resources: {limits: {rdma/ib: 1}}")[0] == []
    assert resource_findings("resources: {requests: {rdma/ib: 1}}")[0]
    assert detect_ibstat("State: Inactive")[0] == "down"
    print("SELF-TEST PASSED: transport evidence, limits defaulting, and port state")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="infile", default="-")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.infile == "-" and sys.stdin.isatty():
        parser.error("provide --in diagnostics.txt or pipe diagnostics on stdin")
    if args.infile == "-":
        raw = sys.stdin.read()
    else:
        with open(args.infile, encoding="utf-8") as source:
            raw = source.read()
    if not raw.strip():
        parser.error("empty diagnostic input")
    result = diagnose(raw)
    print(json.dumps(result, indent=2, allow_nan=False) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
