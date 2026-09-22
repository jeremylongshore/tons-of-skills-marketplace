---
name: vastai-sdk-patterns
description: >-
  Choose the correct Vast.ai Python client and implement typed, bounded, ownership-safe GPU lifecycles. Use when integrating the high-level SDK, SyncClient, AsyncClient, or Serverless client. Trigger with: "use the Vast.ai SDK", "wrap a Vast.ai instance lifecycle", "choose SyncClient or AsyncClient".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[client-mode-resource-and-lifecycle-owner]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - python
  - sdk
  - lifecycle
compatibility: 'Requires Python 3.9+, the current Vast.ai package, a scoped API key, and tests that can replace network calls.'
---

# Owned Vast.ai Python SDK Lifecycles

## Overview

Use the highest-level client that preserves the required control. Keep resource identity and cleanup ownership explicit, normalize provider response variants at one boundary, and never hide a billable instance behind an unbounded retry.

## Prerequisites

- Chosen high-level, synchronous, asynchronous, or Serverless client surface
- Typed internal model for offers, instances, terminal states, and provider errors
- Idempotency, timeout, test-double, and cleanup design

## Instructions

### Step 1: Select one client boundary

Use `VastAI` for broad CLI-equivalent operations, `SyncClient` for typed synchronous instance control, `AsyncClient` inside an async context, or `Serverless` for endpoint inference.

### Step 2: Normalize responses once

Map provider dictionaries and error shapes into a small internal result type. Preserve offer ID, contract ID, status, price, and raw error code for diagnosis.

### Step 3: Separate plan from mutation

Search and score offers without creating resources. Require an approved plan object before calling create, update, destroy, or credit operations.

### Step 4: Own the lifecycle

Persist the returned instance ID immediately, apply a monotonic deadline, classify terminal failure states, and place destroy or handoff in an explicit finalizer.

### Step 5: Test failure boundaries

Cover 401, 403, 429, malformed responses, create-without-ID, readiness timeout, and cleanup failure using local fakes.

### Step 6: Expose a redacted receipt

Return normalized decisions and state transitions; never return the API key or full environment.

## Authentication

Construct clients from `VAST_API_KEY` or the approved local configuration. Do not pass keys as literals, serialize client objects, or let provider credentials cross into workload payloads.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Client-selection decision and typed adapter contract
- Bounded lifecycle implementation with local failure tests
- Redacted mutation and cleanup receipt

Return client type, package version, plan identity, provider resource IDs, terminal outcome, and cleanup owner.

## Examples

An async job runner uses `AsyncClient` as a context manager, records `instance.id` before waiting, cancels on its deadline, and destroys the instance in a tested finalizer.

## Error Handling

| Failure | Response |
| --- | --- |
| Create succeeds without a usable ID | Stop follow-on work, reconcile instances from the account, and avoid a blind second create. |
| Response shape changes | Fail at the adapter boundary and retain the redacted raw response for review. |
| 429 occurs | Use bounded client retry and reduce polling; do not multiply retries at every layer. |
| Finalizer cannot destroy | Persist the resource ID and page the billing owner. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Official SDK skill](https://github.com/vast-ai/vast-cli/blob/master/vastai_sdk/SKILL.md)
- [Python SDK reference](https://docs.vast.ai/sdk/python)
- [API rate limits and errors](https://docs.vast.ai/api-reference/rate-limits-and-errors)
