---
name: miro-reference-architecture
description: "Analyze and execute this workflow: design tenant-safe Miro boundaries across Web SDK, backend OAuth, REST adapters, queues, and reconciliation. Use when planning a Miro integration. Trigger with \"miro integration reference architecture\"."
argument-hint: "[use-case] [deployment-model]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- architecture
- design
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Integration Reference Architecture

## Overview

Put each capability at the correct browser, backend, tenant, and persistence boundary; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Approved Miro application, tenant, and board scope
- Current repository and deployment evidence
- Named owner, success criteria, and rollback or recovery boundary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Web SDK operates in loaded board contexts; REST requires OAuth Authorization Code.
- Hybrid apps configure SDK authorization for backend REST authentication.
- Tokens must bind to app, user, team, and scopes.
- Durable change capture requires reconciliation because REST webhooks were retired.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Map actors, tenants, boards, data classes, journeys, and destructive operations.
2. Assign in-board interaction to Web SDK and durable orchestration to backend REST.
3. Define OAuth callback, rotating encrypted token storage, tenant authorization, and revocation.
4. Add weighted queues, cursor checkpoints, operation records, reconciliation, and safe telemetry.
5. Design failures for auth loss, tenant mismatch, 429, ambiguous writes, drift, and outage.
6. Review scopes, retention, capacity, recovery, and experimental use with owners.

## Approval Boundaries

Shared tokens, browser-held client secrets, unbounded polling, and experimental dependencies require architecture/security approval and should normally be rejected. Pause when the responsible owner or exact target is uncertain.

## Output

Return scope, observed contract, proposed or completed actions, verification evidence, approvals, residual risks, and next owner. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Tenant or board context mismatches | Stop before mutation and quarantine the credential mapping. |
| Current docs contradict the implementation | Treat the official current contract as a blocker and design an explicit migration. |
| A mutation result is ambiguous | Reconcile state before retrying. |
| Required evidence is unavailable | Return a blocked decision with the smallest safe next probe. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
ui=web-sdk; auth=backend-oauth; rest=v2; tokens=tenant-bound; events=5m-reconcile
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [REST auth from Web SDK](https://developers.miro.com/docs/enable-api-authentication-from-sdk-authorization)
- [REST introduction](https://developers.miro.com/reference/overview)
