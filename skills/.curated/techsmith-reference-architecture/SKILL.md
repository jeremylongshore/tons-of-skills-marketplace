---
name: techsmith-reference-architecture
description: >-
  Design a controlled architecture for Snagit capture and Camtasia recording/export workers with local scratch, durable manifests, validation, and artifact promotion. Use when moving beyond one-off scripts. Trigger with "TechSmith architecture", "Snagit automation design", or "Camtasia worker topology".
argument-hint: "[system-context] [diagram-or-design-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- architecture
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Desktop Media Automation Architecture

## Overview

This skill separates orchestration from licensed desktop execution. A control plane stores only job intent and redacted state; approved Windows or macOS workers perform version-pinned product operations on local storage; validators promote immutable outputs to archive or publishing systems after the application closes.

## Prerequisites

- Workload classes, data classifications, service objectives, and expected volume
- Endpoint and entitlement inventory with product/version/platform capabilities
- Storage, network, identity, logging, retention, and incident constraints
- Approval owners for capture scope, deployment, activation, and publication

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Snagit COM jobs run only on licensed Windows workers with an interactive desktop.
- Camtasia active projects and media remain local and non-synced; promoted outputs are immutable artifacts.
- Job manifests carry product version, operation, input hashes, output policy, deadline, and idempotency key.
- Workers expose redacted state transitions, not remote arbitrary-shell access or license secrets.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Discover existing scripts, workers, endpoints, storage paths, product versions, licenses, and downstream consumers.
2. Define job classes and state transitions from accepted through staged, running, validating, promoted, failed, or quarantined.
3. Partition workers by platform, product/version, interactive capability, and data classification.
4. Design local scratch, durable manifests, checksums, output validation, post-close archival, and retention cleanup.
5. Add admission control, per-session capture locks, bounded export workers, health probes, and dead-letter handling.
6. Document trust boundaries, failure modes, rollback, recovery-time objectives, and migration from current scripts.

## Approval Boundaries

Do not centralize raw license keys, captures, or project media in the control plane. Do not treat desktop workers as generic remote execution hosts.

## Output

Return current and target topology, job/state model, trust boundaries, worker capability matrix, data flow, failure handling, migration stages, and unresolved decisions.

## Error Handling

| Condition | Response |
|---|---|
| Worker capability unknown | Probe version and supported interfaces before assigning a job class. |
| Active data crosses to sync storage | Stage locally and promote only after product closure and validation. |
| Control plane needs product secrets | Redesign so activation stays endpoint-managed. |
| No idempotency boundary | Add durable job and output identities before enabling retries. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
control-plane -> signed job manifest -> licensed local worker -> validator -> immutable artifact store
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Deployment overview](https://support.techsmith.com/hc/en-us/articles/43771074923021-Deploying-TechSmith-Products)
- [Camtasia file model](https://support.techsmith.com/hc/en-us/articles/203730028-Working-with-Camtasia-Editor-TSCPROJ-and-TREC-Files)
