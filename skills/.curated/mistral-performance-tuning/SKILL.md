---
name: mistral-performance-tuning
description: >-
  Analyze and improve Mistral latency and throughput from measured queue, transport, streaming, retrieval, and token evidence. Use when optimizing a slow integration. Trigger with "speed up Mistral", "reduce Mistral latency", or "tune Mistral throughput".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<operation> <latency-slo> <load-profile>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, performance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Performance Tuning

## Overview

Optimize the measured bottleneck rather than changing models or caching content by instinct. Separate queue, connection, first-event, generation, tool, and application time.

## Prerequisites

- A representative synthetic benchmark and explicit quality/safety acceptance.
- Content-free latency, token, queue, retry, and error instrumentation.
- Current workspace limits plus fixed model and request parameters.

## Current Contract

Chat, streaming, embeddings, batch, FIM, OCR, and audio differ in latency and batching. Compare only compatible operations and current account access.

## Authentication

Metrics may include timing, counts, endpoint class, and opaque model ID, but never prompts, outputs, files, credentials, or headers.

## Instructions

1. Define user SLOs and a stable workload covering typical, tail, and cancellation cases.
2. Measure queue, connection, first-event, terminal, parsing, retrieval, tool, and storage durations.
3. Identify the dominant segment and test one reversible hypothesis at a time.
4. Tune bounds, connection reuse, admission, streaming UX, retrieval size, or app concurrency.
5. Compare latency, errors, tokens, quality, safety, and spend using the same workload.
6. Canary the change, monitor regression, and retain prior configuration for rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Live benchmarks, model changes, caching, concurrency, endpoint changes, or relaxed gates require approval. Performance never overrides data policy.

## Error Handling

- Fast first event can hide worse terminal latency.
- Caching user content can violate tenancy and deletion.
- Concurrency can move latency into shared provider queues.

## Output

Return workload hash, before and after segments, confidence, quality, safety and spend deltas, chosen change, canary, and rollback. State whether the SLO actually improved.

## Examples

- Reduce retrieval context only after evaluation preserves quality.
- Reuse connections while retaining cancellation and end-to-end deadlines.

## Validation

Repeat warm and cold trials, vary concurrency, test cancellation and outage, and reject any weakened correctness or isolation. Preserve the exact workload for comparison.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
