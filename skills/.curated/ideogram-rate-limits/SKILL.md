---
name: ideogram-rate-limits
description: >-
  Control Ideogram concurrency with a bounded queue, deadlines, backoff, and fair tenant admission. Use when preventing 429 responses or sizing generation workers. Trigger with "tune Ideogram concurrency", "fix Ideogram throttling", or "design an Ideogram request queue".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<traffic-shape> <latency-slo> <tenant-policy>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, reliability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live capacity tests require explicit spend and load approval"
---
# Ideogram Concurrency and Queue Control

## Overview

Keep paid image work inside a measurable concurrency envelope. Combine admission control, tenant fairness, operation deadlines, and endpoint-aware retry so a traffic burst does not become duplicate spend, an unbounded queue, or persistent `429` pressure.

## Prerequisites

- Request arrival rate, latency objective, output count, endpoint mix, and cost ceiling.
- Queue ownership, per-tenant policy, cancellation behavior, and overload response.
- Current account capacity and an approved contact path for increased scale.

## Current Contract

Ideogram's API overview documents a default limit of 10 in-flight requests and directs larger-capacity needs to `partnership@ideogram.ai`. This is a concurrency boundary, not permission to launch ten workers per process. Account-wide observed behavior remains authoritative.

## Authentication

Workers inject `IDEOGRAM_API_KEY` server-side and send `Api-Key` only to `https://api.ideogram.ai`. Queue records and metrics must exclude keys, prompts, images, and response URLs.

## Instructions

1. Measure arrival rate, service time by endpoint, current in-flight count, queue age, timeout rate, and `429` responses.
2. Place a shared account-level semaphore below the verified limit; start conservatively and reserve capacity for recovery probes.
3. Add bounded per-tenant admission, queue length, age, output count, and total operation deadlines.
4. Prefer asynchronous endpoints for work that cannot fit an interactive deadline and persist each `generation_id`.
5. Retry only classified transient responses using server guidance when present, exponential backoff with jitter, and a strict attempt ceiling.
6. Prevent ambiguous duplicate generation by reconciling known async identifiers before resubmission.
7. Raise capacity only through the vendor path and a reviewed load plan; canary the new limit.

## Tool Discipline

Use Read, Glob, and Grep for queue, worker, metric, and fixture inspection. Use Write and Edit for approved limit, test, or documentation changes. Invocation does not authorize load generation, quota negotiation, or increased production concurrency.

## Approval Boundaries

Require owners for live load tests, spend, tenant-priority changes, queue dropping, capacity increases, and deployment. Document how queued work is cancelled or drained before changing the envelope.

## Error Handling

- A `429` is an admission-control signal; immediate retries amplify pressure.
- Expired queue work should terminate before calling Ideogram, not after spending credit.
- Do not retry `400`, `401`, `422`, unsafe output, or an already accepted async submission as if transient.

## Output

Return verified limit source, chosen semaphore, queue and tenant bounds, deadline and retry policy, measured status counts, cost impact, test result, canary state, and rollback setting. Exclude content and credentials.

## Examples

- Set eight shared worker permits, retain two for recovery probes, and cap each tenant below the account total.
- Report `peak_inflight=8; queue_p95=3s; 429=0; expired_before_submit=12; duplicates=0`.

## Validation

Use a deterministic queue simulator first, verify fairness and deadline expiration, inject `429` and timeout outcomes, and prove duplicate suppression. Run a paid load check only within the approved request and cost ceiling.

## Resources

- [Current first-party evidence map](references/official-docs.md)
