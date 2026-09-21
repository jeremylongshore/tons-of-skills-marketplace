---
name: palantir-observability
description: >-
  Design Foundry observability using build metrics, execution history, governed logs, audit exports, and monitoring subscriptions. Use when defining dashboards, alerts, or operational evidence. Trigger with "Foundry observability" or "Palantir monitoring".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[pipeline-action-function-or-module]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, observability, monitoring]
---
# Palantir Foundry Observability Design

## Overview

Use Foundry-native telemetry for Foundry workloads and export only when there is a governed consumer. Distinguish operational metrics, service/trace logs, execution history, monitoring notifications, and audit logs because they have different access and retention semantics.

## Prerequisites

- Identify the resource, owner, service objectives, failure modes, audiences, data classification, and incident process.
- Inventory available build metrics, resource metrics, execution history, logs, monitoring views, audit exports, and external notification targets.
- Read `references/official-docs.md` and confirm current log-access and marking policy.
- Define the minimum telemetry needed to detect user-visible or data-quality failures.

## Current Contract

- Transform build metrics expose CPU, memory, and job behavior in build reports.
- Ontology and AIP metrics, execution history, and logs have different permission requirements; logs may require Edit permission, enabled log access, and markings.
- Organization log exports support Palantir or OpenTelemetry payload formats and must respect source-executor and export-dataset marking requirements.
- Audit logs record high-level security and administrative activity and require tightly controlled export datasets.

## Instructions

1. Define measurable service and data objectives, owners, thresholds, and response actions before creating dashboards.

2. Map each signal to the authoritative Foundry surface and identify its permission, marking, retention, and export requirements.

3. Create views or exports with minimum fields and protected destinations; avoid logging object values, prompts, or secrets.

4. Test each alert with a controlled failure and confirm routing, deduplication, acknowledgement, escalation, and recovery.

5. Review false positives, blind spots, access, retention, and evidence quality after a representative operating window.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Resource owners approve service objectives; security/data owners approve log access, markings, and exports; organization administrators approve audit exports; incident owners approve external routing. Never enable broad logs merely to make dashboards easier.

## Output

An observability matrix with objectives, signals, Foundry sources, queries/views, thresholds, audiences, permissions, markings, retention, notification routes, runbooks, and tested alert receipts.

## Error Handling

| Condition | Response |
|---|---|
| Metrics exist but no action is defined | Assign owner, threshold, severity, and runbook before enabling the alert. |
| Logs reveal protected values | Disable or restrict access/export, correct markings and logging, and review exposure. |
| An export omits required source markings | Stop the export and align source-executor and destination controls. |
| Health is green while data is stale | Add freshness, build, transaction, and downstream-consumer signals. |

## Examples

### Example 1

Monitor a transform with build success, freshness, duration, CPU, memory, input/output volume, and data expectations, then test the alert by failing a sandbox build.

### Example 2

Govern an action's service logs by enabling log access with markings, limiting viewers, defining retention, and keeping audit logs as a separate security evidence stream.

## Validation

- Every signal maps to a user, data, security, or reliability objective.
- Controlled tests exercise alert, route, acknowledgement, and recovery.
- Logs and exports have approved permissions, markings, and retention.
- Dashboards include freshness and correctness rather than only endpoint availability.
- Quarterly review has an owner and evidence source.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
