---
name: clari-webhooks-events
description: >-
  Detect Clari changes through supported paginated audit reads and asynchronous activity exports instead of assuming webhooks. Use when building an administrative or sales-activity feed. Trigger with: "monitor Clari changes", "stream Clari audit events", "replace Clari webhooks".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[feed-audit-or-activity-and-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - audit-events
  - activity-export
  - change-detection
compatibility: 'Requires Revenue API access to the chosen audit or activity surface, durable checkpoint or window state, and an approved downstream event sink.'
---

# Clari Audit and Activity Change Feed

## Overview

The published Revenue contract does not define a general webhook subscription surface. Preserve this public route by implementing provider-supported polling: direct paginated audit reads for administrative changes or asynchronous activity exports for emails, meetings, and files.

## Prerequisites

- Chosen feed type, organization scope, and authorized fields
- Monotonic time window or pagination checkpoint with overlap policy
- Deduplication store and downstream event schema

## Instructions

### Step 1: Choose the supported source

Use `GET /audit/events` for paginated audit changes or `POST /export/activity` plus the export-job lifecycle for activity data.

### Step 2: Freeze the window

Record inclusive and exclusive boundaries, page limit, overlap allowance, timezone, and the first checkpoint before requesting data.

### Step 3: Read or queue

Page audit events in stable order, or queue one activity export and persist its job ID before polling.

### Step 4: Normalize event identity

Derive a deterministic key from provider identifiers, event type, actor, timestamp, and source window; retain the source job or page lineage.

### Step 5: Deduplicate and advance

Publish only validated unseen events, then advance the checkpoint atomically after the downstream sink acknowledges the batch.

### Step 6: Detect gaps and replay

Monitor lag, empty windows, page discontinuity, aborted jobs, and reconciliation counts; replay from the last safe checkpoint within retention.

## Authentication

Use the Revenue `apikey` header and an identity authorized for the selected audit or activity data. Do not log actor identities, email content, meeting details, filenames, or the token in event-processing telemetry.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Feed definition and checkpoint policy
- Normalized event batches with provider lineage and deterministic keys
- Lag, gap, deduplication, replay, and checkpoint receipts

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

An audit feed polls with a small overlap, deduplicates by provider event identity, publishes a validated batch, and advances its cursor only after the sink acknowledges it. No unsupported webhook registration is attempted.

## Error Handling

| Failure | Response |
| --- | --- |
| Page or window gap is detected | Stop checkpoint advancement and replay from the last verified boundary. |
| Activity export aborts | Retain the job ID and request fingerprint, diagnose the failure, and avoid blind duplicate submission. |
| Downstream acknowledgement is unknown | Replay the same deterministic batch and let deduplication prevent duplicate effects. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
