---
name: ramp-observability
description: >-
  Instrument Ramp API clients, webhook consumers, deferred tasks, and accounting syncs with safe service and financial-correctness signals. Use when defining dashboards, alerts, traces, or reconciliation health. Trigger with "monitor Ramp integration" or "Ramp observability".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, observability, monitoring, slis]
---
# Ramp Integration Observability

## Overview

Monitor both transport health and business completeness. A low error rate is insufficient if events are missing, objects remain unsynced, or duplicate financial effects occur.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp returns `x-trace-id` on API responses for request correlation.
- Webhook deliveries carry a stable event ID across retries and may arrive out of order.
- Deferred operations have task state that must be polled or reconciled rather than inferred from request acceptance.
- Accounting correctness requires agreement among Ramp source state, downstream references, and Ramp sync receipts.

## Instructions

1. Define service objectives for request success and latency, webhook receive/processing lag, queue age, deferred-task age, sync completeness, duplicate suppression, and reconciliation freshness.

2. Emit method plus path template, status class, environment, entity surrogate, trace ID, attempt, latency, page count, event type, event-ID hash, and release without sensitive values.

3. Track business-state gauges for unsynced and failed objects, unmatched ERP references, webhook reconciliation gaps, suspended workers, and production-write interlock state.

4. Alert on sustained symptom and business impact with a runbook link, owner, environment, affected entity/object class, and safe diagnostic query.

5. Test dashboards and alerts with sandbox events and fault injection; verify telemetry redaction, cardinality bounds, retention, and incident usefulness.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Service owners approve SLOs and alerts; security/privacy approve telemetry fields and retention; finance/data owners approve reconciliation thresholds.

## Output

An SLI/SLO catalog, safe telemetry schema, dashboards, alert routes, reconciliation monitors, synthetic tests, retention controls, and runbook linkage.

## Error Handling

| Condition | Response |
|---|---|
| Metrics are green but finance reports missing objects | Treat reconciliation and source/destination counts as authoritative; investigate coverage gaps. |
| Labels explode in cardinality | Replace raw IDs and URLs with templates, bounded classes, or one-way sampled identifiers. |
| A trace includes a token or payload | Restrict access, purge where possible, rotate credentials, and fix instrumentation before re-enabling it. |

## Examples

### Example 1

Alert when `transactions.ready_to_sync` events are processed but matching ERP references fail to appear within the objective.

### Example 2

Correlate a 504 spike by path template and Ramp trace ID while keeping transaction details out of telemetry.

## Validation

- Service and financial-correctness objectives are both represented.
- Trace IDs support diagnosis without exposing secrets or sensitive payloads.
- Webhook duplicates, out-of-order events, deferred tasks, and reconciliation gaps are visible.
- Each actionable alert has an owner, threshold rationale, and tested runbook.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
