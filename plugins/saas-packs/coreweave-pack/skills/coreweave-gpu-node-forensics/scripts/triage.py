#!/usr/bin/env python3
"""Offline NVIDIA Xid triage recommendations for CoreWeave operators.

A code labels an observed event, not a universal root cause or permission to reset.
Every recommendation requires GPU identity, architecture, driver/DCGM diagnostics,
workload impact and managed lifecycle state to be corroborated. Never uncordon a
controller-owned health cordon. Unknown or multi-GPU evidence stays inconclusive.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# ---------------------------------------------------------------------------
# Severity ranking — used to pick the GOVERNING Xid when a blob carries several
# (the most severe fault dictates the triage move; the rest are noted).
# ---------------------------------------------------------------------------
SEVERITY_RANK = {"critical": 3, "high": 2, "medium": 1, "low": 0}

VALID_ACTIONS = (
    "reschedule",
    "reset-gpu",
    "reboot-node",
    "rma",
    "watch",
    "investigate",
    "investigate-application",
)

# The CoreWeave hard rule, attached to every verdict that touches the node/GPU
# at the hardware level. CoreWeave's node-lifecycle controller places a health
# cordon on a faulting node; a human uncordoning it re-schedules work onto known-
# bad hardware and races the controller. See references/cordon-rules.md.
CORDON_RULE = (
    "Do NOT manually uncordon a CoreWeave health cordon — the node-lifecycle "
    "controller owns cordon/uncordon. Follow the managed recovery owner’s procedure."
)

# CoreWeave does not publish exact auto-RMA thresholds (how many SBE/remap
# events trigger an automatic replacement) or the exact taint/label string of a
# health cordon. Anything depending on those is flagged [unverified].
UNVERIFIED_RMA_THRESHOLD = (
    "[unverified] CoreWeave's exact auto-RMA thresholds (SBE-rate / remaining "
    "remap-bank limits) are not publicly published — treat escalation counts as "
    "guidance, confirm the RMA trigger with CoreWeave support."
)

# ---------------------------------------------------------------------------
# The Xid -> verdict table. Single source of truth for the code path; kept in
# lockstep with references/xid-triage-table.md. Each entry:
#   code: (classification, severity, action, why, next_command)
# ---------------------------------------------------------------------------
XID_TABLE: dict[int, tuple[str, str, str, str, str]] = {
    13: (
        "Graphics/compute engine exception",
        "medium",
        "investigate-application",
        "Application or driver faults are possible; this code alone does not exclude hardware.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    31: (
        "GPU memory page fault",
        "medium",
        "investigate-application",
        "Investigate the failing kernel and driver; a page fault alone does not prove a healthy GPU.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    43: (
        "GPU stopped processing",
        "medium",
        "investigate-application",
        "Correlate prior Xids and application failures; do not classify hardware from this code alone.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    45: (
        "Preemptive channel cleanup (follow-on code)",
        "low",
        "investigate",
        "Xid 45 follows another event: act on the accompanying Xid. When it appears alone, NVIDIA's catalog action is restarting Fabric Manager on NVSwitch systems; the lifecycle owner performs that.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    48: (
        "Double-bit ECC error",
        "critical",
        "reset-gpu",
        "Review memory-error and row-remapper evidence for this GPU; reset is a candidate recovery action, subject to architecture and support guidance.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    63: (
        "Page retirement or row-remap event",
        "high",
        "watch",
        "Check whether remapping is pending or failed on the same GPU; this code alone does not authorize reset or replacement.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    64: (
        "Page retirement or row-remap recording failure",
        "high",
        "reset-gpu",
        "NVIDIA's action is a GPU reset or node reboot, then contact support if it recurs. RMA review only applies when a remapping failure is reported and NVIDIA's field diagnostic fails.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    74: (
        "NVLink error",
        "high",
        "reset-gpu",
        "Review topology, peer GPUs and Fabric Manager diagnostics; any reset must follow the supported procedure.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    79: (
        "GPU inaccessible on PCIe bus",
        "critical",
        "reboot-node",
        "Inspect driver/platform diagnostics and lifecycle state; a node reboot or power cycle may be needed, but is not authorized by this code alone.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    92: (
        "High correctable ECC error rate",
        "medium",
        "watch",
        "Review trends and current diagnostics; correctable events do not establish complete GPU health.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    94: (
        "Contained memory error",
        "high",
        "reschedule",
        "Containment limits the reported error scope; review the affected workload and GPU diagnostics before restarting it. This is not proof the node is healthy.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    95: (
        "Uncontained memory error",
        "critical",
        "reset-gpu",
        "Escalate affected workload integrity and recovery scope. A reset may be required; confirm architecture, driver and lifecycle guidance before disruption.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    119: (
        "GSP RPC timeout",
        "high",
        "reset-gpu",
        "Review driver/GSP and GPU diagnostics; request support guidance before a managed reset or reboot.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    120: (
        "GSP error",
        "high",
        "reset-gpu",
        "Review driver/GSP and GPU diagnostics; a bare code does not establish the recovery scope.",
        "Collect nvidia-smi -q and DCGM diagnostics for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
    154: (
        "GPU recovery action changed",
        "medium",
        "investigate",
        "The driver reports a recovery action; read the 'to 0xN (<action>)' text, which sets the verdict when present.",
        "Read the full Xid 154 line and nvidia-smi -q for the identified GPU; consult the current NVIDIA Xid catalog and CoreWeave lifecycle owner.",
    ),
}

# Xid 154 "GPU recovery action changed from 0xA (<old>) to 0xB (<new>)": the driver's
# own recovery requirement. Label -> (severity, action, why).
RECOVERY_ACTIONS: dict[str, tuple[str, str, str]] = {
    "gpu reset required": (
        "high",
        "reset-gpu",
        "The driver reports 'GPU Reset Required' (Xid 154). Drain the GPU's workload, then reset through the supported recovery path.",
    ),
    "node reboot required": (
        "critical",
        "reboot-node",
        "The driver reports 'Node Reboot Required' (Xid 154). A GPU reset is not sufficient; drain the node for a managed reboot.",
    ),
    "drain and reset": (
        "high",
        "reset-gpu",
        "The driver reports 'Drain and Reset' (Xid 154). Drain workloads first, then reset through the supported recovery path.",
    ),
    "drain p2p": (
        "high",
        "investigate",
        "The driver reports 'Drain P2P' (Xid 154). Drain peer-to-peer workloads and follow NVIDIA's guidance for this action.",
    ),
}

# Non-Xid signal: thermal throttling parsed from nvidia-smi PERFORMANCE output.
THERMAL_VERDICT = (
    "Thermal throttling observed",
    "medium",
    "watch",
    "Thermal throttling is reported; this alone does not establish hardware health. "
    "Investigate cooling / airflow / inlet temp, not the card. Reschedule off it "
    "only if throttling is tanking throughput.",
    "nvidia-smi -q -d PERFORMANCE to read the throttle reasons; check node airflow / datacenter cooling.",
)

# Actions that operate at the hardware/node level -> carry the cordon rule.
_HARDWARE_ACTIONS = {"reset-gpu", "reboot-node", "rma"}


def _verdict(
    *,
    xid: int | None,
    classification: str,
    severity: str,
    action: str,
    why: str,
    next_command: str,
    co_occurring: list[int] | None = None,
    unverified: list[str] | None = None,
) -> dict:
    """Assemble a verdict dict, attaching the cordon rule + unverified hedges."""
    v: dict = {
        "xid": xid,
        "classification": classification,
        "severity": severity,
        "action": action,
        "why": why,
        "next_command": next_command,
        "confidence": "moderate" if xid in XID_TABLE else "low",
        "recommendation_only": True,
        "requires_confirmation": [
            "GPU identity and architecture",
            "driver version and DCGM diagnostics",
            "workload impact and lifecycle owner approval",
        ],
    }
    if co_occurring:
        v["co_occurring_xids"] = co_occurring
    hedges = list(unverified or [])
    if action in _HARDWARE_ACTIONS:
        v["cordon_rule"] = CORDON_RULE
    if action == "rma":
        hedges.append(UNVERIFIED_RMA_THRESHOLD)
    if hedges:
        v["unverified"] = hedges
    return v


def classify_xid(xid: int) -> dict:
    """Map a bare Xid code to its base verdict (no row-remap override)."""
    if xid in XID_TABLE:
        classification, severity, action, why, nxt = XID_TABLE[xid]
        return _verdict(
            xid=xid,
            classification=classification,
            severity=severity,
            action=action,
            why=why,
            next_command=nxt,
        )
    return _verdict(
        xid=xid,
        classification=f"Unmapped Xid {xid}",
        severity="high",
        action="investigate",
        why=f"Xid {xid} is not in this table. Preserve evidence and consult the current catalog; no reset is inferred.",
        next_command="See https://docs.nvidia.com/deploy/xid-errors/ for Xid "
        f"{xid}; collect supported diagnostics and escalate to the lifecycle owner.",
        unverified=[f"[unverified] Xid {xid} has no entry in xid-triage-table.md — verdict is a conservative default."],
    )


def apply_remap_override(base: dict, pending: bool | None, remap_failure: bool | None) -> dict:
    """Row-remapper evidence informs recommendations for the ECC/DBE family.

    - Remapping Failure Occurred: Yes -> support/RMA review for the ECC family.
    - Pending: Yes -> review a supported reset with the lifecycle owner.
    Anything else leaves the base verdict untouched.

    An override builds a FRESH verdict, so it must carry forward the forensic
    context the base accumulated — the co-occurring Xids and any [unverified]
    hedges — rather than silently dropping them.
    """
    xid = base.get("xid")
    if xid not in (None, 48, 63, 64, 94, 95):
        if pending or remap_failure:
            base.setdefault("unverified", []).append(
                "Row-remapper evidence requires same-GPU correlation; it did not override this Xid."
            )
        return base
    if remap_failure:
        v = _verdict(
            xid=xid,
            classification="Row-remapper failure reported",
            severity="critical",
            action="investigate",
            why=(
                "nvidia-smi reports 'Remapping Failure Occurred: Yes'. Take the GPU out of service and "
                "open a support case; RMA review applies only if NVIDIA's field diagnostic then fails."
            ),
            next_command="Collect same-GPU diagnostics and request NVIDIA's field diagnostic through CoreWeave support; do not override lifecycle control.",
            unverified=[UNVERIFIED_RMA_THRESHOLD],
        )
    elif pending:
        v = _verdict(
            xid=xid,
            classification="ECC row-remap PENDING (routine)",
            severity="high",
            action="reset-gpu",
            why=(
                "nvidia-smi reports 'Pending: Yes' with no remap failure — a row-remap "
                "is queued and applies on the next GPU reset. Routine ECC self-healing, "
                "not sufficient evidence for an RMA."
            ),
            next_command="Confirm the same-GPU pending remap with DCGM and the lifecycle owner before scheduling supported recovery.",
        )
    else:
        return base

    # The override verdict is fresh — carry forward the base's forensic context
    # so a remap-driven RMA/reset still shows the ALSO-SEEN co-occurring Xids and
    # preserves the base's [unverified] hedges.
    if base.get("co_occurring_xids"):
        v["co_occurring_xids"] = base["co_occurring_xids"]
    base_hedges = base.get("unverified") or []
    if base_hedges:
        # union, dedup — do NOT double-append _verdict's own standard hedges
        v["unverified"] = list(dict.fromkeys([*base_hedges, *v.get("unverified", [])]))
    return v


# ---------------------------------------------------------------------------
# Blob parsing — pull Xid codes + row-remapper state + thermal flags out of a
# pasted dmesg / nvidia-smi dump.
# ---------------------------------------------------------------------------
# Matches:  "NVRM: Xid (PCI:0000:3b:00): 79, pid=..."  and  "[Xid 48]"  and  "Xid: 94"
# Also "XID 79", "Xid=79", "Xid (0000:03:00): 79" and redacted tags like "Xid [REDACTED]: 79" or "Xid ...: 13".
_XID_RE = re.compile(r"\bXid\s*(?:\([^)]*\)|\[[^\]]*\]|\.{3}|\u2026)?\s*[:,=]?\s*(\d{1,4})\b", re.IGNORECASE)
_GPU_ID_RE = re.compile(r"\bXid\s*\((?:PCI:)?((?:[0-9a-f]{4}:)?[0-9a-f]{2}:[0-9a-f]{2}(?:\.[0-7])?)\)", re.IGNORECASE)
_RECOVERY_RE = re.compile(r"recovery action changed from\s+\S+\s*\([^)]*\)\s*to\s+\S+\s*\(([^)]*)\)", re.IGNORECASE)
_REMAP_FAIL_RE = re.compile(r"Remapping\s+Failure\s+Occurred\s*:\s*(Yes|No)", re.IGNORECASE)
_PENDING_RE = re.compile(r"\bPending\s*:\s*(Yes|No)", re.IGNORECASE)
_THERMAL_RE = re.compile(r"(HW|SW)\s+Thermal\s+Slowdown\s*:\s*Active", re.IGNORECASE)


def parse_blob(text: str) -> dict:
    """Extract structured signals from a pasted dmesg / nvidia-smi blob."""
    xids = [int(m) for m in _XID_RE.findall(text)]
    recovery = _RECOVERY_RE.findall(text)
    remap_fail_m = _REMAP_FAIL_RE.search(text)
    # nvidia-smi -q prints "Remapped Rows"; older docs and tools say "Row Remapper".
    row_section = re.search(r"(?:Row Remapper|Remapped Rows)(?P<body>(?:\n[ \t]+[^\n]*)+)", text, re.IGNORECASE)
    pending_m = _PENDING_RE.search(row_section.group("body")) if row_section else None
    return {
        "xids": xids,
        "remap_failure": (remap_fail_m.group(1).lower() == "yes") if remap_fail_m else None,
        "pending": (pending_m.group(1).lower() == "yes") if pending_m else None,
        "thermal": bool(_THERMAL_RE.search(text)),
        "recovery_action": recovery[-1].strip().lower() if recovery else None,
    }


def triage_from_blob(text: str) -> dict:
    """End-to-end: parse a blob, pick the governing signal, return one verdict."""
    parsed = parse_blob(text)
    gpu_ids = {gpu.lower().removeprefix("0000:") for gpu in _GPU_ID_RE.findall(text)}
    if len(gpu_ids) > 1:
        return _verdict(
            xid=None,
            classification="Multiple GPU identities in input",
            severity="high",
            action="investigate",
            why="Split evidence by GPU and time before correlating Xids or row-remapper state.",
            next_command="Collect one GPU diagnostic set per report.",
        )
    xids = parsed["xids"]

    recovery = RECOVERY_ACTIONS.get(parsed["recovery_action"] or "")
    if recovery:
        # The driver's own Xid 154 recovery requirement governs; other codes are noted.
        severity, action, why = recovery
        v = _verdict(
            xid=154,
            classification=f"GPU recovery action: {parsed['recovery_action']}",
            severity=severity,
            action=action,
            why=why,
            next_command=XID_TABLE[154][4],
        )
        others = sorted({x for x in xids if x != 154})
        if others:
            v["co_occurring_xids"] = others
        return v

    if xids:
        # The most severe known Xid governs; unknown codes rank below known ones and
        # follow-on Xid 45 below everything, so neither overrides a mapped event.
        governing = max(xids, key=_governing_rank)
        base = classify_xid(governing)
        others = sorted({x for x in xids if x != governing})
        if others:
            base["co_occurring_xids"] = others
        return apply_remap_override(base, parsed["pending"], parsed["remap_failure"])

    # No Xid — fall back to row-remap state, then thermal.
    if parsed["remap_failure"] or parsed["pending"]:
        return apply_remap_override(
            _verdict(
                xid=None,
                classification="Row-remapper state (no Xid in blob)",
                severity="high",
                action="watch",
                why="Row-remapper fields found without an Xid; the remap state governs.",
                next_command="nvidia-smi -q -d ROW_REMAPPER",
            ),
            parsed["pending"],
            parsed["remap_failure"],
        )
    if parsed["thermal"]:
        classification, severity, action, why, nxt = THERMAL_VERDICT
        return _verdict(
            xid=None,
            classification=classification,
            severity=severity,
            action=action,
            why=why,
            next_command=nxt,
        )

    return _verdict(
        xid=None,
        classification="No GPU fault signal found",
        severity="low",
        action="watch",
        why="No Xid, row-remapper failure, or thermal-throttle signal was found in the input.",
        next_command="Collect fresh evidence: dmesg -T | grep -i xid ; nvidia-smi -q -d ROW_REMAPPER,ECC,PERFORMANCE",
    )


def _severity_of(xid: int) -> str:
    return XID_TABLE[xid][1] if xid in XID_TABLE else "high"


def _governing_rank(xid: int) -> int:
    if xid == 45:
        return -2
    if xid not in XID_TABLE:
        return -1
    return SEVERITY_RANK[XID_TABLE[xid][1]]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def render_verdict(v: dict) -> str:
    """Human-readable VERDICT block (the SKILL reasons over the JSON, humans read this)."""
    xid = v.get("xid")
    head = f"Xid {xid} — {v['classification']}" if xid is not None else v["classification"]
    lines = [
        f"VERDICT: {head} [severity: {v['severity'].upper()}]",
        f"RECOMMENDED ACTION (confirmation required): {v['action']}",
        f"WHY:     {v['why']}",
        f"NEXT:    {v['next_command']}",
    ]
    if v.get("co_occurring_xids"):
        lines.append(
            f"ALSO SEEN: Xid {', '.join(str(x) for x in v['co_occurring_xids'])} (governed by the most severe above)"
        )
    if v.get("cordon_rule"):
        lines.append(f"CORDON:  {v['cordon_rule']}")
    for hedge in v.get("unverified", []):
        lines.append(f"NOTE:    {hedge}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-test — bundled fixtures, exit 0 on all-pass
# ---------------------------------------------------------------------------
def _run_self_test() -> int:
    cases = [
        # (label, verdict-producing thunk, expected_action)
        ("xid 94 CONTAINED -> reschedule", lambda: classify_xid(94), "reschedule"),
        ("xid 95 UNCONTAINED -> reset-gpu", lambda: classify_xid(95), "reset-gpu"),
        ("xid 79 fell-off-bus -> reboot-node", lambda: classify_xid(79), "reboot-node"),
        ("xid 43 context -> investigate-application", lambda: classify_xid(43), "investigate-application"),
        ("xid 13 engine-exception -> investigate-application", lambda: classify_xid(13), "investigate-application"),
        ("xid 31 page-fault -> investigate-application", lambda: classify_xid(31), "investigate-application"),
        ("xid 92 SBE-trend -> watch", lambda: classify_xid(92), "watch"),
        ("xid 64 remap-record-failure -> reset-gpu", lambda: classify_xid(64), "reset-gpu"),
        (
            "xid 63 + Pending:Yes -> reset-gpu",
            lambda: apply_remap_override(classify_xid(63), pending=True, remap_failure=False),
            "reset-gpu",
        ),
        (
            "remap-failure override -> investigate (field diagnostic before RMA)",
            lambda: apply_remap_override(classify_xid(63), pending=False, remap_failure=True),
            "investigate",
        ),
        (
            "xid 48 DBE + remap-failure -> investigate",
            lambda: apply_remap_override(classify_xid(48), pending=False, remap_failure=True),
            "investigate",
        ),
        (
            "blob: contained 94 -> reschedule",
            lambda: triage_from_blob("NVRM: Xid (PCI:0000:3b:00): 94, pid=1234, Contained: ECC error"),
            "reschedule",
        ),
        (
            "blob: uncontained 95 -> reset-gpu",
            lambda: triage_from_blob("kernel: NVRM: Xid (PCI:0000:65:00): 95, Uncontained ECC error"),
            "reset-gpu",
        ),
        (
            "blob: 79 fell off bus -> reboot-node",
            lambda: triage_from_blob("NVRM: Xid (PCI:0000:04:00): 79, GPU has fallen off the bus."),
            "reboot-node",
        ),
        (
            "blob: nvidia-smi remap FAILURE -> investigate",
            lambda: triage_from_blob("    Remapping Failure Occurred          : Yes\n    Pending: No"),
            "investigate",
        ),
        (
            "blob: nvidia-smi remap Pending -> reset-gpu",
            lambda: triage_from_blob(
                "  Row Remapper\n    Pending                             : Yes\n    Remapping Failure Occurred : No"
            ),
            "reset-gpu",
        ),
        (
            "blob: thermal throttle -> watch",
            lambda: triage_from_blob("Clocks Throttle Reasons\n    HW Thermal Slowdown : Active"),
            "watch",
        ),
        (
            "blob: co-occurring 43+79, 79 governs -> reboot-node",
            lambda: triage_from_blob("Xid 43, software fault\nlater: NVRM: Xid (PCI:0000:04:00): 79, fell off bus"),
            "reboot-node",
        ),
    ]

    passed = 0
    failed = 0
    for label, thunk, expected in cases:
        v = thunk()
        got = v.get("action")
        ok = got == expected and got in VALID_ACTIONS
        # Invariant: every hardware action carries the cordon rule.
        if v.get("action") in _HARDWARE_ACTIONS and not v.get("cordon_rule"):
            ok = False
            note = " (MISSING cordon_rule)"
        else:
            note = ""
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"[{status}] {label}: expected={expected} got={got}{note}")

    # ---- context-preservation checks for the remap override ----------------
    # A remap override builds a FRESH verdict; it must still carry forward the
    # base verdict's forensic context — co-occurring Xids AND [unverified]
    # hedges — deduping against _verdict's own standard hedges.
    ctx_checks = []

    # remap FAILURE (-> RMA): preserve co-occurring Xids + base hedges, and dedup
    # against _verdict's own standard RMA hedge (seeded into the base to prove it).
    base_fail = classify_xid(48)
    base_fail["co_occurring_xids"] = [79, 94]
    base_fail["unverified"] = ["[unverified] base-only forensic hedge", UNVERIFIED_RMA_THRESHOLD]
    v_fail = apply_remap_override(base_fail, pending=None, remap_failure=True)
    ctx_checks.append(
        (
            "remap-failure override preserves co_occurring_xids + base hedge (no dupes)",
            v_fail.get("action") == "investigate"
            and v_fail.get("co_occurring_xids") == [79, 94]
            and "[unverified] base-only forensic hedge" in v_fail.get("unverified", [])
            and UNVERIFIED_RMA_THRESHOLD in v_fail.get("unverified", [])
            and len(v_fail.get("unverified", [])) == len(set(v_fail.get("unverified", []))),
        )
    )

    # pending (-> reset-gpu): likewise preserve the base's forensic context.
    base_pending = classify_xid(48)
    base_pending["co_occurring_xids"] = [92]
    base_pending["unverified"] = ["[unverified] base-only pending hedge"]
    v_pending = apply_remap_override(base_pending, pending=True, remap_failure=False)
    ctx_checks.append(
        (
            "pending override preserves co_occurring_xids + base hedge (no dupes)",
            v_pending.get("action") == "reset-gpu"
            and v_pending.get("co_occurring_xids") == [92]
            and "[unverified] base-only pending hedge" in v_pending.get("unverified", [])
            and len(v_pending.get("unverified", [])) == len(set(v_pending.get("unverified", []))),
        )
    )

    for label, ok in ctx_checks:
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"[{status}] {label}")

    print(f"\nself-test: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _yesno(val: str | None) -> bool | None:
    if val is None:
        return None
    lowered = str(val).strip().lower()
    if lowered not in ("yes", "y", "true", "1", "no", "n", "false", "0"):
        raise ValueError("boolean flag must be yes or no")
    return lowered in ("yes", "y", "true", "1")


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic CoreWeave GPU-node failure triage.")
    ap.add_argument("--xid", type=int, help="NVIDIA Xid code to classify.")
    ap.add_argument("--pending", help="Row-remapper 'Pending' state: yes|no.")
    ap.add_argument("--remap-failure", dest="remap_failure", help="'Remapping Failure Occurred' state: yes|no.")
    ap.add_argument("--blob", help="Path to a pasted dmesg/nvidia-smi blob ('-' for stdin).")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    ap.add_argument("--self-test", action="store_true", help="Run bundled fixtures and exit.")
    args = ap.parse_args()

    if args.self_test:
        return _run_self_test()

    if args.xid is not None and args.blob:
        ap.error("choose --xid or --blob, not both")
    if args.xid is None and (args.pending is not None or args.remap_failure is not None):
        ap.error("row-remapper flags require --xid; blob mode reads its own evidence")
    if args.xid is not None:
        if args.xid < 0 or args.xid > 9999:
            ap.error("Xid must be between 0 and 9999")
        try:
            _yesno(args.pending)
            _yesno(args.remap_failure)
        except ValueError as exc:
            ap.error(str(exc))
        base = classify_xid(args.xid)
        verdict = apply_remap_override(base, _yesno(args.pending), _yesno(args.remap_failure))
    else:
        # Blob mode: explicit --blob, else read stdin if piped.
        if args.blob:
            if args.blob == "-":
                text = sys.stdin.read()
            else:
                with open(args.blob, encoding="utf-8") as fh:
                    text = fh.read()
        elif not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            print(
                "error: provide --xid N, or --blob <file|->, or pipe a dmesg/nvidia-smi blob on stdin", file=sys.stderr
            )
            ap.print_help(sys.stderr)
            return 1
        if not text.strip():
            print("error: empty input blob", file=sys.stderr)
            return 1
        verdict = triage_from_blob(text)
        # A standalone row-remap override may still apply when the user pastes an
        # Xid AND supplies remap flags on the CLI alongside --blob (rare) — blob
        # parsing already folded remap state in, so nothing more to do here.

    if args.json:
        print(json.dumps(verdict, indent=2))
    else:
        print(render_verdict(verdict))
        print()
        print(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
