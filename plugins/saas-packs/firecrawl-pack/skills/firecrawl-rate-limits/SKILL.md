---
name: firecrawl-rate-limits
description: >-
  Implement bounded Firecrawl throttling and retry behavior using current team RPM, browser concurrency, queue status, timeouts, and Retry-After. Use when handling 429s or producer backpressure. Trigger with "Firecrawl rate limits", "Firecrawl throttling", or "Firecrawl queue".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <operation>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, rate-limits, reliability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Rate, Concurrency, and Queue Control

## Overview

Control request production and page-processing concurrency as different resources. Derive limits from the current team plan and live queue evidence, not copied constants.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Firecrawl documents per-team request-per-minute limits and concurrent browser limits. All keys on one team share rate counters. Work beyond browser capacity can queue, queue wait counts toward timeout, and excessive queued jobs can return 429. The error catalog says to honor Retry-After when present; batch shares crawl limits.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Read the current rate-limit documentation and team configuration for the exact operation; record the evidence timestamp without embedding plan numbers in code.
2. Model submission RPM, in-flight browser work, Firecrawl queue, application backlog, target-origin limits, and credit ceiling separately.
3. Use a bounded token bucket or equivalent for submissions and a bounded worker pool for jobs. Keep crawl/batch maxConcurrency within the approved envelope.
4. On 429, inspect error classification and Retry-After. Pause the relevant producer, add jitter, cap attempts and total wait, and preserve idempotency.
5. Poll Queue Status at a modest cadence, apply backpressure before timeout risk rises, and shed or defer low-priority work using an owned policy.
6. Test rate 429, concurrency 429, long queue, missing/invalid Retry-After, cancellation, and recovery with synthetic responses.
7. Tune from observed throughput with safety headroom; emit queue, throttle, retry, drop/defer, latency, and cost receipts.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before raising producer or page concurrency, extending total retry time, increasing plan capacity, bypassing backpressure, or prioritizing one workload over another.

## Output

Return current limit sources, control design, operation budgets, Retry-After behavior, queue/backpressure policy, synthetic test results, safe envelope, alerts, and escalation path.

## Error Handling

- Limit source is stale or unknown: begin conservatively and require verification.
- Retry-After exceeds the job deadline: defer or fail rather than sleeping past the SLO.
- Team queue remains saturated: stop producers and escalate capacity or scheduling; do not rotate keys to evade shared limits.

## Examples

- "Fix Firecrawl 429s" distinguishes RPM, concurrency, and queue exhaustion first.
- "Use another key for more RPM" is rejected because team keys share counters.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
