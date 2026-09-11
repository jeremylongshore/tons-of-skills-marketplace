---
name: salesforce-advanced-troubleshooting
description: 'Analyze complex Salesforce integration failures across request traces, metadata, query plans, automation, locks, jobs, events, and limits. Use when basic triage stalls. Trigger with "deep diagnose Salesforce".'
argument-hint: "[incident-id] [request-or-job-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, troubleshooting, query-plan, automation]
model: inherit
effort: high
compatibility: Designed for Claude Code; deep logs, trace flags, query feedback, job access, and production reproduction require support and data-owner approval
---
# Salesforce Advanced Integration Troubleshooting

## Overview

Build and falsify layered hypotheses with minimum evidence rather than changing several org, query, permission, or retry variables at once.

## Prerequisites

- Basic triage record, exact time window, environment, release, principal, request or job IDs, and current symptom
- Architecture, API and event contracts, object metadata, automation map, limits, deployments, and prior baselines
- Incident commander, application, Salesforce platform, security, data, and vendor support owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce diagnostic behavior spans versioned REST responses, debug logs, query feedback, async jobs, event usage, and org configuration. REST query explain is Beta and must be corroborated; diagnostic surface availability varies by entitlement and permission.

## Authentication

Use the narrowest diagnostic principal and time window. Never enable broad logging or collect unredacted queries, records, tokens, sessions, org identifiers, or user data without explicit authorization.

## Instructions

1. Restate the invariant, symptom, first failure, blast radius, changes, retry history, and what basic triage already ruled out.
2. Construct hypotheses across client, network, OAuth, permission, sharing, metadata, query, automation, lock, limit, async, event, and downstream layers.
3. Collect one discriminating redacted signal per hypothesis using request IDs, logs, limits, job results, metadata fingerprints, and deployment IDs.
4. Use query explain or plan evidence only under its documented status and compare it with representative measured execution.
5. Reproduce with synthetic data or read-only requests, then change one variable at a time under a defined stop condition.
6. Confirm root cause by restoring the invariant with the smallest reversible fix and disproving leading alternatives.
7. Remove trace settings, reconcile affected data or events, publish evidence and uncertainty, and create prevention tests and alerts.

## Approval Boundaries

Do not broaden tracing, query sensitive data, change indexes or automation, increase limits, replay work, or reproduce writes in production without owners.

## Output

Return the hypothesis table, evidence and timeline, reproduced condition, root cause and confidence, approved fix, reconciliation, cleanup, and prevention work.

## Error Handling

| Condition | Response |
|---|---|
| Evidence supports multiple causes | Report uncertainty and design the next discriminating test instead of declaring a root cause. |
| Diagnostic surface is unavailable | Record the entitlement or permission boundary and use an approved alternative or Salesforce Support. |
| Trace collection changes system behavior | Stop, remove the trace, and use less invasive evidence. |

## Example

A redacted completion receipt might look like this:

```text
incident=SF-311; hypotheses=7; disproved=6; root=lock-order; fix=ordered-batches; canary=pass; traces=removed
```

## Resources

- [REST query performance feedback](https://developer.salesforce.com/docs/platform/api-rest/guide/dome-query-explain.html)
- [Apex debug logs](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_debugging_debug_log.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
