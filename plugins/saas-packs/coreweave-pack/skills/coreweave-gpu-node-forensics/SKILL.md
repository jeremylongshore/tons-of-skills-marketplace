---
name: coreweave-gpu-node-forensics
description: |
  Review NVIDIA Xid and row-remapper evidence for a CoreWeave GPU incident.
  Use when a GPU throws an Xid, a training rank stalls, a device falls off the bus,
  or deciding whether to restart a workload or escalate hardware recovery.
  Trigger with "xid error", "gpu fell off the bus", "coreweave gpu dead",
  "should I RMA this GPU", or "gpu node triage".
allowed-tools: Read, Bash(python3:*), Bash(nvidia-smi -q:*), Bash(kubectl get:*), Bash(dmesg:*)
version: 1.15.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, coreweave, gpu-cloud, reliability, xid]
---
# CoreWeave GPU Node Forensics

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Produce deterministic triage recommendations from supplied Xid evidence, with confidence and required corroboration.
A code identifies an event class; it does not prove a universal root cause, a healthy GPU, or permission to reset hardware.
The script never executes cluster commands, resets, reboots, RMA requests or uncordons.

## Prerequisites

- A sanitized Xid line or nvidia-smi diagnostic excerpt with GPU identity, time and workload correlation.
- Python 3 for the stdlib-only classifier; no live account is required for pasted evidence.
- For corroboration, authorized access to driver version, GPU architecture, DCGM diagnostics and managed Node lifecycle state.
- A platform owner who approves disruptive recovery and checks workload/checkpoint impact.

## Instructions

1. Read the supplied evidence and identify one GPU and run. Split multi-GPU logs; do not apply another device’s row-remapper state to the current fault.
2. Run the bundled classifier. Read `action` as a recommendation requiring confirmation, alongside `confidence`, `requires_confirmation` and `unverified` fields.
3. For Xid 94, explain containment of the reported application event; do not claim the Node is healthy or that a convenient later reset is never useful. For Xid 95, explain uncontained scope and the documented reset requirement for supported devices before workload restart. Confirm architecture/driver guidance and managed recovery first.
4. For Xids 13/31/43, investigate application/driver context without excluding hardware from a bare code. Xid 45 is a follow-on code: act on the accompanying Xid. An Xid 154 recovery action (GPU Reset Required, Node Reboot Required) sets the verdict. Unknown codes stay `investigate`, rank below mapped codes and never trigger an automatic reset.
5. Correlate pending/failure row-remapper evidence (`Remapped Rows` in `nvidia-smi -q`) with the same GPU. Pending remap can inform supported reset planning; reported failure requires support review and NVIDIA's field diagnostic before declaring terminal hardware or requesting replacement.
6. Read lifecycle state, pending-state and cordon provenance. Never manually uncordon a controller-owned health cordon; follow the platform owner’s supported recovery path.

## Examples

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/triage.py" --xid 94 --json
python3 "${CLAUDE_SKILL_DIR}/scripts/triage.py" --xid 95 --json
python3 "${CLAUDE_SKILL_DIR}/scripts/triage.py" --blob gpu-diagnostics.txt --json
python3 "${CLAUDE_SKILL_DIR}/scripts/triage.py" --self-test
```

For explicitly authorized corroboration, `nvidia-smi -q` and `dmesg` read device/log data and can still expose workload identifiers; review before sharing.
Do not translate a recommendation into `nvidia-smi -r`, reboot, drain or uncordon execution.

## Output

- Classification, severity, recommended action, reason and the next diagnostic step.
- Confidence, confirmation requirements, co-occurring codes and unresolved evidence.
- The managed-cordon rule on every disruptive hardware recommendation.
- An inconclusive result for ambiguous device scope or unknown codes.

## Error Handling

| Evidence problem | Response |
|---|---|
| Unknown Xid | Consult the current catalog and collect diagnostics; do not default to reset. |
| Different GPU identities in a blob | Split the evidence; no single combined recovery action. |
| Pending field outside Remapped Rows | Do not treat an unrelated Pending value as a memory-remap signal. |
| PCIe-bus failure plus a remap field | Preserve the governing bus failure; a remap must not downgrade it to a simpler reset. |
| No signal found | Report missing evidence, not a clean health result. |

## Resources

- [Xid recommendations and limits](references/xid-triage-table.md)
- [Row-remapper evidence](references/row-remap-decision.md)
- [Managed cordon ownership](references/cordon-rules.md)
- [NVIDIA Xid catalog](https://docs.nvidia.com/deploy/xid-errors/latest/analyzing-xid-catalog.html)
- [CoreWeave lifecycle transitions](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions)

## Evidence status

Offline parser/recommendation tests are reproducible. No live device health, reset capability, recovery, RMA threshold or CoreWeave account behavior was validated in this review.
