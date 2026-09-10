---
name: salesloft-reference-architecture
description: >-
  Design a multi-team Salesloft integration with explicit tenant, auth, client, scheduler, cursor, webhook, queue, reconciliation, and ownership boundaries. Use when reviewing or creating production architecture. Trigger with "Salesloft architecture", "design Salesloft integration", or "Salesloft multi-tenant system".
argument-hint: "[repository-path] [architecture-scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- architecture
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Integration Reference Architecture

## Overview

This skill maps Salesloft integration responsibilities into inspectable components and data flows. It treats tenant isolation, rate sharing, and reconciliation as architectural requirements rather than library details.

## Prerequisites

- Business workflows, team topology, data classes, and service objectives
- Auth-flow and endpoint/scope inventory
- Hosting, queue, database, secret-store, and observability constraints
- Named service, security, data, and incident owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository topology, boundaries, schemas, and deployment files. Use `WebFetch` only for official Salesloft contracts. Use `Write` or `Edit` after confirming the intended architecture artifact.

## Current Contract

- Every request carries an explicit team context and tenant-bound Bearer credential.
- The client preserves endpoint-specific requests, response envelopes, pagination, and rate metadata.
- A scheduler coordinates the team-wide cost budget across workers and integrations.
- Incremental readers persist microsecond `updated_at` cursors with overlap and deduplication.
- Webhook ingress preserves raw bytes, verifies SHA-1 HMAC and callback token, then queues durable idempotent work.

## Authentication

Model separate authorization-code, customer API-key, and private client-credentials lifecycles. Keep encrypted credentials and refresh state keyed by immutable Salesloft team identity.

## Instructions

1. Map actors, Salesloft teams, trust zones, data classes, and all read/write flows.
2. Define tenant context at ingress and carry it through client, queue, cache, database, and logs.
3. Place auth resolution and refresh behind a serialized tenant-bound service.
4. Place request shaping, envelopes, paging, errors, and rate headers behind a narrow client.
5. Separate webhook receipt from processing and pair it with cursor-based reconciliation.
6. Define mutation ownership, idempotency, read-after-write, and repair workflows.
7. Add metrics and runbooks for auth, status, cost, remaining budget, lag, duplicates, and reconciliation.

## Approval Boundaries

Do not centralize mutable global credentials, share tenant caches, accept webhooks before verification, or create a write path without ownership and repair controls.

## Output

Return component and data-flow diagrams, tenant invariants, auth model, endpoint boundaries, rate scheduler, webhook/reconciliation design, failure modes, owners, and open decisions.

## Error Handling

| Condition | Response |
|---|---|
| Tenant context absent | Reject before resolving credentials or data. |
| Queue duplicates | Deduplicate before side effects and retain receipt history. |
| Cursor corruption | Restore last committed checkpoint and replay overlap. |
| Provider/API failure | Degrade boundedly, preserve work, and reconcile after recovery. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
teams=12; auth=tenant-bound; limiter=per-team; webhook=verified; reconciliation=daily
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API basics](https://developers.salesloft.com/docs/platform/api-basics/)
- [Efficient cursor poller](https://developers.salesloft.com/docs/platform/guides/building-an-efficient-cursor-poller/)
- [Webhook introduction](https://developers.salesloft.com/docs/platform/webhooks/introduction/)
