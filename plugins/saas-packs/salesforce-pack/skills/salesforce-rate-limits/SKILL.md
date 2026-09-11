---
name: salesforce-rate-limits
description: 'Analyze and govern Salesforce API, asynchronous, bulk, and event capacity from current org allocations and usage evidence. Use when preventing or resolving exhaustion. Trigger with "govern Salesforce limits".'
argument-hint: "[org-alias] [workload]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, limits, capacity, backpressure]
model: inherit
effort: high
compatibility: Designed for Claude Code; capacity changes, workload deferral, and production concurrency require platform and business owner approval
---
# Salesforce Org Limit and Capacity Governance

## Overview

Treat limits as shared, time-varying org contracts and allocate headroom across integrations without publishing fixed universal thresholds.

## Prerequisites

- Authorized org, workload, API and event modes, business priority, and peer integrations
- Current Limits resource, Sforce-Limit-Info, job, event-usage, and application telemetry
- Platform, integration, incident, and business owners with a deferral policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

The versioned Limits REST resource returns maximum and remaining allocations and can lag consumption by up to five minutes. Sforce-Limit-Info reports REST API usage; names, allocations, windows, grace behavior, and entitlements vary by org, edition, license, API version, and workload.

## Authentication

Use an approved read-only principal with the permission required to view limits. Do not expose tokens, org identifiers, or unrelated allocation details in public metrics or receipts.

## Instructions

1. Inventory every workload sharing the org, its API mode, priority, schedule, concurrency, retry behavior, and owner.
2. Discover a supported API version and capture current Limits and response-header evidence with timestamps.
3. Map relevant REST, bulk, async, Apex, storage, and event allocations to workloads and business deadlines.
4. Model normal, burst, retry-storm, backfill, and incident demand with an explicit measurement-lag safety margin.
5. Define admission, concurrency, batching, backpressure, deferral, and stop policies per priority class.
6. Test the policy with synthetic work in an authorized non-production org and prove hard exhaustion is not blindly retried.
7. Monitor actual usage and reconcile deferred work; review allocations and policy after releases, license changes, and incidents.

## Approval Boundaries

Do not consume production capacity for testing, raise concurrency, defer critical work, purchase capacity, or disable peer integrations without accountable owners.

## Output

Return the dated allocation snapshot, workload budget, scenarios, safety margin, controls, alerts, deferred-work ledger, and review owner.

## Error Handling

| Condition | Response |
|---|---|
| Limits values change between reads | Use timestamps and the documented measurement lag; avoid rapid concurrent reads as a consistency oracle. |
| Hard allocation is exhausted | Stop admission and reconcile pending work; exponential backoff alone cannot create capacity. |
| Workload ownership is unknown | Do not assign it shared capacity until an owner and priority are established. |

## Example

A redacted completion receipt might look like this:

```text
org=production; resources=rest+bulk+events; snapshot=dated; margin=owner-approved; admission=active; deferred=42; blind-retry=off
```

## Resources

- [Limits REST resource](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-limits.html)
- [Sforce-Limit-Info header](https://developer.salesforce.com/docs/platform/api-rest/guide/headers-api-usage.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.

