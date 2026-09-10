---
name: algolia-performance-tuning
description: >-
  Analyze and optimize an Algolia search path using repository and production evidence instead of universal latency targets. Use when search feels slow, payloads are large, or rendering regresses. Trigger with "tune Algolia performance", "slow Algolia search", or "search latency".
argument-hint: "[repository-path] [journey-or-query-set]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- performance
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Evidence-Based Performance Tuning

## Overview

This skill decomposes perceived search time into input handling, network, provider request, response transfer, transformation, and render work. Optimization starts with an owned baseline and ends with a comparable measurement.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Set targets from the application's SLO, user geography, device mix, and measured baseline.
- Inspect record and response shape before changing relevance or faceting settings.
- Separate query count amplification from individual request latency.
- Preserve correctness and relevance assertions alongside performance measurements.

## Authentication

Run measurements with search-only or secured keys and sanitized representative queries. Do not expose write credentials or sensitive query logs.

## Instructions

1. Define the journey, environment, representative query set, device/network profile, and success criteria.
2. Capture request count, component timings, payload size, cache behavior, result correctness, and render cost.
3. Locate the dominant segment before proposing changes.
4. Test bounded changes such as debouncing, stalled-search handling, requested attributes, query batching, or render work.
5. Compare before and after with the same harness and inspect relevance and freshness regressions.
6. Document the accepted change, uncertainty, monitoring signal, and rollback trigger.

## Approval Boundaries

Do not change ranking, remove required facets, cache personalized responses, or publish claimed improvements without comparable evidence.

## Output

Return the benchmark protocol, baseline distribution, bottleneck attribution, tested changes, before/after evidence, relevance checks, and rollout guardrails.

## Error Handling

| Condition | Response |
|---|---|
| Results are noisy | Increase samples and control geography, device, cache, and query set. |
| Faster response changes hits | Reject or obtain product acceptance for the relevance tradeoff. |
| Client emits duplicate requests | Fix lifecycle or input handling before provider tuning. |
| No SLO exists | Report the baseline without inventing a target. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
journey=mobile-typeahead; queries=approved-100; network=recorded-profile
```

Expected handoff:

```text
dominant=duplicate-client-requests; requests-keystroke=3-to-1; relevance=unchanged
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Search performance](https://www.algolia.com/doc/guides/building-search-ui/going-further/improve-performance/js)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
- [Monitoring API](https://www.algolia.com/doc/rest-api/monitoring)
