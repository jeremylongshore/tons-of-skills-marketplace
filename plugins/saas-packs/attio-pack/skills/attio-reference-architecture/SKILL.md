---
name: attio-reference-architecture
description: >-
  Design a production Attio integration architecture with tenant-bound credentials, schema discovery, queued writes, verified webhooks, idempotency, reconciliation, and rollback ownership. Use when planning or reviewing a multi-workspace Attio service. Trigger with "Attio architecture", "design Attio integration", or "Attio system design".
argument-hint: "[repository-path] [single-workspace|multi-workspace]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- architecture
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Integration Reference Architecture

## Overview

This skill produces a repo-grounded architecture for reliable Attio reads, writes, and events. It treats tenant isolation, duplicate delivery, schema evolution, and reconciliation as first-class controls.

## Prerequisites

- Workspace and tenancy model
- Required objects, lists, attributes, records, entries, and events
- Availability, freshness, recovery, and retention objectives
- Owners for credentials, queues, data mapping, and incident response

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to map components, trust boundaries, state, and existing clients. Use `WebFetch` only for current official Attio contracts. Use `Write` or `Edit` after the architecture, ownership, and approval boundaries are agreed.

## Current Contract

- Use OAuth for multi-workspace applications and a workspace key only for a controlled single-workspace integration.
- Discover object and attribute identifiers rather than hard-coding display labels.
- Pagination differs by endpoint, and record or entry queries can carry score-based rate cost.
- Webhooks are at-least-once signals; durable processing needs signature verification, idempotency, a queue, and reconciliation.

## Authentication

Place a tenant credential resolver behind a server-side interface. Bind each encrypted token to one workspace identity and exact scopes; never accept a workspace identifier from a caller without authorization.

## Instructions

1. Map ingress, egress, data stores, trust boundaries, tenant context, and failure domains from the repository.
2. Define a credential resolver and auditable endpoint-to-scope map.
3. Add a bounded schema registry or cache with explicit refresh and invalidation.
4. Route outbound mutations through idempotent jobs with separate read and write governors.
5. Terminate webhooks at an HTTPS receiver that verifies the raw body, deduplicates by idempotency key, acknowledges quickly, and queues work.
6. Add replay, dead-letter handling, periodic reconciliation, and operator-visible lag metrics.
7. Specify deployment order, canary cohort, rollback, recovery exercise, and component owners.

## Approval Boundaries

Do not broaden data collection, scopes, retention, tenant access, or mutation authority without approval from the relevant data and service owners.

## Output

Return a component-and-data-flow design, trust boundaries, endpoint contracts, failure controls, ownership matrix, rollout sequence, and rollback plan.

## Error Handling

| Condition | Response |
|---|---|
| Tenant cannot be resolved safely | Reject the operation before credential lookup. |
| Schema cache is stale | Refresh discovery and pause incompatible writes. |
| Webhook queue is unavailable | Fail closed so Attio can retry; preserve observability. |
| Reconciliation finds drift | Quarantine conflicting mutations and assign an owner. |

## Examples

Input:

```text
tenancy=multi-workspace; flows=record sync and webhooks; recovery=required
```

Expected handoff:

```text
auth=oauth resolver; writes=queued; webhooks=verified; reconciliation=scheduled
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [REST API overview](https://docs.attio.com/rest-api/overview)
- [Objects and lists](https://docs.attio.com/docs/objects-and-lists)
- [Webhooks](https://docs.attio.com/rest-api/guides/webhooks)
