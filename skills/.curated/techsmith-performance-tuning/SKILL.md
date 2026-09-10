---
name: techsmith-performance-tuning
description: >-
  Optimize Snagit capture and Camtasia project/export throughput from measured workstation bottlenecks and safe concurrency limits. Use when queues are slow, unstable, or resource-bound. Trigger with "TechSmith performance", "Camtasia export tuning", or "Snagit capture throughput".
argument-hint: "[workload-manifest] [workstation-alias]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- performance
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Workstation Performance Tuning

## Overview

This skill improves throughput without assuming server-style horizontal scale. It measures one representative workload, separates capture from export bottlenecks, keeps active Camtasia data local, and changes one resource or concurrency control at a time.

## Prerequisites

- A representative, non-sensitive capture or project workload and acceptance criteria
- Baseline wall time, CPU, GPU, memory, disk, output size, and failure rate
- Product/version, hardware, local scratch path, and export preset
- A rollback point and permission for any preference or driver change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Serialize interactive Snagit captures per desktop unless validated isolation proves otherwise.
- Keep Camtasia project media, scratch, and export output on a fast local non-synced drive while active.
- Bound parallel exports by measured CPU/GPU/memory/disk headroom and licensed workstation capacity.
- Do not trade correctness, media validation, or workstation stability for raw queue throughput.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Capture a cold and warm baseline for one fixed workload with product/version and preset pinned.
2. Identify the dominant constraint: interactive desktop, source media decode, CPU, GPU, memory, local disk, codec, or operator wait.
3. Set a conservative worker limit and queue backpressure from measured peak headroom.
4. Apply one reversible change such as local scratch, proxy behavior, preset correction, or worker count.
5. Repeat the identical workload and compare duration, utilization, output properties, and failure rate.
6. Keep only changes that improve the declared service objective without a quality or stability regression.

## Approval Boundaries

Do not edit projects on cloud/network storage, disable security software, force undocumented command flags, or launch duplicate exporters to manufacture concurrency.

## Output

Return baseline and candidate metrics, bottleneck, change, before/after delta, quality checks, safe worker limit, rollback, and monitoring threshold.

## Error Handling

| Condition | Response |
|---|---|
| Workload is not reproducible | Freeze inputs and preset before drawing conclusions. |
| Disk saturation | Reduce workers and stage active files on approved local storage. |
| Output differs | Reject the optimization and restore the baseline configuration. |
| Crash rate increases | Rollback immediately and preserve redacted diagnostics. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
workload=training-20m; workers=1->2; duration=-28%; peak_mem=82%; quality=pass; decision=keep
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Camtasia local-storage guidance](https://support.techsmith.com/hc/en-us/articles/203730028-Working-with-Camtasia-Editor-TSCPROJ-and-TREC-Files)
- [Cloud storage compatibility](https://support.techsmith.com/hc/en-us/articles/203732738-Cloud-Storage-Compatibility-FAQ)
