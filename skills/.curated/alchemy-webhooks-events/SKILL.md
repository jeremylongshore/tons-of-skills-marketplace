---
name: alchemy-webhooks-events
description: >-
  Operate Alchemy Notify webhooks with raw-body HMAC verification, idempotent intake, durable processing, and safe lifecycle changes. Use when implementing or repairing blockchain event delivery. Trigger with "Alchemy webhook", "Alchemy Notify", or "verify X-Alchemy-Signature".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<webhook-type> <network> <callback>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, webhooks, events]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Notify Webhook Operations

## Overview

Operate Alchemy Notify webhooks with raw-body HMAC verification, idempotent intake, durable processing, and safe lifecycle changes. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

Alchemy signs the exact raw request body with HMAC-SHA256 using the webhook's signing key and sends the digest in `X-Alchemy-Signature`. Notify management uses its documented auth token, not the signing key. Current docs describe automatic retries/backoff and ordered first-time delivery; consumers still need idempotency because duplicate processing and application retries remain possible.

## Authentication

Keep the per-webhook signing key and Notify management token in separate managed secrets. The receiver may read the signing key only for verification; it may not create, update, or delete webhook registrations.

## Instructions

1. Select the current webhook type and network from first-party support, define event semantics, confirmation policy, callback SLO, and data retention.
2. Create or modify the registration only through an approved management path; record webhook ID, redacted filter, owner, signing-key version, and rollback configuration.
3. Capture the raw request bytes before JSON parsing, compute HMAC-SHA256, and compare decoded equal-length values with a timing-safe function.
4. Persist the webhook and event identifiers atomically before acknowledging; enqueue work and return success without blocking on downstream side effects.
5. Make consumers idempotent, preserve per-entity ordering where required, and define reorganization, mined, dropped, and duplicate-event behavior.
6. Test valid, invalid, replayed, delayed, out-of-order, and downstream-failure cases; operate a bounded dead-letter replay with explicit approval.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

The product owner approves event scope and user impact. Security approves callback exposure and secret storage. Creating, changing, deleting, replaying, or rotating a production webhook requires explicit owner approval.

## Error Handling

- Reject a missing, malformed, or mismatched signature before parsing or side effects.
- Do not use the Notify management token as the HMAC signing key.
- A duplicate-safe acknowledgement is preferable to repeating a user-visible side effect.

## Output

Return the event contract, registration receipt, raw-body verifier, idempotency key and storage design, acknowledgement SLO, ordering/reorg policy, replay runbook, tests, and rollback. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Accept one synthetic signed Address Activity event, then acknowledge its exact duplicate without repeating a notification.
- Quarantine a valid event when downstream processing fails and replay it only after the fault and approval boundary are resolved.

## Validation

Exercise and record expected and observed results for:

- valid signature
- wrong signing key
- body changed after signing
- duplicate event
- out-of-order event
- downstream failure and replay

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
