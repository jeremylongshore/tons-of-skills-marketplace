---
name: coreweave-fabric-diagnostics
description: |
  Diagnose the most expensive silent failure on a CoreWeave multi-node GPU job:
  GPUDirect RDMA falling back from InfiniBand to TCP. When NCCL drops from NET/IB to
  NET/Socket, collectives keep running with NO error but throughput collapses (commonly
  5-20x slower) while every GPU still bills at full rate — 5x the GPU bill for the same
  work, invisibly. Paste an NCCL_DEBUG=INFO log (and/or a pod-spec, ibstat, or
  all_reduce_perf output) and the bundled deterministic script verdicts whether RDMA is
  actually engaged, which of the three required conditions is missing, and the fix.
  Use when multi-node training is slow, when checking whether RDMA/InfiniBand is engaged,
  or when all-reduce bandwidth looks low. Trigger with "coreweave slow training", "is RDMA
  working", "NCCL fell back to TCP", "NET/Socket", "GPUDirect RDMA", "infiniband not
  used", "multi-node training slow".
allowed-tools: Read, Write, Edit, Glob, Bash(kubectl get:*), Bash(python3:*)
version: 1.12.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, coreweave, gpu-cloud, rdma, nccl]
---

# CoreWeave Fabric Diagnostics

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by
> CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

Detects when a CoreWeave multi-node GPU job has silently fallen off the InfiniBand fabric
onto TCP — the failure that makes distributed training run at a fraction of the hardware's
speed while every GPU keeps billing at the full rate — and gives the exact fix.

## Overview

On a CoreWeave multi-node job, NCCL should carry collectives over **InfiniBand with
GPUDirect RDMA** (`NET/IB`). If any one of three conditions is missing, NCCL **silently
falls back to TCP sockets** (`NET/Socket`): the job still runs, still converges, and
raises **no error** — but all-reduce throughput collapses (commonly cited as **5-20x
slower** [[nccl]]) because it now crosses the Ethernet control plane instead of the
400 Gb/s-class fabric. You keep paying full GPU rate for a multi-node run that performs
like a badly-connected one. This is the single highest-dollar invisible failure on the
platform, and nothing in the default output flags it.

The diagnosis is **deterministic**: the bundled `scripts/fabric-check.py` greps the pasted
`NCCL_DEBUG=INFO` log for the decisive `Using network` line (and `NET/IB` vs `NET/Socket`),
parses the pod-spec's `resources` block for the RDMA device request, reads `ibstat` port
state, and echoes any `all_reduce_perf` bus bandwidth — then emits a VERDICT with the
`rdma_engaged`/`transport` call, the missing conditions, and the fix. The LLM never
eyeballs which transport is in use; the script decides. Deep grounding lives in
`references/`, loaded only when a leg of the diagnosis needs it.

## Prerequisites

- **An `NCCL_DEBUG=INFO` log from the actual run** — the primary signal. Re-run the job
  (or one rank) with `NCCL_DEBUG=INFO` set and capture stderr. The decisive line is
  `Using network IB` (good) vs `Using network Socket` (the fallback). This is the one input
  the skill really needs; everything else corroborates.
- **Optional, for a full diagnosis:** the pod/job spec (`kubectl get pod NAME -o yaml`) to
  check the RDMA device request; `ibstat` output from the node for port health; and
  `all_reduce_perf` results from CoreWeave's [nccl-tests][nt] to measure bus bandwidth.
- **`python3`** to run the deterministic checker (stdlib only).
- **`kubectl` (read-only)** if corroborating the live pod spec / node cordon state.

**Authentication.** Nothing secret is read. If the pod spec is pulled live, `kubectl` uses
the existing `$KUBECONFIG`; the skill only ever runs `kubectl get` (read-only) — it never
cordons, drains, or applies.

## The three required conditions (all must hold, or NCCL falls back)

1. **The RDMA device is requested in BOTH `resources.requests` AND `resources.limits`**
   (`rdma/ib: 1`). If it is in only one — or absent — the device plugin does not inject the
   IB device into the pod and NCCL never sees a HCA. [unverified — the exact resource key
   (e.g. `rdma/ib`) depends on the installed RDMA device-plugin config; confirm with
   `kubectl describe node` / `kubectl get node -o yaml`.]
2. **`NCCL_IB_HCA=ibp` and `NCCL_SOCKET_IFNAME=eth0` are set** (CoreWeave's documented
   values [[cw]]) — unless you launch via the **MPI Operator**, which manages this network
   config for you [[nt]].
3. **`NCCL_DEBUG=INFO` then confirms `NET/IB`** (ideally a `GPU Direct RDMA Enabled` line).
   If it shows `NET/Socket` / `Using network Socket`, RDMA is not engaged.

Full checklist with verification commands: [`references/rdma-engagement-checklist.md`](references/rdma-engagement-checklist.md).

## Instructions

The pipeline is **gather → verdict → fix → confirm**. The script does the transport call;
`references/` carry the grounding:

1. Gather the `NCCL_DEBUG=INFO` log (required) plus any pod-spec / ibstat / all_reduce_perf
   output you have. Concatenate them into one paste — the checker keys on each signal
   independently.
2. Run the deterministic checker to get the VERDICT.
3. If the verdict is **fallback (Socket)**, apply the three-condition fix and re-run.
4. If the verdict is **IB but degraded**, chase the degraded signal (port down / low busbw).
5. On NVSwitch systems with a stuck fabric, use the Fabric Manager reset order.

### Step 1: Gather the evidence

The log is the load-bearing input. If the user has not run with `NCCL_DEBUG=INFO`, tell
them to — without it, transport selection is unknowable. To pull the live pod spec:

```bash
kubectl get pod "$POD" -o yaml > pod.yaml
```

### Step 2: Run the deterministic checker (it makes the call, not the model)

Pipe everything you gathered to `fabric-check.py`. It greps for the decisive `Using
network` line, the `resources` block, `ibstat` state, and any `Avg bus bandwidth`:

```bash
cat nccl-debug.log pod.yaml ibstat.txt allreduce.txt 2>/dev/null | \
  python3 scripts/fabric-check.py
```

The verdict names `rdma_engaged` (yes/no/partial/unknown), the `transport` in use, the
missing conditions, and the fix. Use `--json` to capture the structured result for further
processing. Reading the log by eye is what this step exists to prevent — see
[`references/nccl-debug-reading.md`](references/nccl-debug-reading.md) for what each line
means.

Use `Glob` to gather multiple pasted log files when a run spans several ranks, `Write` the
verdict report to the working directory, and `Edit` it to refine the fix as the user
iterates on the manifest.

### Step 3: If the verdict is fallback (NET/Socket) — apply the three-condition fix

This is the money case. Fix in order (the checker prints the same list):

1. Add `rdma/ib: 1` to **both** `resources.requests` and `resources.limits`.
2. Set `NCCL_IB_HCA=ibp` and `NCCL_SOCKET_IFNAME=eth0` (or launch via the MPI Operator).
3. Re-run with `NCCL_DEBUG=INFO` and confirm the log now shows `NET/IB` +
   `GPU Direct RDMA Enabled`, not `NET/Socket`.

If the log shows `NCCL_IB_DISABLE=1`, that alone forces sockets — set it to `0` (RoCE and
IB both need the IB verbs transport enabled [[env]]).

### Step 4: If the verdict is IB-but-degraded — chase the degraded signal

RDMA can be engaged yet slow. Two corroborating checks:

- **`ibstat`** — every port must read `State: Active` / `Physical state: LinkUp`. A port
  `Down`/`Polling`, or a link that flaps, drags the whole collective; CoreWeave
  auto-cordons flapping links, so a shrinking node count mid-run is a fabric symptom.
- **`all_reduce_perf` bus bandwidth** — compare the reported `busbw` against **CoreWeave's
  published nccl-tests manifest baseline for your GPU count + NCCL version** [[nt]]. Do
  **not** compare against a fixed number: the baseline moves with GPU type, node count, NCCL
  version, and SHARP. The checker echoes the observed figure tagged `[unverified vs
  baseline]` precisely so nobody reads it as a hard pass/fail.

Details + the busbw-vs-algbw distinction: [`references/allreduce-baseline.md`](references/allreduce-baseline.md).

### Step 5: NVSwitch systems — Fabric Manager reset order

On NVSwitch/NVLink systems, a wedged fabric shows up as NVLink/NVSwitch errors rather than
IB fallback. The safe reset order is **stop Fabric Manager → reset the GPUs → start Fabric
Manager**, never the reverse:

```bash
sudo systemctl stop nvidia-fabricmanager
sudo nvidia-smi -r            # GPU reset
sudo systemctl start nvidia-fabricmanager
```

`[unverified — service unit name and reset support vary by image/driver; on managed
CoreWeave nodes prefer opening a support ticket / cordoning over an in-place reset.]`

## Output

- **A VERDICT line** stating whether RDMA is engaged, the transport actually in use, and —
  for the fallback case — the plain-language cost framing (running on TCP, paying full GPU
  rate for a fraction of the throughput).
- **The missing-conditions list** — which of the three required conditions is absent, each
  one sufficient on its own to force the fallback.
- **The ordered fix** — the `rdma/ib`-in-requests-AND-limits change, the env vars, and the
  re-verify step.
- **Degraded-fabric signals** when RDMA is engaged but slow — down/flapping IB ports and the
  observed `busbw` (tagged `[unverified vs baseline]`).

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Verdict is `unknown` | No `NET/IB` / `NET/Socket` / `Using network` line in the paste | Re-run the job with `NCCL_DEBUG=INFO` and capture stderr; without it transport is unknowable. |
| Verdict `Socket` but the pod "has RDMA" | `rdma/ib` in `limits` only (or only `requests`) | Add it to BOTH blocks; the device plugin injects the IB device only when the resource is requested. |
| `NET/IB` present yet training still slow | GDR not actually enabled; `nvidia-peermem` unloaded → traffic stages through host memory | Confirm a `GPU Direct RDMA Enabled` line; verify `nvidia-peermem` is loaded on the node [[nccl]]. |
| `busbw` "looks low" | Compared against a wrong/guessed baseline | Compare only against CoreWeave's nccl-tests manifest baseline for your GPU count + NCCL version; the number is workload/version-dependent. |
| Nodes drop out mid-run | Flapping IB link → CoreWeave auto-cordon | Check `ibstat` for `Physical state` != `LinkUp`; the cordoned node's link is the cause, not your job. |
| `rdma/ib` resource not schedulable | Wrong resource key for the installed device plugin | Confirm the exact key with `kubectl describe node` (search the Allocatable list) and substitute it. |

## Examples

### Example 1: "Our 4-node H100 training run got slow — is RDMA even working?"

The user pastes an `NCCL_DEBUG=INFO` excerpt plus the pod spec. The checker finds `Using
network Socket` and `rdma/ib` only in `requests`, and verdicts:

```text
### VERDICT: RDMA is NOT engaged -- NCCL fell back to TCP (NET/Socket). Multi-node collectives are running over the Ethernet control plane, commonly 5-20x slower for the same GPU-hours -- you pay full GPU rate for a fraction of the throughput, and NCCL raised no error.

- RDMA engaged: **no**
- Transport in use: **Socket**
- Missing conditions (each one alone forces a silent TCP fallback):
    - `rdma/ib` missing from resources.limits
    - `NCCL_IB_HCA` not set (e.g. `ibp`) -- unless the MPI Operator manages it

**The fix (in order):**
1. Request the RDMA device in BOTH requests AND limits: `rdma/ib: 1` (if it is in only one, the device plugin will not inject the IB device).
2. Set `NCCL_IB_HCA=ibp` and `NCCL_SOCKET_IFNAME=eth0` (CoreWeave values), or let the MPI Operator manage them.
3. Re-run with `NCCL_DEBUG=INFO` and confirm the log now shows `NET/IB` and `GPU Direct RDMA Enabled` -- not `NET/Socket` / `Using network Socket`.
4. Confirm each IB port is `State: Active` / `Physical state: LinkUp` via `ibstat`; a flapping link gets auto-cordoned by CoreWeave.
```

### Example 2: "RDMA is on but all-reduce bandwidth seems low"

The log shows `NET/IB` and `GPU Direct RDMA Enabled`, so the checker returns
`rdma_engaged: yes`. It then surfaces the `ibstat` port that reads `Physical state:
Polling` as a degraded signal and echoes the observed `busbw` tagged `[unverified vs
baseline]`, directing the user to compare against CoreWeave's nccl-tests manifest for their
GPU count + NCCL version rather than a guessed number.

## Resources

- [`references/rdma-engagement-checklist.md`](references/rdma-engagement-checklist.md) — the three required conditions + how to verify each, cited.
- [`references/nccl-debug-reading.md`](references/nccl-debug-reading.md) — reading `NCCL_DEBUG=INFO`: `NET/IB` vs `NET/Socket`, the decisive `Using network` line, GDR.
- [`references/allreduce-baseline.md`](references/allreduce-baseline.md) — `all_reduce_perf` busbw/algbw and why the baseline is never hardcoded.
- Sibling: `coreweave-gpu-cost-leak-hunter` dollarizes idle/right-sizing spend; this skill finds the throughput leak (fabric fallback) that a cost report cannot see.

[cw]: https://docs.coreweave.com/docs/products/networking/hpc-interconnect/use-gpudirect-rdma
[nt]: https://github.com/coreweave/nccl-tests
[nccl]: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html
[env]: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html
