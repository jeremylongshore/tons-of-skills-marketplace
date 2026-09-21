---
name: procore-observability
description: >-
  Monitor Procore Integration Health, API activity, rate budget, webhook deliveries, and synchronization freshness with route-level ownership. Use when defining dashboards, alerts, service objectives, or a regular health-review cadence. Trigger with: "monitor Procore integration", "review Procore API activity", "alert on Procore health".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-and-service-objectives]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - observability
  - integration-health
compatibility: 'Requires access to Procore Developer Portal health data plus application metrics, logs, queue state, and deployment identifiers.'
---

# Procore Integration Health Observability

## Overview

Combine provider-side observations with application-side service signals. Procore's Integration Health and API Call Activity Report identify unhealthy response patterns and routes, while the integration must supply latency, backlog, freshness, reconciliation, and release context.

## Prerequisites

- App owner with Developer Portal access and a recurring review cadence
- Normalized route, status, latency, retry, queue, webhook, and freshness telemetry
- Release identifiers, endpoint owners, alert destinations, and incident runbook

## Instructions

### Step 1: Export provider evidence

Review Integration Health and download the production API activity report. Preserve report time range, app identity, and a checksum in the audit receipt.

### Step 2: Join route ownership

Map normalized route, method, status, and count to the responsible service and adapter. Flag unknown traffic as a legacy deployment or credential-compromise hypothesis.

### Step 3: Monitor provider limits

Track rate limit, remaining budget, reset time, Retry-After, 401, 403, 404, 422, 429, and 5xx outcomes by route and release.

### Step 4: Monitor data freshness

Track webhook acknowledgment and delivery outcomes, queue age, deduplication, reconciliation cursor age, changed records, and parity failures.

### Step 5: Define actionable alerts

Every alert names the affected tenant boundary, route owner, runbook, severity, and recovery condition. Exclude tokens, payloads, names, and signed URLs.

### Step 6: Close the loop

After remediation, verify application metrics and the provider observation history. Record when provider-side status may lag the underlying fix.

## Authentication

Provider evidence is accessed through authorized Developer Portal sessions, while API probes use the intended OAuth 2.0 principal. Observability stores aliases and normalized metadata, never tokens or raw construction payloads.

## Tool Discipline

Use Read and Grep to inspect reports, telemetry, releases, and runbooks. Use Write or Edit only for the approved dashboard, alert, mapping, or redacted receipt; do not broaden log collection to raw customer data.

## Output

- Provider and application signal inventory
- Route ownership, objectives, alerts, and runbook links
- Health-review and remediation verification receipt

Return current health, dominant routes and failures, freshness risk, owner, action, and expected recovery signal.

## Examples

An alert ties rising 403 counts on one normalized route to a specific adapter release and company alias. The operator fixes routing, verifies the error rate locally, and then watches the provider's daily health history catch up.

## Error Handling

| Failure | Response |
| --- | --- |
| API traffic has no owner | Treat it as potentially stale or compromised and investigate credential usage. |
| Provider and app metrics disagree | Preserve both time windows and reconcile sampling, release, and tenant scope. |
| Alert contains payload data | Remove the field and replace it with an alias or hash. |
| Health status remains stale | Check documented refresh cadence before declaring the fix ineffective. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Integration Health](https://developers.procore.com/documentation/integration-health)
- [API Call Activity Report](https://developers.procore.com/documentation/api-activity-export)
- [Rate limiting](https://developers.procore.com/documentation/rate-limiting)
