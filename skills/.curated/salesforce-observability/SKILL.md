---
name: salesforce-observability
description: 'Build Salesforce integration observability across application traces, platform status, limits, async jobs, events, logs, and business reconciliation. Use when designing monitoring. Trigger with "monitor Salesforce integration".'
argument-hint: "[integration] [service-objective]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, observability, monitoring, event-monitoring]
model: inherit
effort: high
compatibility: Designed for Claude Code; log, Event Monitoring, alert, and data access require entitlement and security approval
---
# Salesforce Integration Observability and Reconciliation

## Overview

Connect technical telemetry to Salesforce platform state and business correctness without exporting sensitive records into monitoring systems.

## Prerequisites

- System context, service and business objectives, APIs, jobs, event channels, orgs, and owners
- Current Salesforce Status, Limits, EventLogFile or entitled Event Monitoring, async-job, and event-usage surfaces
- Telemetry data classification, redaction, retention, alert routing, incident, and reconciliation policies

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce Status, REST limits, response headers, async jobs, platform-event usage, debug logs, and Event Monitoring expose different signals with different entitlements and delays. Limits resource values can lag recent consumption.

## Authentication

Use separate read-only monitoring access with minimum permissions. Never emit access tokens, session IDs, authorization headers, raw SOQL results, record payloads, or unrestricted user and org identifiers as telemetry.

## Instructions

1. Define availability, latency, throughput, error, freshness, completeness, duplicate, limit, job, event-lag, and business-invariant objectives.
2. Instrument the adapter with redacted request IDs, operation class, API version, timing, outcome, retry, and reconciliation state.
3. Collect Salesforce platform status, relevant limit and header values, async job summaries, event metrics, and entitled logs.
4. Normalize timestamps, org and environment aliases, deployment IDs, and correlation IDs without exposing customer record data.
5. Build dashboards by environment and workload with freshness labels and separate technical from business-correctness views.
6. Alert on sustained objective breaches, capacity margin, auth failure, job failure, event gap, wrong-org binding, and reconciliation mismatch.
7. Test alerts and runbooks in non-production, measure noise and blind spots, and assign review and retention owners.

## Approval Boundaries

Do not enable broad logging, retrieve sensitive event files, expand retention, export record data, or create production alerts without security, admin, and incident-owner approval.

## Output

Return the signal catalog, instrumentation contract, dashboards, alerts, redaction and retention rules, runbook links, test receipt, blind spots, and owners.

## Error Handling

| Condition | Response |
|---|---|
| Signal is unavailable without an add-on | Document the entitlement boundary and implement a lower-risk compensating signal. |
| Telemetry contains record or credential data | Block export, purge according to policy, rotate exposed credentials, and repair redaction. |
| Platform is healthy but business reconciliation fails | Escalate as an application or data incident rather than closing on status alone. |

## Example

A redacted completion receipt might look like this:

```text
service=customer-sync; slo=defined; traces=redacted; limits=dated; jobs=monitored; event-gap=alerted; reconcile=exact
```

## Resources

- [Salesforce Status](https://status.salesforce.com)
- [EventLogFile object](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_eventlogfile.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
