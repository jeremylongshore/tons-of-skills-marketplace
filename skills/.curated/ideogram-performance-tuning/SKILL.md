---
name: ideogram-performance-tuning
description: >-
  Optimize Ideogram latency and throughput through route choice, bounded media, concurrency, async handling, and immediate storage. Use when improving an established workload without weakening quality or safety. Trigger with "speed up Ideogram", "profile Ideogram latency", or "optimize Ideogram throughput".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <latency-slo> <quality-floor>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, performance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; paid benchmarks require a bounded test plan"
---
# Ideogram Performance Tuning

## Overview

Improve end-to-end time and useful throughput with measurements, not unsupported rendering flags. Separate queue wait, upload, vendor generation, webhook or polling, download, validation, and storage so optimization preserves safety, quality, cost, and asset durability.

## Prerequisites

- Representative synthetic workload, latency and throughput SLOs, quality floor, and cost ceiling.
- Per-stage metrics, current endpoint mix, output count, media sizes, and concurrency policy.
- Approved benchmark budget, isolated destination, and cleanup owner.

## Current Contract

Ideogram offers synchronous and asynchronous routes plus V4, transparency, P-Image, V3, and outcome-focused tools. Route-specific rendering options differ; V4 `FLASH` currently returns `400`. Default capacity is 10 in-flight requests, and returned asset URLs require prompt download.

## Authentication

Benchmark workers use server-side `IDEOGRAM_API_KEY` through `Api-Key` to `https://api.ideogram.ai`. Metrics label endpoint, status, stage, and content-free workload class, never prompt or image content.

## Instructions

1. Measure queue, upload, generation, reconciliation, download, validation, and storage latency separately at p50, p95, and p99.
2. Confirm the selected endpoint is the narrowest route that meets model, transparency, edit, or tool requirements.
3. Bound input bytes, dimensions, output count, and post-processing; reject work unlikely to meet its deadline.
4. Move long work to async, persist `generation_id`, acknowledge application requests early, and reconcile by webhook plus polling.
5. Tune shared concurrency below observed capacity while tracking `429`, timeout, queue age, and cost per useful output.
6. Compare one change at a time against the quality and safety floor; canary before rollout.
7. Remove benchmark assets and restore the prior setting when any guardrail regresses.

## Tool Discipline

Use Read, Glob, and Grep to inspect metrics, queues, adapters, and fixtures. Use Write and Edit for approved instrumentation or tuning changes. Do not launch a paid benchmark or alter production capacity merely because this skill was selected.

## Approval Boundaries

Require owners for benchmark spend, traffic sampling, model or rendering changes, quality evaluation, concurrency increases, and deployment. Never trade away safety checks or durable persistence for lower apparent latency.

## Error Handling

- Unsupported V4 `FLASH` is a validation defect, not a performance strategy.
- A faster response with an unsafe or unpersisted image is not a successful sample.
- Stop a benchmark on rising errors, queue runaway, budget exhaustion, or storage cleanup failure.

## Output

Return baseline and candidate stage metrics, route and settings, concurrency, useful-output counts, error and safety rates, cost, statistical limitations, canary state, and rollback receipt. Exclude content and credentials.

## Examples

- Move batch generation from synchronous request threads to async submission and webhook reconciliation.
- Reduce oversized uploads before increasing concurrency, then compare p95 end-to-end durable completion.

## Validation

Repeat the benchmark with the same synthetic workload, compare distributions and guardrails, verify account-wide pressure, and test rollback. Confirm all benchmark objects and temporary URLs are removed.

## Resources

- [Current first-party evidence map](references/official-docs.md)
