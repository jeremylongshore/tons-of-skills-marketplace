---
title: "NCCL 2.22 TCP Fallback Prints NET/IB Using: Check Devices"
description: "NCCL 2.22 logs NET/IB : Using on TCP fallback. Count InfiniBand only when a [n]dev:port/IB device entry appears. Caught by 80 hand-labelled public logs."
date: "2026-11-13"
tags: ["debugging", "devops", "testing"]
featured: false
canonical: "https://startaitools.com/posts/nccl-net-ib-using-line-tcp-fallback/"
---
If you run multi-node GPU training and trust a script to tell you whether the job used InfiniBand, that script may be wrong on NCCL 2.22 and later. Our open-source diagnostic scripts reported InfiniBand traffic (a `mixed` verdict) on runs that had fully fallen back to plain TCP sockets. This post shows the one log detail that tells the two apart, and how we found the bug.

Some quick definitions. InfiniBand (IB) is the fast network that GPU nodes use to talk to each other; RoCE is the same idea carried over Ethernet. TCP fallback means the job quietly used ordinary sockets instead, which is much slower. NCCL is NVIDIA's library for moving data between GPUs, and it writes its network choice into the startup log.

From version 2.22 on, that log can say `NET/IB : Using` even when the job fell back to TCP. On a fallback, the list of network cards after it is empty. It shows only the out-of-band (OOB) interface NCCL uses for setup:

```
NET/IB : Using [RO]; OOB eth0
```

Our check matched the phrase `NET/IB : Using`, not a network card. A fallback log also prints a Socket line, so the check saw both transports and reported `mixed` (its label for "some IB, some TCP"). A job running entirely on TCP looked like it was at least partly on InfiniBand.

The fix is one rule for that line. A `NET/IB : Using` line counts as InfiniBand only when it names a real card and port, an entry shaped like `[0]mlx5_0:1/IB` or ending in `/RoCE` (generically `[n]dev:port/IB`). The other two forms the check accepts, `Using network IB` and per-channel `via NET/IB/` lines, still count on their own. The pattern now looks like this:

```python
_IB_NET = r"IB(?:ext(?:_v\d+)?)?"
_IB_SELECTED = re.compile(
    rf"Using network {_IB_NET}\b|NET/{_IB_NET}\s*:\s*Using\s+\[\d+\]\S+:\d+/(?:IB|RoCE)\b|via NET/{_IB_NET}/",
    re.I,
)
```

The device-entry branch is the one that matters for 2.22. The bare `Using [RO]; OOB` line no longer counts. External `IBext` plugins, used for SHARP and COLLNET, count as IB too. The fix also reads pasted lines that lost their `NCCL INFO` prefix, and it treats `NCCL_IB_DISABLE set by environment to 1` as a sign that IB was turned off.

The bug got through because the parser had only been tested against fixtures written alongside it. Self-written fixtures tell you the parser agrees with its author. Logs labelled by someone else can disagree with it.

The fix commit records a run of the helpers against 80 hand-labelled public NCCL and Xid logs. That run found the 2.22 problem. The same change added 27 regression tests, and 24 of them failed before the fix.

The pull request that carried the fix into the marketplace has a before-and-after table. It shows the 2.22 fallback case scoring 0/7, read as mixed, in the corpus run that found the bug. The corpus was not on the machine that built the fix, so the pull request made no claim about accuracy after the fix. A follow-up corpus rerun found one more miss, described below.

The same testing gap hid two defects in the GPU triage helper. Xid is NVIDIA's GPU error code. The helper looked for a section called "Row Remapper". `nvidia-smi -q` prints "Remapped Rows", so a real "Pending: Yes" line was never read. The rerun's miss was in Xid extraction: `NVRM: Xid ...: 13` lines where the PCI tag had been redacted to `...`. The code is now extracted from those lines.

The triage verdicts changed too. Xid 64 now routes to a GPU reset plus a support contact, not an RMA. A remapping failure escalates to support and NVIDIA's field diagnostic before any RMA is considered.

This post quotes no new before-and-after accuracy percentage. The sources give the test counts, the corpus size and the 0/7 row from that first corpus run. They do not give a final corpus score, so none appears here.

The pack is an unofficial community project. It is not affiliated with or endorsed by CoreWeave, Inc.

## Use this

- Require a `[n]dev:port/IB` or `/RoCE` device entry before your log check treats a `NET/IB : Using` line as InfiniBand. With an empty device list, that line is a TCP fallback until other evidence proves otherwise.
- Run your parser against real logs you labelled by hand, and keep your own fixtures as a second check. Compare against the helpers and their 27 regression tests at https://github.com/jeremylongshore/unofficial-coreweave-operator-pack.
- Test your triage parser against a real `nvidia-smi -q` capture (section names like "Remapped Rows"), and your Xid extraction against real, redacted `NVRM: Xid` lines.

## Related Posts

- [July 2026 field guide to CoreWeave GPU failure modes](https://startaitools.com/posts/coreweave-gpu-ops-field-guide/)
