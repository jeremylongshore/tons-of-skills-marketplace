---
name: miro-observability
description: "Design and implement repository-side Miro instrumentation with safe metrics, rate-credit headers, semantic outcomes, and actionable alerts. Use when operating a Miro integration. Trigger with \"monitor Miro integration\"."
argument-hint: "[service] [slo]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- observability
- operations
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Integration Observability

## Overview

Observe vendor transport and business correctness without turning board content, credentials, or high-cardinality identifiers into telemetry; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Service objectives and supported user journeys
- Operation, retry, queue, reconciliation, and token lifecycle map
- Approved telemetry fields, retention, access, and alert owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary. These declared tools do not call authenticated Miro APIs or deployment CLIs; implement client, configuration, and test changes, then return exact operator commands or an approval-gated handoff for live execution.

## Current Contract

- Rate responses expose limit, remaining, and reset credit headers suitable for gauges and forecasts.
- HTTP success alone does not prove a mutation or synchronization outcome; semantic reconciliation needs separate signals.
- Miro's public status is a dependency clue, not proof that a local authorization or tenant issue is vendor-wide.
- Board names, item content, resource URLs, tokens, and raw user/team IDs should not be metric labels or logs.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Define SLIs for availability, latency, errors, credits, queue age, token refresh, reconciliation lag, and semantic drift.
2. Instrument adapters with bounded operation names, status classes, retry decisions, and redacted tenant hashes.
3. Parse rate headers and emit remaining fraction, reset time, weighted demand, and throttled duration.
4. Trace OAuth refresh and write/reconcile spans without recording credential or content fields.
5. Create alerts tied to user impact and runbooks, including Miro status as corroborating context.
6. Test dashboards and alerts with synthetic 401, 429, 5xx, drift, queue, and stale-checkpoint failures.

## Approval Boundaries

Do not add board/user content, raw identifiers, credentials, or unrestricted URLs to telemetry without privacy/security approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return SLI/SLO table, metric/log/trace fields, dashboards, alerts, redaction tests, runbook links, and coverage gaps. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Metric cardinality grows unbounded | Remove raw IDs and aggregate by bounded dimensions. |
| Alert has no owner/action | Disable paging until a runbook and owner exist. |
| Rate headers are absent | Mark capacity unknown and use conservative request controls. |
| Status page is green during failures | Continue local auth, scope, network, and tenant diagnosis. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
availability=99.96%; p95=740ms; remaining-p10=42%; reconcile-lag-p95=210s; content-labels=0; alerts-tested=6/6
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Rate limits](https://developers.miro.com/reference/rate-limiting)
- [Miro status](https://status.miro.com/)
