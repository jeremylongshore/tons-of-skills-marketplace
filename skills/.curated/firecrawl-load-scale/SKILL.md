---
name: firecrawl-load-scale
description: >-
  Measure Firecrawl throughput under plan, team rate, browser concurrency, queue, timeout, target-policy, and credit constraints. Use when planning or validating scale. Trigger with "load test Firecrawl", "Firecrawl concurrency", or "scale Firecrawl".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <load-profile>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, performance, capacity]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Capacity and Load Validation

## Overview

Find the safe operating envelope with synthetic or explicitly authorized targets. A load test must not become an uncontrolled scrape campaign or consume unapproved credits.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Firecrawl separates per-team requests-per-minute limits from concurrent browser capacity. Work beyond browser capacity can queue, queue time counts against request timeout, and queue status exposes availability. Crawl and batch calls also accept maxConcurrency, while a crawl delay forces concurrency to one.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Define the approved target set, environment, maximum requests/pages/credits, concurrency steps, duration, stop thresholds, and owner. Prefer a controlled synthetic origin.
2. Measure a single-worker baseline for submission latency, completion latency, throughput, queue time, error classes, origin status, output size, quality, and credit usage.
3. Increase producer concurrency in small steps below the current plan/team limits. Observe Firecrawl queue status and the application's own backlog separately.
4. For crawl or batch, test maxConcurrency and explicit limits; do not assume client request concurrency equals page-processing concurrency.
5. Exercise 429 rate pressure, concurrency queuing, Retry-After handling, timeout, cancellation, partial pagination, and backpressure using synthetic responses before live load.
6. Stop on error, spend, target-load, latency, queue-age, or quality thresholds. Drain or cancel work according to the test plan.
7. Report the sustainable envelope with headroom, bottleneck evidence, configuration, cost, and rollback; never publish captured bodies.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before live load, increasing credits or plan capacity, using third-party targets, changing target delay/concurrency, or extending the test window.

## Output

Return the load profile, target authorization, baseline and stepped metrics, queue behavior, throttle/error counts, credits, sustainable envelope, stop event, cleanup, and capacity recommendation.

## Error Handling

- Queue grows without stable throughput: stop producers and drain before testing another step.
- Target-origin failures rise: treat target protection as a stop condition, not a reason to add proxies.
- Credit telemetry is delayed: hold the next step until async usage settles.

## Examples

- "Can we run 100 workers?" derives the answer from current team limits and a stepped test.
- "Stress a competitor's site" is refused because target authorization is absent.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
