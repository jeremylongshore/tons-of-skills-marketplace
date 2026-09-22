---
name: runway-debug-bundle
description: >-
  Assemble a support-ready Runway failure bundle with task, contract, timing, and media metadata while excluding secrets and signed URLs. Use when escalating a reproducible issue. Trigger with: "Runway debug bundle", "collect Runway evidence", "escalate Runway task".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[operation-or-task-id]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - debugging
  - support
  - redaction
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Redacted Runway Generation Debug Bundle

## Overview

A useful bundle proves exactly what contract ran and where it failed without redistributing sensitive prompts, customer media, bearer secrets, or temporary output access. Collect metadata and hashes first, then add narrowly approved samples only when support requires them.

## Prerequisites

- Internal operation ID or provider task ID
- Access to redacted application traces and current contract sources
- An approved destination and retention period for support evidence

## Instructions

### Step 1: Freeze identifiers

Record environment, organization alias, internal operation ID, task ID, endpoint, model or router config ID, API version, SDK name/version, and UTC timestamps.

### Step 2: Capture the request contract

Store a canonical request hash plus field names, lengths, MIME metadata, dimensions, duration, and source checksums. Omit bearer headers, raw customer media, unsafe prompts, and reachable input URLs.

### Step 3: Capture state and timing

Include create response correlation, `PENDING`, `THROTTLED`, `RUNNING`, and terminal transitions as observed; add local queue, upload, poll, download, and storage timings.

### Step 4: Capture the failure plane

For HTTP failure, include status, safe headers, request ID, and redacted error. For task failure, include `failureCode` and sanitized diagnostic. For malformed success, include output count and validation errors, not the signed URLs.

### Step 5: Prove local controls

Attach retry attempt bounds, backoff/jitter settings, timeout, cancellation action, duplicate check, selected model schema fingerprint, and relevant fixture result.

### Step 6: Minimize and share

Review every field, replace values with hashes where possible, encrypt the bundle, set access and expiry, and record the recipient and deletion owner.

## Authentication

Task retrieval uses the server-side Runway secret, but the bundle never contains the secret or an authorization header. Temporary input and output URLs are credentials to media and must be redacted.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Machine-readable redacted manifest and human timeline
- Contract, state, retry, and media-metadata evidence
- Access-controlled support package with retention and deletion owner

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A task returns `INTERNAL.BAD_OUTPUT`. The bundle includes the request hash, model schema fingerprint, input dimensions and checksum, task transitions, failure code, SDK/API versions, and one approved low-sensitivity sample—not the bearer key or signed output URL.

## Error Handling

| Failure | Response |
| --- | --- |
| Task no longer resolves | Use durable local task and trace records, state the evidence gap, and do not fabricate a provider response. |
| Bundle scanner finds a key or signed URL | Quarantine the package, revoke exposed credentials if necessary, redact, and rebuild. |
| Support requests raw customer media | Obtain data-owner approval and a scoped secure transfer or provide a synthetic reproducer. |

## Validation

Run secret and URL scanning, verify hashes against source records, replay the issue with a synthetic fixture where possible, test archive access, and record automatic expiration and deletion.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
