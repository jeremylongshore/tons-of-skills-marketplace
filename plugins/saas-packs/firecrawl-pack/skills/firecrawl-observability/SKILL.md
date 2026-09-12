---
name: firecrawl-observability
description: >-
  Instrument Firecrawl v2 requests, async jobs, queue pressure, credits, origin status, webhooks, output quality, and downstream delivery without logging content. Use when building monitoring or SLOs. Trigger with "monitor Firecrawl", "Firecrawl metrics", or "Firecrawl dashboard".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <service-or-slo>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, observability, sre]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Operational Observability

## Overview

Measure the service as a pipeline: submission, Firecrawl processing, origin result, pagination, validation, storage, and freshness. Transport success alone does not prove usable content.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Use Credit Usage endpoints and dashboard activity for spend, Queue Status for capacity, job/status APIs for async progress, webhookId for delivery identity, metadata.statusCode for origin response, and creditsUsed where returned. Metric labels must not contain raw URLs, page content, prompts, keys, or unbounded IDs.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Define SLIs and SLOs for accepted-result success, end-to-end latency, freshness, queue age, pagination completeness, origin-status distribution, output quality, webhook recovery, and spend.
2. Instrument each stage with low-cardinality operation, environment, source-class, terminal-state, retry-class, and policy-version labels.
3. Record opaque request/job/webhook IDs only in access-controlled traces. Hash or classify URLs and exclude custom headers, bodies, extracted values, screenshots, and secrets.
4. Poll or stream async state within bounds, count every result page, and reconcile submitted, processed, accepted, rejected, stored, and deleted totals.
5. Collect queue and credit evidence at a cadence that respects API limits. Account for delayed asynchronous billing before alerting on unexplained deltas.
6. Alert on user-impacting SLO burn, sustained queue pressure, 402/403/429 shifts, origin errors, webhook retry exhaustion, schema rejection, and freshness lag.
7. Run synthetic failure and recovery tests, verify dashboards against raw aggregate counts, and document alert ownership and runbook links.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before adding high-cardinality labels, retaining target identifiers, exporting telemetry to a new provider, or enabling synthetic network calls.

## Output

Return the SLI/SLO definitions, event and metric schema, redaction/cardinality rules, dashboard and alert design, reconciliation checks, test results, and runbook ownership.

## Error Handling

- Metrics disagree with job totals: stop reporting completeness until pagination and terminal states reconcile.
- An alert includes content or a credential: remove it and treat the exposure according to policy.
- Credit data is delayed: use a settlement window and corroborate with completed-page counts.

## Examples

- "Alert on bad Firecrawl output" combines origin status and content-quality gates, not HTTP success alone.
- "Label metrics with full URL" is replaced with an approved source class or controlled hash.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
