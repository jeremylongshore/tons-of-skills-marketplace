---
name: notion-architecture-variants
description: >-
  Choose a Notion integration architecture from explicit consistency, latency, security, and recovery requirements. Use when comparing synchronous, queued, scheduled, or webhook-driven designs. Trigger with "design Notion architecture", "choose Notion sync pattern", or "review Notion topology".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <consistency-objective> <environment>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, architecture]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Integration Architecture Decision

## Overview

Choose a Notion integration architecture from explicit consistency, latency, security, and recovery requirements.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Notion exposes versioned REST resources, paginated reads, connection webhooks, and mutable limits. Architecture must tolerate additive response fields, out-of-order signals, partial pagination, and changing quotas. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Map each component to a distinct connection or token boundary. Keep inbound webhook verification material, Notion access, queue administration, and destination credentials separated.

## Instructions

1. State the business operation, source of truth, consistency objective, recovery point, and recovery time.
2. Inventory reads, writes, webhook signals, scheduled reconciliation, files, and downstream processors.
3. Compare direct request, queued worker, scheduled batch, and webhook-plus-reconciliation variants.
4. Model pagination, retry, idempotency, backpressure, dead letters, and replay for each candidate.
5. Threat-model credentials, workspace content, tenant isolation, logs, and operator privileges.
6. Choose one variant with rejected alternatives, capacity assumptions, rollout gates, and rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require security and data-owner approval for new connections, external processors, production queues, workspace-wide access, or cross-tenant data movement.

## Error Handling

- A webhook is a change signal, not a complete or ordered event log.
- Do not multiply tokens to evade connection limits.
- Reject a design without reconciliation and replay boundaries.

## Output

Return a decision record, context diagram, trust boundaries, capacity model, failure modes, rollout stages, and rollback triggers. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Choose webhook plus reconciliation for freshness without treating delivery as a ledger.
- Choose a bounded scheduled export when latency is secondary to auditability.

## Validation

Exercise and record these paths with expected and observed results:

- failure injection
- pagination completeness
- duplicate safety
- out-of-order handling
- tenant isolation
- rollback rehearsal

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
