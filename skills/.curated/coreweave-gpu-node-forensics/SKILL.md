---
name: coreweave-gpu-node-forensics
description: |
  Triage a dead or degraded GPU on a CoreWeave node fast — decide reschedule
  vs GPU-reset vs node-reboot vs RMA from an Xid code or a pasted dmesg /
  nvidia-smi blob, so a bad card does not silently kill a multi-day training run.
  Use when a GPU throws an Xid error, a node "fell off the bus", a training run
  stalls or NCCL hangs on one rank, or you need to know whether to replace,
  reset, or just reschedule. Trigger with "xid error", "gpu fell off the bus",
  "coreweave gpu dead", "should I RMA this GPU", "gpu node triage".
allowed-tools: Read, Bash(python3:*), Bash(nvidia-smi -q:*), Bash(kubectl get:*), Bash(dmesg:*)
version: 1.12.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, coreweave, gpu-cloud, reliability, xid]
---

# CoreWeave GPU Node Forensics

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by
> CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.
> "NVIDIA" and "Xid" are trademarks of NVIDIA Corporation; Xid semantics are
> cited from NVIDIA's public documentation.

Triages a dead or degraded GPU on a CoreWeave node in seconds and returns one
grounded move — **reschedule, reset-gpu, reboot-node, rma, watch, or
app-bug-not-hardware** — from an NVIDIA Xid code or a pasted `dmesg` /
`nvidia-smi` blob. The classification is deterministic: a bundled script does the
mapping so the agent never guesses whether a card is dead, degraded, or fine.

## Overview

A single bad GPU can kill a 64-GPU, multi-day training run — thousands of dollars
and days of wall-clock gone — because one rank stalls the whole collective. The
expensive mistakes are triage mistakes: RMAing a healthy card for an app bug,
restarting a job onto a GPU whose memory error was **uncontained**, or manually
uncordoning a node the lifecycle controller is trying to replace. This skill kills
that ambiguity.

The decision logic is grounded in the **NVIDIA Xid error catalog**
(<https://docs.nvidia.com/deploy/xid-errors/>) and CoreWeave's node-lifecycle /
cordon behavior. The math-of-the-matter — which Xid means what, and how
row-remapper state overrides it — lives in `scripts/triage.py` as a table the LLM
does not get to re-litigate. Deep domain knowledge (the full code→action table,
the row-remap decision, the cordon rules) loads from `references/` on demand.

**The headline is the Xid 94-vs-95 split.** A *contained* memory error (94) cost
you one job restart on a healthy node; an *uncontained* one (95) means the GPU
could not isolate the fault and everything it touched is suspect. Getting that one
bit wrong is the difference between a 30-second reschedule and a run that quietly
trained on corrupt gradients. The script decides it; the skill never eyeballs it.

This skill is diagnostic, not destructive: it **recommends** the cordon / drain /
reset / RMA next-step but its tools are scoped read-only (`nvidia-smi -q`,
`kubectl get`, `dmesg`) — it never runs a reset, a reboot, or an uncordon itself.

## Prerequisites

- **The failure evidence.** Either an Xid number, or a pasted `dmesg` /
  `nvidia-smi` dump. The skill works from a paste alone — no live cluster access
  required — which is the common case (an operator pastes what the run's logs
  showed).
- **Optional live access** for corroboration: `kubectl` context on the CoreWeave
  cluster (read-only is enough), and `nvidia-smi` on the node. If neither is
  available the skill still triages from the paste.
- **`python3`** to run the deterministic classifier (`scripts/triage.py`, stdlib
  only — no dependencies).

No secrets are handled. All commands are read-only queries.

## Instructions

The pipeline is **capture → classify → act**. The classifier is authoritative for
the verdict; `references/` supplies the "why" when a case needs depth.

### Step 1: Capture the evidence

If the user has not already pasted it, ask for (or read) the fault signal. The two
richest sources:

```bash
dmesg -T | grep -i xid                       # the Xid line(s) with timestamps
nvidia-smi -q -d ROW_REMAPPER,ECC,PERFORMANCE # remap state, ECC counts, throttle reasons
```

On a CoreWeave node you can also check who owns any cordon before acting:

```bash
kubectl get node NODE -o json | jq '{unschedulable: .spec.unschedulable, taints: .spec.taints}'
```

### Step 2: Run the deterministic triage

Feed the Xid code, or the whole blob, to the classifier. **Do not classify by
hand** — the script owns the Xid→action mapping and the row-remap override.

```bash
# From an Xid code:
python3 "${CLAUDE_SKILL_DIR}/scripts/triage.py" --xid 95

# With row-remapper state (Xid 63/64 or a DBE):
python3 "${CLAUDE_SKILL_DIR}/scripts/triage.py" --xid 63 --pending yes
python3 "${CLAUDE_SKILL_DIR}/scripts/triage.py" --xid 48 --remap-failure yes

# From a pasted dmesg / nvidia-smi blob (file or stdin):
python3 "${CLAUDE_SKILL_DIR}/scripts/triage.py" --blob /path/to/dmesg.txt
dmesg -T | grep -i xid | python3 "${CLAUDE_SKILL_DIR}/scripts/triage.py"
```

The script emits a `VERDICT` block plus a JSON object
(`{classification, severity, action, why, next_command, cordon_rule?, unverified?}`).
Add `--json` for machine-readable output only.

When a blob carries several Xids, the **most severe** one governs the move and the
rest are reported as `co_occurring_xids` — a co-occurring app-side Xid 43 next to a
hardware Xid 79 does not soften the "reboot the node" verdict.

### Step 3: Read the verdict and act on the action

Present the `action` and the `next_command` to the user in plain language. The six
actions and what each means live in
[`${CLAUDE_SKILL_DIR}/references/xid-triage-table.md`](references/xid-triage-table.md).
Load it when the user wants the full table or asks about an Xid not in the summary.

- `reschedule` — restart the failed rank; the node stays in service.
- `reset-gpu` — drain the GPU and reset it; re-run any job that shared it.
- `reboot-node` — the card is off the bus; only a bare-metal reboot returns it.
- `rma` — terminal hardware fault; the card must be replaced.
- `watch` — correctable / trending; monitor, do not act yet.
- `app-bug-not-hardware` — the app faulted, not the GPU. **Do NOT RMA.**

### Step 4: The 94-vs-95 headline (load-bearing — get this right)

If the Xid is **94 or 95**, state the containment explicitly, because the two look
almost identical in the logs and lead to opposite actions:

- **Xid 94 (CONTAINED)** → `reschedule`. The error was isolated to the app's
  context; the GPU and node are healthy. Restart the job. Do not reset or RMA.
- **Xid 95 (UNCONTAINED)** → `reset-gpu`. The GPU could not isolate it; every
  context it touched is suspect. Drain, reset, and re-run anything that shared the
  card — otherwise the run may continue on corrupt state.

### Step 5: Row-remap (Xid 63 / 64 / 48) — routine vs terminal

For any ECC/DBE or row-remap Xid, the `nvidia-smi -q -d ROW_REMAPPER` fields
override the base verdict. Pass them in (`--pending`, `--remap-failure`) and let
the script decide. The rule:

- `Remapping Failure Occurred: Yes` → **`rma`** (terminal — sparing failed).
- `Pending: Yes` (no failure) → **`reset-gpu`** (routine — applies on reset).

Full logic + how to read the histogram:
[`${CLAUDE_SKILL_DIR}/references/row-remap-decision.md`](references/row-remap-decision.md).

### Step 6: The cordon hard rule (never violate)

Whenever the action is a hardware move (`reset-gpu`, `reboot-node`, `rma`), the
verdict carries a `cordon_rule`. Surface it verbatim:

> **Never manually uncordon a CoreWeave health cordon** — the node-lifecycle
> controller owns cordon/uncordon and is driving remediation. Uncordoning
> re-admits the run onto known-bad hardware and races the controller.

Determine cordon provenance before touching schedulability. Full guidance:
[`${CLAUDE_SKILL_DIR}/references/cordon-rules.md`](references/cordon-rules.md).

## Output

- **A verdict** — the deterministic `{classification, severity, action, why,
  next_command}` for the governing signal, presented in plain language with the
  single next command an operator runs.
- **The 94-vs-95 call stated explicitly** when either fires — contained →
  reschedule, uncontained → reset — never conflated.
- **The cordon rule** attached to every hardware action, verbatim, so nobody
  uncordons a node the controller is replacing.
- **Co-occurring Xids** listed when a blob carried several, with the most-severe
  one named as governing.
- **`[unverified]` hedges** surfaced honestly — e.g. CoreWeave's exact auto-RMA
  thresholds and health-cordon taint strings are not publicly published, and the
  skill says so rather than inventing a number.

## Error Handling

| Situation | Cause | Response |
|-----------|-------|----------|
| Unmapped Xid | Xid not in the triage table | Script returns a conservative `reset-gpu` default, flags it `[unverified]`, and points at the NVIDIA catalog. Do not RMA on an unmapped Xid. |
| Xid 94 vs 95 ambiguity | Both are "ECC error" in casual logs | Never infer from prose — use the exact code. 94 = contained (reschedule), 95 = uncontained (reset). |
| Row-remap without an Xid | Only `nvidia-smi` pasted | Script reads `Remapping Failure Occurred` / `Pending` and decides from those alone. |
| App-side Xid mistaken for hardware | Xid 13/31/43/45 | Classed `app-bug-not-hardware`; the fix is compute-sanitizer on the job, **never** an RMA. |
| Multiple Xids in one blob | Cascade (e.g. 43 then 79) | Most-severe governs; others listed as `co_occurring_xids`. |
| Empty / no signal | Blob has no Xid, remap, or thermal line | Script returns `watch` and asks for fresh `dmesg` + `nvidia-smi -q` evidence. |
| Thermal throttle, not a fault | `HW/SW Thermal Slowdown : Active` | Classed `watch` — healthy but hot; investigate cooling, not the card. |
| Tempted to uncordon a stalled node | Health cordon owned by the controller | Refuse. Surface the cordon rule; let remediation run. |

## Examples

### Example 1: "Xid 94 on one rank — do I need to replace the GPU?"

```text
VERDICT: Xid 94 — Contained ECC/memory error [severity: HIGH]
ACTION:  reschedule
WHY:     The error was CONTAINED to the faulting application's context — the GPU
         and node are healthy. Just reschedule/restart the job; no reset or RMA needed.
NEXT:    Restart or reschedule the failed rank; the node stays in service.
```

No replacement. The containment did its job — restart the rank and keep the node.

### Example 2: "Xid 95 — same run, different node"

```text
VERDICT: Xid 95 — Uncontained ECC/memory error [severity: CRITICAL]
ACTION:  reset-gpu
WHY:     The error was UNCONTAINED — the GPU could not isolate it, so every context
         it touched is suspect. Drain the GPU and reset it; treat all in-flight work as corrupt.
NEXT:    Cordon + drain, GPU-reset (nvidia-smi -r) or node reset; re-run any job that shared this GPU.
CORDON:  Do NOT manually uncordon a CoreWeave health cordon — the node-lifecycle
         controller owns cordon/uncordon. Let it drain and replace the node.
```

Opposite of Example 1 despite looking identical in the logs: drain, reset, and
re-run the shared work — do not just restart.

### Example 3: "GPU fell off the bus"

`python3 scripts/triage.py --xid 79` → `reboot-node`. The card is unreachable on
the PCIe bus and returns only after a bare-metal reboot; expect the controller to
cordon and reboot — let it, and RMA only if it recurs after the reboot.

### Example 4: "Xid 63 with a remap failure"

`python3 scripts/triage.py --xid 63 --remap-failure yes` → `rma`. The remapper
tried to swap in a spare row and physically could not — terminal. Cordon, drain,
open the RMA. (The script flags that CoreWeave's exact auto-RMA threshold is
`[unverified]`.)

### Example 5: "Xid 43 killed my job"

`python3 scripts/triage.py --xid 43` → `app-bug-not-hardware`. Software-induced
fault — the fix is in the application (run it under compute-sanitizer), not an RMA.
Pulling the card would waste healthy hardware and never fix the job.

## Resources

- [`${CLAUDE_SKILL_DIR}/references/xid-triage-table.md`](references/xid-triage-table.md) — the full Xid→action table, the six actions, the 94-vs-95 distinction, cited to the NVIDIA Xid catalog.
- [`${CLAUDE_SKILL_DIR}/references/row-remap-decision.md`](references/row-remap-decision.md) — the `ROW_REMAPPER` routine-vs-terminal decision and how to read the histogram.
- [`${CLAUDE_SKILL_DIR}/references/cordon-rules.md`](references/cordon-rules.md) — CoreWeave health-cordon ownership and the safe operator path per action.
- [NVIDIA Xid Errors reference](https://docs.nvidia.com/deploy/xid-errors/)
- [NVIDIA GPU Memory Error Management (row remapping)](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/index.html)
