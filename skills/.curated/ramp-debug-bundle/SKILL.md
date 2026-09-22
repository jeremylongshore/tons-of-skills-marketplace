---
name: ramp-debug-bundle
description: >-
  Collect a minimal, safe Ramp API diagnostic bundle centered on trace IDs and reproducible contract evidence. Use when escalating a persistent API, webhook, deferred-task, or accounting failure. Trigger with "Ramp debug bundle" or "Ramp support evidence".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, debugging, support, evidence]
---
# Sanitized Ramp Support Bundle

## Overview

Create an evidence package that Ramp support and internal responders can use without exposing credentials, card details, receipts, or unnecessary employee and financial data.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp responses include `x-trace-id`, the preferred correlation handle for developer support.
- API error bodies may include `error_v2.error_code`, additional information, and a message.
- Webhook and deferred-task incidents need delivery/task identifiers and lifecycle state, not copied secrets or full payloads.
- Authorization failures require environment, grant, and scope metadata, but never the bearer token or client secret.

## Instructions

1. Open a restricted case directory and record incident window, environment, affected endpoint or event, expected behavior, owner, and data-handling classification.

2. Capture UTC timestamps, method, sanitized path template, status, `x-trace-id`, error code, attempt count, latency, idempotency key hash, and application release.

3. Add a minimized schema-valid reproducer using placeholders and sandbox IDs; record grant type and scope names without credential values.

4. For webhooks or deferred tasks, include subscription/event/task identifiers, deduplication outcome, state transitions, and sanitized response metadata.

5. Run a secret/card/identity scan, obtain the data owner's sharing approval, generate checksums, and transmit only through the approved support channel.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

The incident owner approves scope; security/data owners approve external sharing. Never upload raw production bodies, receipts, PAN/CVV, tokens, or client secrets.

## Output

A checksummed sanitized bundle, field manifest, reproduction steps, trace IDs, environment and release metadata, redaction scan, sharing approval, and retention deadline.

## Error Handling

| Condition | Response |
|---|---|
| No trace ID was retained | Reproduce the smallest safe request in sandbox or an approved read-only path and capture the new trace. |
| Redaction destroys reproducibility | Replace values with type-preserving placeholders and keep restricted originals outside the shared bundle. |
| A support request asks for secrets | Refuse and use an approved credential-verification or secure escalation process. |

## Examples

### Example 1

Bundle a recurring 422 with one sanitized request fixture, `error_v2` code, trace ID, schema version, and exact release.

### Example 2

Document a webhook gap using event IDs, receive timestamps, dedupe decisions, and a reconciled object count without event bodies.

## Validation

- The bundle reproduces or precisely bounds the failure.
- Trace IDs and identifiers are preserved while secret and sensitive value scans are clean.
- Every included field has an explicit diagnostic purpose.
- Sharing channel, approver, checksum, and deletion date are recorded.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
