---
name: linktree-webhooks-events
description: 'Review an approved Linktree partner event mechanism or choose a documented export and polling alternative without inventing webhooks. Use when synchronizing Linktree changes or analytics. Trigger with "review Linktree events".'
argument-hint: "[contract-path] [consumer]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- events
- partner-contract
- data-sync
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Partner Event Contract Review

## Overview

Establish whether an authorized event contract actually exists, then design validation, replay, ordering, reconciliation, and fallback from evidence rather than generic webhook conventions.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- The public developer page announces program-gated APIs and SDKs but publishes no general event catalog or verification scheme.
- Linktree documents on-screen Insights and plan-dependent CSV exports as public data-access paths.
- Event delivery details are private-contract facts and must not be inferred from another provider.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Name the synchronization objective, data owner, consumer, freshness requirement, data classification, and reconciliation authority.
2. Use Read, Glob, and Grep to inspect the supplied partner contract, event fixtures, consumer code, and export workflow without reading secrets.
3. If an approved event mechanism exists, build an evidence table for event names, schema revision, authentication, replay protection, ordering, retries, retention, and acknowledgment behavior.
4. If it does not exist, choose the least-privileged documented alternative: operator review, authorized Insights CSV, or a contract-approved polling operation.
5. Test synthetic duplicates, out-of-order delivery, unknown fields, stale exports, consumer failure, and reconciliation.
6. Use Write or Edit to record the design and fixtures only after authority and retention are clear.
7. Use WebFetch only for official public export guidance or approved partner documentation.

## Approval Boundaries

Do not expose a receiver, accept live deliveries, or process subscriber data until authentication, consent, retention, deletion, and incident handling are approved.

## Output

Return objective, documented mechanism, contract revision, authentication evidence, event or export schema, failure tests, reconciliation path, data controls, and go/no-go.

## Error Handling

| Condition | Response |
|---|---|
| Event verification is undocumented | Do not deploy a receiver; obtain the partner contract or use a documented alternative. |
| Export contains unnecessary personal data | Minimize fields and storage before processing. |
| Consumer cannot reconcile duplicates | Add idempotency and a bounded replay test before launch. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
objective=weekly-performance-sync; mechanism=authorized-CSV; personal-data=none; duplicates=tested; reconciliation=profile+window; receiver=not-deployed; result=go
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
