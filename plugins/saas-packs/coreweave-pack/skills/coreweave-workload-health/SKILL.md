---
name: coreweave-workload-health
description: Verify workload readiness, GPU allocation and observed activity from
  pasted snapshots without changing workloads. Use when reviewing CoreWeave workload
  health or checking supplied operational evidence. Trigger with "coreweave workload
  health".
allowed-tools: Read, Write, Edit, Bash(python3:*), Grep
version: 1.15.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Portable local Python 3.12+ fixture workflow; optional platform commands
  require separately approved credentials.
tags:
- coreweave
- gpu-cloud
- operations
- offline
---
# Workload and GPU health evidence

> Community-contributed; not affiliated with, endorsed by, or sponsored by CoreWeave, Inc.

## Overview

Verify workload readiness, GPU allocation and observed activity from pasted snapshots without changing workloads.
Use Read for supplied evidence and references, Write for a local report, Edit for a proposed local plan, and Grep for relevant log excerpts. Bash is restricted to Python helpers; no helper makes account calls.

## Prerequisites

- Python 3.12+, the supplied evidence contract and explicit intended context/namespace.
- An owner-reviewed resource scope, timestamps, model provenance and applicable platform versions.
- Redacted local inputs; no kubeconfig, token or customer payload in fixtures or reports.

## Instructions

1. Read the evidence contract and classify missing inputs before reviewing a result.
2. Inspect the supplied scope and timestamps. Never fall back to a current context.
3. Run the local helper and preserve the full status, findings and input digest.
4. Resolve blockers and collect missing evidence through an authorized operator.
5. Verify the outcome against the acceptance criteria; distinguish supplied evidence from live observation.

## Examples

Use the fixture replay below before processing redacted operator evidence.

## Output

A JSON report with status, findings, observations, input SHA-256 and evidence boundary.

## Error Handling

| Condition | Response |
| --- | --- |
| Invalid or mismatched input | Stop with a blocker and request corrected evidence. |
| Stale or missing observations | Return incomplete; do not infer healthy or zero cost. |
| Unsupported platform shape | Use a reviewed adapter before claiming compatibility. |

## Resources

- [Primary platform reference](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [CoreWeave official skills](https://github.com/coreweave/skills) for vendor-maintained workflows.

## Offline verification

Supply the Kubernetes `pod` JSON object, `gpu_allocations` mapping Pod UID to GPU UUID, and `gpu_samples` with uuid/pod_uid/at/utilization_percent. Allocation evidence must come from the approved device/Pod mapping; do not join only on a reused Pod name. Samples must be finite, in 0..100 and within five minutes of capture. Positive utilization shows activity in that window, not model correctness, sustained efficiency, all GPU architectures or application health. Idle but healthy batch workloads can return incomplete activity evidence. MIG/MPS/time-slicing need an explicit adapter; do not pretend full-GPU UUID semantics prove those allocations.

From this skill directory, replay the synthetic example (its timestamp is intentionally
fixed; it contains no account data):

```bash
python3 scripts/check-health.py --input tests/fixtures/example.json --as-of 2026-11-05T12:01:00Z
```

For current evidence, omit `--as-of`; it defaults to current UTC. Required common
fields: `schema: coreweave-evidence/v1`, `captured_at`, `context`, `namespace`,
`expected_context`, `expected_namespace`. The scope must agree and evidence must
be at most five minutes old. Explicit replay time is for testing historical fixtures,
not a way to make stale production evidence current.

Exit 0 / `reviewed` means the supplied assertions satisfy this bounded contract;
2 / `blocked` requires correction; 3 / `incomplete` requires more evidence. Read the
findings rather than relying only on exit status. Scripts never execute text from
inputs, call a cloud API or authorize a change. Fixture and package checks are
separate from model behavior and live compatibility.

- [Input contract and limitations](references/evidence-contract.md)
- [Skill blueprint and acceptance](docs/BLUEPRINT.md)

- [Health evidence boundaries](references/health-evidence.md)
