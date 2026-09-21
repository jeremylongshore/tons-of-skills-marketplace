---
name: navan-common-errors
description: >-
  Triage Navan integration failures without exposing travel or payment data or applying blind retries. Use when a contracted API, SFTP, SCIM, or direct integration fails. Trigger with "Navan error", "Navan sync failed", or "debug Navan integration".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <failure-time> <correlation-id>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, troubleshooting]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Contract Failure Triage

## Overview

Triage Navan integration failures without exposing travel or payment data or applying blind retries. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Classify failures by layer: local configuration, identity, tenant enablement, contract/schema, transport, vendor availability, destination, or reconciliation. Status codes alone do not establish safe retry behavior.

## Authentication

Never ask for or reproduce credentials. Confirm only secret presence, source, age, scope label, target host, and last rotation using content-free evidence.

## Instructions

1. Freeze retries and preserve the first sanitized failure receipt.
2. Identify tenant, environment, surface, operation, and contract revision.
3. Check configuration and identity metadata without printing values.
4. Compare request and response envelopes against fixtures using redacted structure only.
5. Check Navan status and destination health before attributing cause.
6. Select retry, reconcile, credential rotation, contract update, or escalation with an owner.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Replays, secret rotation, backfills, file retransmission, traveler-data inspection, and write retries require explicit approval and an impact bound.

## Error Handling

- Do not retry a possibly accepted write without idempotency evidence.
- HTML or a login page means wrong contract or authentication path.
- Redact names, emails, itineraries, payment data, receipts, and tokens from support bundles.

## Output

Return failure layer, evidence timeline, affected window, retry safety, data exposure check, owner, and next action. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Distinguish expired transfer credentials from a changed file schema.
- Pause a destination load after a Navan read succeeded but acknowledgement failed.

## Validation

Reproduce only with approved synthetic data and prove both safe-retry and unknown-outcome paths. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
