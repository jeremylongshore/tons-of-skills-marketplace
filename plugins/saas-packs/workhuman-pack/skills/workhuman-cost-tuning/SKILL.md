---
name: workhuman-cost-tuning
description: 'Govern Workhuman recognition budget, award spend, redemption, licensing, services, and integration operations using current customer evidence. Use when reviewing cost and value. Trigger with "optimize Workhuman cost".'
argument-hint: "[program] [review-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, cost, budget, governance]
model: inherit
effort: high
compatibility: Designed for Claude Code; budget, award, eligibility, license, service, and program changes require finance, HR, procurement, and program-owner approval
---
# Workhuman Cost and Recognition-Budget Governance

## Overview

Build a dated cost and value model that separates contract charges, recognition awards, redemption effects, services, and customer-operated integration costs.

## Prerequisites

- Current order form, invoices, program budget, award ledger, redemption reporting, and implementation or support statements
- Eligible population, participation and outcome definitions, finance policy, and program owner
- Data classification and approved aggregation thresholds for workforce analysis

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved financial and operational evidence, `WebFetch` for current public context, and `Write` or `Edit` for models, scenarios, and redacted decision records.

## Current Contract

Workhuman publicly describes active spend monitoring and control in Admin Hub and a points-based global Store. Public pages do not provide universal customer pricing or prove that one API call, award, point, or redemption has a fixed cost; use customer contract and ledger evidence.

## Authentication

Use read-only authorized exports or reports for analysis. Separate financial, program, and technical access and never expose individual compensation, award, balance, or redemption details in broad reports.

## Instructions

1. Freeze the review window, population, currencies, budget basis, contract date, and owners.
2. Reconcile invoices and commitments with recognition awards, active spend, redemption or liability reporting, services, taxes, and customer infrastructure.
3. Normalize currencies and time periods while preserving source, effective date, and accounting treatment.
4. Calculate participation, recognition reach, manager and peer distribution, award mix, redemption experience, operational effort, and approved outcome measures.
5. Detect overspend, underspend, concentration, inequity, dormant entitlements, duplicate services, failed jobs, and support-heavy workflows without exposing individuals.
6. Model bounded scenarios with assumptions, confidence, financial impact, cultural or equity risk, and reversibility.
7. Present policy, budget, eligibility, contract, or architecture changes to finance, HR, procurement, privacy, and program owners.
8. After approval, canary reversible changes and compare spend, participation, equity, support, and business outcomes.

## Approval Boundaries

Do not change budgets, award values, eligibility, redemption policy, licenses, contracts, or workforce communications without accountable owners.

## Output

Return the reconciled baseline, dated sources, allocation and value metrics, anomalies, scenarios, assumptions, approvals, canary result, and review date.

## Error Handling

| Condition | Response |
|---|---|
| Invoice and ledger totals disagree | Preserve both, stop optimization, and route reconciliation to finance and the program owner. |
| A scenario harms equity or recognition quality | Reject it even if nominal spend falls. |
| Pricing evidence is stale | Mark the model provisional and obtain current customer terms. |

## Example

A redacted completion receipt might look like this:

```text
window=FY2026-Q3; sources=invoice+award-ledger+ops; reconciliation=exact; scenarios=3; recommendation=canary-schedule-change; savings=not-guaranteed
```

## Resources

- [Workhuman Social Recognition](https://www.workhuman.com/platform/social-recognition/)
- [Workhuman Store](https://www.workhuman.com/capabilities/rewards/)

## Next Steps

Review approved changes after a representative cycle and reverse them if participation, equity, quality, or outcomes regress.
