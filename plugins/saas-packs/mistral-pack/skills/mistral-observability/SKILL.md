---
name: mistral-observability
description: >-
  Instrument Mistral requests, streams, tools, batch, and workflows without logging sensitive content. Use when building dashboards or SLOs. Trigger with "monitor Mistral", "trace Mistral latency", or "add Mistral alerts".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <slo> <telemetry-backend>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, observability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Content-Free Observability

## Overview

Observe demand, reliability, latency, usage, and state convergence without credentials or content. Keep app telemetry authoritative; evaluate provider Public Preview observability separately.

## Prerequisites

- Defined SLOs, error taxonomy, data classification, and telemetry retention.
- A correlation design using opaque application identifiers.
- Metrics for queue, transport, stream, usage, tools, batch, workflows, and spend.

## Current Contract

Mistral documents Public Preview observability endpoints plus API/admin usage evidence. Preview adoption is optional and requires schema, retention, and availability evaluation.

## Authentication

Never emit authorization, keys, prompts, responses, embeddings, files, tool data, or signed URLs. Restrict admin/preview observability access separately.

## Instructions

1. Define golden signals and state outcomes before fields.
2. Emit endpoint class, opaque model, status/error, attempts, latency segments, usage, and terminal state.
3. Propagate trace context without provider/customer content as identifiers.
4. Dashboard SLOs, throttling, unfinished streams, duplicates, backlog, and spend anomalies.
5. Alert on user impact and actionable budget/state thresholds with owners/runbooks.
6. Evaluate beta observability for data, retention, access, export, failure, and rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Provider observability, trace export, identifier retention, sampling changes, or content-bearing fields require approval. Application-owned content-free telemetry remains the safe default.

## Error Handling

- Logging prompts turns telemetry into an uncontrolled content store.
- `2xx` can hide invalid output or unfinished state.
- High-cardinality customer text exposes data and destabilizes monitoring.

## Output

Return SLOs, telemetry schema and exclusions, dashboards, alerts and owners, preview decision, retention, evidence, and rollback. Identify every signal that remains unavailable.

## Examples

- Measure queue, first event, terminal latency, usage, and validation without response text.
- Alert when workflow state stops converging despite a healthy stream.

## Validation

Inspect telemetry for all paths, scan for secrets and content, and test alert and runbook routing. Confirm cardinality and retention remain within approved bounds.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
