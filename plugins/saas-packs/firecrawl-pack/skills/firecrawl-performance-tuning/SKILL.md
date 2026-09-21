---
name: firecrawl-performance-tuning
description: >-
  Improve Firecrawl latency and throughput through measured scope, formats, cache freshness, async selection, pagination, and concurrency controls. Use when a valid integration is too slow. Trigger with "speed up Firecrawl", "Firecrawl latency", or "optimize crawl performance".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <latency-or-throughput-slo>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, performance, optimization]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Performance Tuning

## Overview

Tune the whole path from submission to accepted downstream record. Preserve freshness, completeness, target policy, and cost while changing one control at a time.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Firecrawl v2 cache behavior is controlled by maxAge/minAge and related options; current defaults and effects belong to the scrape documentation. Crawl and batch provide waiter and asynchronous paths, pagination can dominate retrieval time, and queue wait consumes request timeout. maxConcurrency affects page processing but remains bounded by team capacity.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Define an SLO and baseline for submission, queue, processing, pagination, validation, storage, freshness, accepted-result rate, and credits.
2. Segment by operation, target class, format, cache state, origin status, content size, and async job size without putting raw URLs or content in metrics.
3. Remove unnecessary formats, actions, waits, screenshots, raw HTML, JSON extraction, and over-broad crawl scope before adding concurrency.
4. Set maxAge or cache-only behavior only when the freshness SLA permits it. Verify cacheState and quality rather than assuming a cache hit is acceptable.
5. Use batch for known URL sets, async submission for long work, and complete pagination efficiently. Bound maxConcurrency below observed team capacity.
6. Tune one factor per canary, compare tail latency and accepted-output quality, and watch rate, concurrency, queue, origin, and credit effects.
7. Promote only improvements that meet all guardrails; retain baseline, candidate, and rollback evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before reducing freshness, enabling storage/cache on sensitive sources, increasing concurrency or scope, changing formats, or accepting lower completeness.

## Output

Return the baseline, bottleneck attribution, controlled experiment, configuration delta, latency/throughput/quality/cost results, queue effects, chosen setting, and rollback threshold.

## Error Handling

- Faster result has stale or incomplete content: reject the optimization.
- Queue time dominates: reduce producers or change scheduling before increasing timeouts.
- Metrics mix transport and accepted-content success: repair measurement before tuning.

## Examples

- "Scrapes take ten seconds" separates origin/rendering, cache, queue, and downstream time.
- "Increase all concurrency" is replaced with a stepped canary inside team and target limits.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
