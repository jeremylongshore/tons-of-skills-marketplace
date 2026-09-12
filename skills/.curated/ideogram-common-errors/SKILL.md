---
name: ideogram-common-errors
description: >-
  Diagnose Ideogram authentication, validation, throttling, capacity, safety, and asset-expiry failures by evidence class. Use when a request fails or returns no usable image. Trigger with "debug Ideogram 422", "fix Ideogram 429", or "diagnose an empty Ideogram URL".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<status-or-symptom> <endpoint> <environment>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, troubleshooting]
model: inherit
effort: high
compatibility: "Designed for Claude Code; diagnosis defaults to sanitized offline evidence"
---
# Ideogram Error Diagnosis

## Overview

Classify an Ideogram failure before changing code or retrying spend. Separate authentication, billing readiness, request validation, throttling, service capacity, safety policy, asynchronous lifecycle, download expiry, and application storage failures.

## Prerequisites

- Endpoint, method, environment, timestamp, sanitized status, and opaque request or generation identifier.
- The exact adapter version and current endpoint documentation.
- Access to content-free logs, fixtures, queue state, and storage receipts.

## Current Contract

Endpoint docs surface `400`, `401`, `422`, and `429`; operational paths can also encounter transient service failures such as `503`. V4 `FLASH` currently produces `400`. Unsafe generation may complete with `is_image_safe=false` and an empty URL. Async work must reach a recognized terminal state.

## Authentication

Verify only that a server-side `Api-Key` header is configured for `https://api.ideogram.ai`; never paste or print its value. A key, team balance, and application user authorization are separate checks.

## Instructions

1. Capture the endpoint, status, latency, attempt count, content type, sanitized error code, and opaque identifiers.
2. Reproduce against a fixture before considering another paid live call.
3. Map `401` to key presence, header name, environment, and revocation; map `400` or `422` to endpoint-specific fields and media validation.
4. Map `429` to local in-flight concurrency, queue deadline, and server retry guidance; map `503` or transport failure to bounded transient handling.
5. Inspect `is_image_safe`, URL presence, async terminal state, download timing, and durable-storage result separately.
6. Apply one minimal correction, rerun the deterministic test, and use one approved synthetic live probe only if needed.
7. Record cause, evidence, spend, affected scope, correction, and rollback.

## Tool Discipline

Use Read, Glob, and Grep for adapters, schemas, logs, and fixtures. Use Write and Edit only for an approved minimal fix or test. Do not rotate keys, add credit, replay production requests, alter prompts, or relax safety automatically.

## Approval Boundaries

Require ownership before a paid reproduction, credential rotation, balance change, concurrency increase, policy change, customer-content access, or production deploy. Preserve the failed state until enough sanitized evidence exists.

## Error Handling

- Never retry `400`, `401`, or `422` without a verified correction.
- Retry transient capacity failures only within attempt, jitter, and total-deadline bounds.
- An expired URL is a persistence failure; regenerating is a new paid and policy-governed operation.

## Output

Return symptom class, endpoint, sanitized status, evidence IDs, affected scope, leading cause, ruled-out causes, correction, tests, spend impact, and rollback status. Exclude credentials, prompts, images, raw vendor bodies, and URLs.

## Examples

- Diagnose `400` by finding V4 `rendering_speed=FLASH`, then reject the option locally.
- Diagnose a `200` with no URL by checking `is_image_safe` before blaming storage or networking.

## Validation

Reproduce the original class deterministically, prove the corrected branch, test neighboring failure classes, and verify logs remain content-free. Confirm no queued retry or temporary asset remains after diagnosis.

## Resources

- [Current first-party evidence map](references/official-docs.md)
