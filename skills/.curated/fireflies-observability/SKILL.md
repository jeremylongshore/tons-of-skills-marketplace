---
name: fireflies-observability
description: >-
  Instrument Fireflies GraphQL and webhook workflows with operation, latency, quota, queue, signature, and processing metrics that exclude meeting content and identities. Use when building dashboards or alerts. Trigger with "monitor Fireflies", "Fireflies metrics", or "Fireflies webhook alerts".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, observability, privacy]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Content-Free Observability

## Overview

Instrument Fireflies GraphQL and webhook workflows with operation, latency, quota, queue, signature, and processing metrics that exclude meeting content and identities.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Observability may include operation name, result class, GraphQL code, duration, response size bucket, retryAfter, event type, signature result, queue depth, and processing latency. It must exclude Authorization, queries with variables, meeting IDs, emails, titles, sentences, summaries, and media URLs.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Define service-level indicators for GraphQL success, webhook acknowledgement, queue processing, and freshness.
2. Instrument safe dimensions with a strict allowlist and cardinality budget.
3. Track plan and operation-specific throttles separately.
4. Measure transcribed-to-summarized and event-to-processing latency without meeting IDs in metrics.
5. Alert on auth failures, signature failures, throttle spikes, backlog, dead letters, and stale processing.
6. Keep detailed identifiers only in access-controlled audit records when approved.
7. Test telemetry redaction with synthetic secrets and meeting data.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before logging identifiers or response fragments, increasing telemetry retention, or exporting observability data to a new vendor.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- High-cardinality label detected: remove it before deployment.
- Sensitive value appears in telemetry: stop export and follow incident handling.
- Metrics disagree with audit receipts: investigate instrumentation before changing workload behavior.

## Examples

- "Review fireflies content-free observability" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
