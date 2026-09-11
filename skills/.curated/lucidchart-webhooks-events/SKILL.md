---
name: lucidchart-webhooks-events
description: 'Implement and operate the documented Lucid data-connector webhook lifecycle. Use when a connector needs webhook-assisted source synchronization. Trigger with "Lucid connector webhook".'
argument-hint: "[connector-path] [source-system]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, data-connectors, webhooks, synchronization]
model: inherit
effort: high
compatibility: Designed for Claude Code; webhook registration, public endpoints, source credentials, replay, and production enablement require connector and source-owner approval
---
# Lucid Data-Connector Webhook Lifecycle

## Overview
Build webhook-assisted data synchronization only within Lucid's documented data-connector model. Do not claim generic Lucid document, shape, or collaboration event webhooks.

## Prerequisites
- A justified Lucid data connector and supported source-system webhook contract
- Stable source record/event identifiers and reconciliation API
- Endpoint, identity, retention, observability, replay, and rollback owners

## Tool Discipline
Use `Read`, `Glob`, and `Grep` to inspect connector and handler code, `WebFetch` for current Lucid and source contracts, and `Write` or `Edit` only for local implementation, synthetic fixtures, and redacted receipts.

## Current Contract
Lucid documents a webhook SDK in the context of data connectors. Exact interfaces come from the current SDK/docs. Delivery authentication, signing, event names, ordering, retry, and retention may be source-system responsibilities and must be verified there—not invented as universal Lucid guarantees.

## Authentication
Authenticate each boundary independently: Lucid connector, webhook source, and upstream reconciliation API. Keep secrets server-side; validate the source's documented authenticity mechanism and never invent a `LUCID_WEBHOOK_SECRET` convention.

## Instructions
1. Prove the use case belongs to a data connector and identify the authoritative source system.
2. Re-fetch Lucid webhook/connector docs and the source's official delivery contract; record unknown guarantees.
3. Define event envelope validation, stable IDs, freshness/replay window, deduplication, ordering tolerance, and reconciliation.
4. Make the receiver acknowledge quickly and enqueue bounded work; isolate poison events and apply backpressure.
5. Treat webhook data as a change hint. Fetch/reconcile authoritative state before mutating connector data when the source contract permits.
6. Test valid, invalid-auth, malformed, duplicate, reordered, delayed, missing-record, partial-sync, and replay scenarios with synthetic fixtures.
7. Present registration, endpoint exposure, secrets, expected traffic, data mutations, and disable/rollback plan for approval.
8. After approval, enable a bounded canary and record registration ID, counts, rejects, duplicates, lag, reconciliation, and rollback.

## Approval Boundaries
Do not expose/register endpoints, create secrets, replay production events, mutate connector data, or enable delivery without approval.

## Output
Return contract evidence, architecture, auth method, validation/dedup policy, tests, mutation preview, canary receipt, reconciliation, and rollback.

## Error Handling
| Condition | Response |
|---|---|
| Request is for generic document events | Report that this pack has no verified contract; do not fabricate one. |
| Delivery authenticity is undocumented | Keep the endpoint disabled until the source contract is verified. |
| Duplicate or reordered events diverge state | Pause consumption and reconcile from the authoritative source. |

## Example
```text
surface=data-connector; source=approved-system; fixtures=8/8; duplicates=0; canary=not-approved; generic-document-events=unsupported
```

## Resources
- [Official documentation map](references/official-docs.md)

## Next Steps
Enable only a reversible canary, then compare webhook-assisted state with a full authoritative reconciliation.
