---
name: algolia-observability
description: >-
  Instrument an Algolia integration for actionable availability, latency, freshness, relevance, and event-health signals. Use when defining dashboards, alerts, traces, or service objectives. Trigger with "monitor Algolia", "Algolia metrics", or "search observability".
argument-hint: "[repository-path] [service-or-journey]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- observability
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Search Observability

## Overview

This skill instruments the application-owned search journey rather than substituting generic provider claims. It connects client outcomes, request IDs, index publication, source freshness, and product-level relevance indicators.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Derive thresholds and objectives from the product SLO and measured baseline; do not use universal latency numbers.
- Separate application latency from Algolia request latency and rendering time.
- Track source snapshot to completed indexing task to searchable sentinel for freshness.
- Treat event delivery and query-ID coverage as their own health surface.

## Authentication

Telemetry must exclude API keys, raw personal data, sensitive queries, and unrestricted record payloads. Use approved read-only monitoring access where provider data is needed.

## Instructions

1. Define the user journey, owned SLOs, current baseline, and incident-routing owner.
2. Instrument operation, outcome, duration, index alias, environment, SDK version, request ID, and bounded retry count.
3. Add freshness markers linking source snapshot, task completion, and searchable sentinel.
4. Measure no-result and event coverage using privacy-reviewed aggregation.
5. Build dashboards and alerts from sustained error-budget or baseline deviation, not a copied threshold.
6. Test telemetry during success, denial, timeout, stale-index, and event-failure scenarios.

## Approval Boundaries

Do not log secrets or raw sensitive queries, create arbitrary alert thresholds, or enable high-cardinality labels without review.

## Output

Return the signal catalog, field and redaction schema, SLO mapping, dashboards, alerts, synthetic checks, test evidence, and known blind spots.

## Error Handling

| Condition | Response |
|---|---|
| Request ID unavailable | Preserve local trace correlation and full redacted error metadata. |
| High cardinality detected | Aggregate or hash approved identifiers. |
| Provider and app latency differ | Split the spans and investigate the dominant segment. |
| No product SLO exists | Report measurements and request an owner decision. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
journey=product-search; slo=company-owned; fields=operation,outcome,duration,index
```

Expected handoff:

```text
secret-fields=blocked; freshness-sentinel=pass; alert-threshold=baseline-derived
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Monitoring API](https://www.algolia.com/doc/rest-api/monitoring)
- [Algolia status](https://status.algolia.com/)
- [Sending events](https://www.algolia.com/doc/guides/sending-events)
