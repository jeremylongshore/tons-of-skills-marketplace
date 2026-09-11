---
name: salesforce-incident-runbook
description: 'Run evidence-led Salesforce integration incident response from detection through containment, recovery, reconciliation, and prevention. Use when handling service or data incidents. Trigger with "respond to Salesforce incident".'
argument-hint: "[incident-id] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, incident-response, recovery, reconciliation]
model: inherit
effort: high
compatibility: Designed for Claude Code; credential, permission, workload, event, data, and production changes require incident commander and customer approval
---
# Salesforce Integration Incident Response

## Overview

Restore business invariants safely by separating Salesforce platform state, customer org state, application behavior, data correctness, and event delivery.

## Prerequisites

- Incident commander, severity model, affected environments and workloads, communications, and evidence channel
- Current deployment, org identity, app and principal, API, limits, jobs, events, data, and reconciliation contracts
- Pre-approved containment, failover, deferral, rollback, credential revocation, and vendor escalation procedures

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce Status reports platform incidents, while org-specific authorization, limits, metadata, automation, jobs, events, and data can fail independently. A green platform status does not prove an integration or business invariant is healthy.

## Authentication

Use read-only incident access first and separate break-glass access under the customer process. Never paste tokens, sessions, private keys, raw records, or unrestricted logs into tickets or chat.

## Instructions

1. Declare severity, commander, time window, affected orgs and workloads, business invariant, data risk, and communication cadence.
2. Freeze deployments and unsafe retries; preserve request, job, event, deployment, and reconciliation identifiers.
3. Check Salesforce Status, org identity, authorization, API support, limits, metadata, automation, async jobs, event flow, and application telemetry.
4. Classify platform, org, identity, permission, schema, capacity, code, dependency, data, or consumer failure and bound impact.
5. Select the least-destructive approved containment such as pausing intake, deferring work, isolating a consumer, rollback, or credential revocation.
6. Recover in a bounded cohort, reconcile records and events by stable keys, and monitor technical and business stop signals.
7. Close only after invariants, backlog, security, and data exposure are resolved; assign root-cause and prevention work.

## Approval Boundaries

Do not rotate credentials, broaden access, disable automation, replay events, retry writes, purge queues, roll back, or fail over without incident and system owners.

## Output

Return severity, timeline, evidence, classification, containment, approved actions, recovery IDs, reconciliation, exposure assessment, communications, and prevention owners.

## Error Handling

| Condition | Response |
|---|---|
| Salesforce Status is green | Continue org and application diagnosis; do not downgrade from platform status alone. |
| Prior write outcome is unknown | Block replay and reconcile by stable business key and request evidence. |
| Containment can lose business work | Use durable deferral or quarantine and document the recovery obligation. |

## Example

A redacted completion receipt might look like this:

```text
incident=SF-311; severity=2; class=event-consumer; intake=paused; recovery=bounded; backlog=0; reconcile=exact
```

## Resources

- [Salesforce Status](https://status.salesforce.com)
- [REST API limits](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-limits.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
