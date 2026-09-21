---
name: linear-reference-architecture
description: >-
  Design a Linear integration with separated auth, GraphQL, webhook, queue, policy, and reconciliation boundaries. Use when reviewing or creating a durable service architecture. Trigger with "design Linear integration", "architect Linear webhook service", or "review Linear system design".
argument-hint: "[repository-path] [read-only|bidirectional|event-driven]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- architecture
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Integration Reference Architecture

## Overview

Create a repo-grounded architecture that makes authority, data flow, failure containment, and reconciliation explicit. Preserve the host application's boundaries instead of forcing a generic service topology.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Use the official SDK for broad typed access and purpose-built GraphQL queries for narrow high-volume projections.
- Webhook ingress must verify the raw-body HMAC, acknowledge within five seconds, deduplicate by delivery ID, and move durable work to a queue.
- A reconciliation reader is still required because webhooks and downstream consumers can fail or be disabled.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Map callers, workspaces, teams, auth actors, data classes, latency targets, writes, and compliance boundaries from the repository.
2. Separate credential acquisition, Linear adapter, policy/authorization, webhook ingress, durable queue, worker, and reconciliation components.
3. Define stable identifiers, idempotency, pagination checkpoints, partial-error handling, and rate-budget ownership.
4. Keep mutation commands behind policy and approval checks; keep reads and reconciliation independently operable.
5. Design observability around operation metadata and delivery IDs with strict content redaction.
6. Review outage, backlog, schema change, credential rotation, replay, rollback, and tenant-isolation scenarios.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Shared mutable client crosses tenants | Split credential and cache scope by workspace/actor. |
| Webhook does business work inline | Queue after verification and acknowledge quickly. |
| No reconciliation path | Add a cursor-based reader before declaring event-driven completeness. |
| Mutation policy embedded in transport | Separate business authorization from GraphQL mechanics. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
mode=bidirectional; tenants=multi-workspace; freshness=5m; writes=approval-gated
```

Expected handoff:

```text
boundaries=defined; ingress=queued; reconciliation=cursor-based; rollback=owned
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
