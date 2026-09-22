---
name: clickup-reference-architecture
description: >-
  Analyze and design a governed ClickUp integration with typed v2/v3 adapters, Workspace policy, durable events, reconciliation, telemetry, and reversible writes. Use when shaping a production ClickUp service. Trigger with "ClickUp architecture", "design ClickUp sync", or "ClickUp integration blueprint".
argument-hint: "[system-context] [one-way|two-way]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- architecture
model: inherit
effort: high
compatibility: Designed for Claude Code; production design requires current ClickUp plan, data, and authorization facts
---
# ClickUp Integration Reference Architecture

## Overview

Separate provider transport, tenancy policy, business mapping, durable execution, and evidence so API evolution or partial failure does not corrupt work.

## Prerequisites

- System boundaries, source-of-truth decision, data classes, latency/freshness SLOs, and ownership
- Endpoint/version and plan inventory for required ClickUp capabilities
- Failure, reconciliation, rollback, and incident requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Use explicit v2 and v3 clients because ClickUp exposes only selected v3 surfaces today.
- Resolve v2 `team_id` to the application Workspace tenant boundary before every operation.
- Treat webhooks as signed change signals processed through a durable idempotent queue, not as a complete event log.
- Writes require stable source identity, reconciliation, and compensating/rollback policy.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Define source of truth and field-level ownership for every one-way or two-way mapping.
2. Place auth and Workspace authorization in a policy layer above versioned transports.
3. Model commands and events with durable IDs, mapping versions, and idempotency records.
4. Add rate-aware queues, webhook ingress, reconciliation sweeps, and dead-letter review.
5. Separate content-free telemetry/evidence from sensitive payload storage and retention.
6. Exercise auth, plan, rate, webhook-gap, partial-write, schema-drift, and rollback scenarios.

## Approval Boundaries

Do not permit autonomous destructive writes, cross-Workspace routing, ACL changes, or conflict resolution without explicit product-owner policy.

## Output

Return component/data-flow design, version matrix, trust and tenant boundaries, failure modes, SLOs, reconciliation, approvals, and rollback.

## Error Handling

| Condition | Response |
|---|---|
| Source of truth is ambiguous | Stop two-way design until ownership is decided. |
| Required endpoint is plan-gated | Record the dependency and approved alternative. |
| Webhook-only design cannot reconcile gaps | Add source reads and durable checkpoints. |
| Compensation is impossible | Narrow write scope or require manual approval. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
mode=two-way; versions=v2-tasks+v3-audit; tenant-guard=required; queue=durable; reconcile=hourly; destructive=manual
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API v2 and v3 terminology](https://developer.clickup.com/docs/general-v2-v3-api)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
