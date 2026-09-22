---
name: clickup-observability
description: >-
  Instrument ClickUp requests, queues, webhooks, and reconciliation with content-free metrics, traces, alerts, and health evidence. Use when operating a ClickUp integration in production. Trigger with "ClickUp observability", "ClickUp metrics", or "monitor ClickUp webhooks".
argument-hint: "[service-path] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- observability
model: inherit
effort: high
compatibility: Designed for Claude Code; live telemetry must follow approved data and secret-handling policy
---
# ClickUp Integration Observability

## Overview

Expose reliability, rate pressure, delivery health, and business reconciliation without exporting task or member content.

## Prerequisites

- A typed ClickUp transport and durable webhook/job queues
- Approved telemetry fields, retention, access, sampling, and alert ownership
- Service-level objectives for request success, latency, queue age, freshness, and reconciliation

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Capture `X-RateLimit-*` values as bounded numeric telemetry without capturing the Authorization header.
- Webhook objects expose health/failure state; over-seven-second or unsuccessful delivery contributes to failure behavior.
- ClickUp retries an event up to five times, but failed events are not later resent after those attempts.
- Task names, descriptions, comments, attachments, emails, raw bodies, tokens, and webhook secrets are not telemetry.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Inventory request, queue, webhook, reconciliation, and deployment signals plus current data exposure.
2. Define low-cardinality metrics by endpoint family, version, status class, environment, and Workspace alias.
3. Add trace spans around the transport and queue without request/response content.
4. Monitor rate remaining/reset, 429s, webhook latency/status/fail count, queue age, and duplicate suppression.
5. Create actionable alerts with runbook links, owners, and tested thresholds from baseline data.
6. Validate dashboards and alerts with synthetic failures and record redaction checks.

## Approval Boundaries

Do not add user/task IDs as unbounded labels, export payloads for debugging, or reactivate a failing webhook automatically without policy.

## Output

Return signal inventory, SLOs, dashboards, alert tests, redaction results, cardinality risks, and runbook links. Separate measured evidence from proposed instrumentation.

## Error Handling

| Condition | Response |
|---|---|
| Telemetry contains work content or secrets | Stop export, quarantine data, rotate if needed, and remediate instrumentation. |
| Labels are unbounded | Aggregate or hash into a governed low-cardinality alias. |
| Alert has no owner/runbook | Do not enable paging. |
| Webhook health degrades | Queue/contain and follow the incident runbook. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
request-slo=99.9%; p95=420ms; 429=0; queue-age=18s; webhook-fail-count=0; sensitive-fields=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Webhook health](https://developer.clickup.com/docs/webhookhealth)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
