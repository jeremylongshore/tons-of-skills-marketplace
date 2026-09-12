---
name: ideogram-observability
description: >-
  Instrument Ideogram request, queue, async, safety, storage, latency, and spend signals without logging image content. Use when building dashboards, alerts, or SLO evidence. Trigger with "monitor Ideogram", "add Ideogram metrics", or "audit Ideogram telemetry".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <slo> <environment>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, observability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; telemetry must remain content-free"
---
# Ideogram Observability

## Overview

Measure whether accepted image work becomes a safe durable asset within its deadline and budget. Join application request, queue, vendor, webhook or polling, download, storage, and publication stages using opaque identifiers rather than prompts or media.

## Prerequisites

- Service boundaries, SLO, error budget, budget window, owners, and incident thresholds.
- A data dictionary and cardinality policy for metrics, logs, and traces.
- Known endpoint, queue, async state, safety, storage, and cleanup transitions.

## Current Contract

Useful vendor-facing signals include endpoint family, HTTP status, `generation_id`, async state, `is_image_safe`, URL-present boolean, and timing. Default capacity is 10 in-flight requests, while actual account behavior and current pricing must be observed at decision time.

## Authentication

Telemetry must record only that server-side `Api-Key` authentication was configured or rejected. Never capture the header value, prompts, structured prompts, source images, output images, signed URLs, or raw payload bodies.

## Instructions

1. Define the user outcome as a safe approved asset durably stored by its deadline, not merely HTTP `200`.
2. Instrument admission, queue wait and age, in-flight count, upload, generation, webhook, polling, download, validation, storage, review, and cleanup stages.
3. Count statuses by endpoint and environment; separate auth, validation, throttling, capacity, safety, expiry, and storage failures.
4. Track accepted async generations to one terminal state and alert on stuck, duplicate, missing-webhook, or unreconciled records.
5. Attribute estimated or reconciled spend to useful, unsafe, failed, abandoned, and unstored outcomes.
6. Build SLO dashboards and actionable alerts with owners, runbook links, burn windows, and content-free exemplars.
7. Test alert delivery and verify telemetry deletion and access controls.

## Tool Discipline

Use Read, Glob, and Grep to inspect instrumentation, dashboards, and logs. Use Write and Edit for approved telemetry or runbook changes. Do not query raw customer content, enable body capture, or change production sampling without authority.

## Approval Boundaries

Require review for new labels, retained opaque IDs, cross-tenant joins, sampling, external telemetry export, SLO changes, and production deployment. High-cardinality content fields are prohibited by default.

## Error Handling

- Alert on rising `429` before retry traffic amplifies it.
- Distinguish unsafe output from transport failure and expired URL from generation failure.
- Treat missing durable-storage confirmation as incomplete even when the vendor stage succeeded.

## Output

Return metric and trace schema, dashboards, alerts, SLO calculation, label-cardinality review, sensitive-field scan, owners, test results, deployment state, and rollback. Exclude content and credentials.

## Examples

- Chart end-to-end durable completion p95 beside vendor generation p95 to expose queue and storage delay.
- Report outcomes as `safe_stored`, `unsafe`, `vendor_failed`, `expired_before_download`, and `storage_failed`.

## Validation

Inject each failure class, verify one terminal outcome per request, inspect sample telemetry for content leakage, and fire alerts through the on-call path. Confirm dashboards survive rollback.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
