---
name: flyio-rate-limits
description: >-
  Implement Fly.io Machines API pacing, per-resource serialization, retry, and reconciliation from the documented action limits. Use when automating Machine or app operations. Trigger with: "handle Fly 429", "throttle Machines API", "batch Fly Machine updates".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-operation-and-worker-count]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - rate-limits
  - machines-api
  - retries
compatibility: 'Requires a scoped Fly.io API token, an operation and resource inventory, durable job state, and current provider limit documentation.'
---

# Fly.io Machines API Rate Control

## Overview

Replace the old invented per-organization table with Fly.io documented limits: Machine actions are constrained per action and per Machine or app identifier, reads have a separate ceiling, and app deletion has its own minute-level limit. Safe workers serialize conflicting operations and reconcile after ambiguous outcomes.

## Prerequisites

- Exact API operations, app and Machine identifiers, request volume, and completion objective
- Durable operation IDs, desired-state fingerprints, retry counts, and acknowledgement state
- Current rate-limit contract and an error budget for delayed or failed operations

## Instructions

### Step 1: Classify each request

Separate create, update, start, stop, suspend, delete, wait, list, and get operations; identify whether the provider scopes the action to a Machine ID or app ID.

### Step 2: Encode the documented ceilings

For Machine actions, budget one request per second per action and identifier with a short burst up to three. For get-Machine, budget five per second with a burst up to ten. Treat app deletion as at most 100 per minute.

### Step 3: Serialize conflicts

Permit parallel work across independent identifiers only. Never overlap updates, starts, stops, leases, or deletion for the same Machine without a reconciled state boundary.

### Step 4: Make intent replay-safe

Persist desired-state hash, operation, target, current Machine instance version, attempt, and acknowledgement before sending a mutation.

### Step 5: Back off on throttling

Honor provider retry timing when present; otherwise use bounded exponential backoff with jitter. Apply a retry budget and circuit breaker rather than an unbounded loop.

### Step 6: Reconcile ambiguous results

After timeout or transport failure, read current Machine and instance state before retrying. Mark complete only when observed state matches intent.

## Authentication

Send the scoped token as a bearer header only to the documented public or private Machines API base URL. Do not widen token scope to solve throttling, and redact headers and Machine configuration secrets from retry telemetry.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Per-operation and per-identifier rate-control policy
- Durable queue state with attempts, acknowledgements, and reconciliation outcomes
- Throttle, retry, circuit-breaker, and manual-disposition receipt

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A worker updates 200 Machines across several apps. It maintains independent queues by action and Machine ID, caps each update lane to the documented rate, adds jitter, records instance versions, and reads state after a timeout before deciding whether to replay.

## Error Handling

| Failure | Response |
| --- | --- |
| 429 or provider throttle | Pause the matching action and identifier lane, honor retry timing, and reduce concurrency without stalling unrelated resources. |
| 408 or transport timeout | Read current state and instance version before retrying; the mutation may have succeeded. |
| 409 or version conflict | Refresh Machine state, compare desired intent, and enqueue a new reviewed update rather than forcing stale configuration. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Machines resource](https://fly.io/docs/machines/api/machines-resource/)
