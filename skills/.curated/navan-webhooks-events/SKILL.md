---
name: navan-webhooks-events
description: >-
  Validate and operate the event or change-delivery mechanism actually enabled for a Navan tenant. Use when evaluating callbacks, API polling, files, or direct integrations. Trigger with "Navan events", "Navan webhook", or "real-time Navan sync".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <delivery-mode> <reconciliation-window>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, events]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Event Delivery Contract Verification

## Overview

Validate and operate the event or change-delivery mechanism actually enabled for a Navan tenant. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Navan's public pages confirm APIs, SFTP, and direct integrations but do not establish a universal webhook endpoint, event taxonomy, or signature header. Use only the tenant's documented delivery mode and keep polling or reconciliation as a recovery path.

## Authentication

For callbacks, use the documented verification scheme and secret lifecycle; for polling or files, use the corresponding read-only identity. Never invent a generic vendor-signature header.

## Instructions

1. Confirm whether the tenant surface supports callback, poll, file, or managed delivery.
2. Capture event or record identifiers, ordering, duplication, correction, and replay semantics.
3. Authenticate before parsing and enforce body or file size limits.
4. Journal receipt before acknowledgement and deduplicate durably.
5. Process idempotently with quarantine for unknown types or schemas.
6. Reconcile periodically against the source-of-record contract.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Registering destinations, issuing verification secrets, enabling new event classes, replaying deliveries, or applying state changes requires explicit approval.

## Error Handling

- A fast acknowledgement must not precede durable receipt.
- Unknown events go to quarantine, not the default handler.
- A delivery gap requires source reconciliation, not blind replay.

## Output

Return delivery-mode evidence, authentication, ordering model, dedupe key, acknowledgement rule, reconciliation cadence, and replay approvals. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Choose polling because no callback contract is enabled.
- Reconcile a managed accounting integration after a delivery gap.

## Validation

Test invalid authentication, duplicate, out-of-order, unknown schema, crash before acknowledgement, replay, and gap recovery. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
