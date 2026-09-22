---
name: notion-load-scale
description: >-
  Plan and test Notion workload capacity within observed limits without evading per-connection controls. Use when scaling exports, syncs, workers, or high-volume reads. Trigger with "scale Notion integration", "capacity plan Notion", or "load test Notion safely".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <target-volume> <test-environment>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, capacity]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Capacity and Backpressure Planning

## Overview

Plan and test Notion workload capacity within observed limits without evading per-connection controls.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Notion documents an average request rate and payload limits but may change quotas. Capacity planning must honor Retry-After, response latency, page size, pagination depth, downstream pressure, and tenant fairness. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Use synthetic non-production content and one approved test connection. Additional tokens are not a sharding mechanism for bypassing limits.

## Instructions

1. Define volume, freshness, concurrency, burst, payload, tenant, and recovery objectives.
2. Measure a low-rate baseline by operation using synthetic fixtures.
3. Model request amplification from pagination, block recursion, retries, reconciliation, and downstream failures.
4. Introduce queue rate control, tenant fairness, bounded concurrency, and backpressure.
5. Increase load in approved stages while observing 429, Retry-After, latency, errors, queue age, and completeness.
6. Set safe operating limits, saturation alarms, degradation behavior, and rollback thresholds.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require platform and workspace-owner approval for load tests; never run them against production content or multiply credentials to raise throughput.

## Error Handling

- Stop when error, latency, queue age, or Retry-After exceeds the stage threshold.
- Do not treat burst success as sustained capacity.
- Preserve unacknowledged cursors when downstream systems fail.

## Output

Return the workload model, measured curve, amplification factors, safe envelope, fairness policy, degradation plan, and rollback threshold. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Size a paginated export worker with bounded downstream writes.
- Prove one noisy tenant cannot starve another queue partition.

## Validation

Exercise and record these paths with expected and observed results:

- sustained load
- burst
- 429 recovery
- downstream stall
- tenant fairness
- checkpoint restart

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
