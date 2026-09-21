---
name: salesforce-cost-tuning
description: 'Analyze Salesforce license, add-on, storage, event, API, support, middleware, and operating costs from current customer evidence. Use when making cost and value decisions. Trigger with "optimize Salesforce cost".'
argument-hint: "[org-or-program] [review-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, cost, licensing, governance]
model: inherit
effort: high
compatibility: Designed for Claude Code; commercial, license, retention, architecture, and workload changes require procurement, finance, platform, and business approval
---
# Salesforce Cost and Value Governance

## Overview

Build a dated total-cost model that connects commercial terms and technical consumption to business outcomes without inventing public prices or savings.

## Prerequisites

- Current order forms, invoices, license assignments, add-ons, storage, support, and vendor or partner statements
- Org usage, API and event allocations, middleware, compute, operations, incident, and migration evidence
- Finance, procurement, Salesforce platform, security, data, architecture, and business owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce editions, licenses, add-ons, storage, event delivery, API allocations, support, and partner services are customer-specific and change over time. Public documentation cannot establish one customer's price or entitlement.

## Authentication

Use read-only approved billing, contract, org, and telemetry evidence. Separate commercial and technical access and do not expose user-level license, compensation, customer, or record data.

## Instructions

1. Freeze review window, currencies, orgs, products, contracts, populations, workloads, outcomes, and accountable owners.
2. Reconcile invoices and commitments with assigned and active licenses, storage, API and event usage, add-ons, support, middleware, compute, and labor.
3. Normalize time periods and currencies while preserving source, effective date, allocation method, and confidence.
4. Identify unused or mismatched assignments, duplicate capability, retention growth, event or API pressure, support load, and architectural overhead.
5. Model bounded scenarios with commercial assumptions, technical effects, business impact, security and data risk, reversibility, and confidence.
6. Present license, contract, retention, integration, scheduling, or architecture changes to the corresponding owners.
7. Canary reversible operational changes, reconcile savings and outcomes, and never claim savings until invoices and service quality confirm them.

## Approval Boundaries

Do not remove licenses, change contracts, delete data, reduce support, throttle business-critical work, or re-architect integrations without owners.

## Output

Return the reconciled baseline, dated sources, allocation model, anomalies, scenarios, assumptions, approvals, canary evidence, realized-versus-forecast result, and review date.

## Error Handling

| Condition | Response |
|---|---|
| Invoice and org inventory disagree | Preserve both and route reconciliation to finance, procurement, and the platform owner. |
| Scenario relies on undocumented pricing or entitlement | Mark it invalid until current customer terms are obtained. |
| Nominal savings degrade compliance or business outcomes | Reject or redesign the scenario regardless of headline cost. |

## Example

A redacted completion receipt might look like this:

```text
window=FY2026-Q3; sources=contract+invoice+org+ops; reconciliation=exact; scenarios=4; approved=1; savings=unrealized
```

## Resources

- [Salesforce REST limits](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-limits.html)
- [Salesforce release notes](https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
