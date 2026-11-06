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


def detect_transport(text: str) -> tuple[str, bool, bool]:
    lines = [line for line in text.splitlines() if "NCCL" in line.upper()]
    info = [line for line in lines if not re.search(r"\b(?:WARN|ERROR)\b", line, re.I)]
    ib = any(re.search(r"Using network IB(?:ext)?\b|NET/IB\s*:\s*Using\b|via NET/IB/", line, re.I) for line in info)
    socket = any(
        re.search(r"Using network Socket\b|NET/Socket\s*:\s*Using\b|via NET/Socket/", line, re.I) for line in info
    )
    gdr = any(re.search(r"GPU Direct RDMA Enabled\b|via NET/IB/\S*/GDRDMA\b", line, re.I) for line in info)
    failed = any(re.search(r"NCCL\s+(?:WARN|ERROR).*?(?:ibv_|NET/IB)", line, re.I) for line in lines)
    return ("mixed" if ib and socket else "IB" if ib else "Socket" if socket else "unknown", gdr, failed)


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


def detect_ibstat(text: str) -> tuple[str, list[str]]:
    states = re.findall(r"^\s*State:\s*(.+)$", text, re.M)
    physical = re.findall(r"^\s*Physical state:\s*(.+)$", text, re.M)
    notes = [f"IB port State: {state.strip()}" for state in states if state.strip().lower() != "active"]
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
    if re.search(r"nccl_ib_disable\s*[:=]\s*[\'\"]?1\b", text, re.I):
        missing.append("NCCL_IB_DISABLE=1 disables the IB transport; review the effective environment")
    rdma = {"IB": "yes", "Socket": "no", "mixed": "partial", "unknown": "unknown"}[transport]
    verdict = {
        "IB": "InfiniBand transport observed; GPU Direct RDMA needs its own positive log evidence.",
        "Socket": "TCP socket transport observed; investigate whether this is an unintended fallback for the selected run.",
        "mixed": "Both transports observed; separate ranks, channels and run timestamps before concluding that one run is degraded.",
        "unknown": "Insufficient positive transport evidence; a warning or bootstrap line is not proof of the data path.",
    }[transport]
    return {
        "rdma_engaged": rdma,
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
