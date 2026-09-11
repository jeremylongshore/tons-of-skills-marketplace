---
name: mindtickle-cost-tuning
description: 'Govern Mindtickle subscription, seat, package, integration, support, and operating costs from contract evidence and adoption outcomes. Use when preparing a renewal or portfolio review. Trigger with "optimize Mindtickle cost".'
argument-hint: "[review-period] [contract-summary]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, cost-governance, licensing, adoption]
model: inherit
effort: medium
compatibility: Designed for Claude Code; contract, seat, package, support, and renewal changes require commercial and business-owner approval
---
# Mindtickle Commercial and Adoption Review

## Overview

Connect contracted spend to licensed population, package use, integration effort, support needs, and measured outcomes without inventing public pricing or consumption meters.

## Prerequisites

- Current order, renewal date, packages, licensed populations, services, support tier, and owners
- Approved aggregate adoption and outcome evidence for the review period
- Finance rules for allocation, savings claims, and renewal decisions

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect contract summaries and aggregate reports, `WebFetch` for current public service descriptions, and `Write` or `Edit` for a sanitized cost model and decision record.

## Current Contract

Mindtickle publicly describes package-dependent modules, standard and premium support, implementation services, and separately scoped custom work. Public pages do not establish a universal seat price or API-consumption charge; signed commercial terms control.

## Authentication

Use approved aggregate reports and contract summaries. Restrict learner-level adoption, invoices, pricing, and negotiated terms to authorized reviewers and exclude them from public artifacts.

## Instructions

1. Freeze the contract baseline: term, packages, licensed units, support, services, commitments, renewal windows, and termination obligations.
2. Map each paid capability to an accountable owner, intended population, workflow, adoption measure, and business outcome.
3. Reconcile licensed, provisioned, active, disabled, duplicate, and exception populations using their systems of record.
4. Separate subscription spend from customer engineering, administration, content, identity, support, and change-management costs.
5. Identify unused entitlements, overlapping tools, inactive access, avoidable custom work, and unsupported savings assumptions.
6. Model keep, right-size, consolidate, and expand scenarios with one-time costs, risks, evidence confidence, and decision dates.
7. Present all seat, package, or support changes for business, finance, identity, and commercial approval.
8. Record the decision and validate realized outcomes against the baseline after implementation.

## Approval Boundaries

Do not remove access, change packages, disclose negotiated pricing, or count forecast savings as realized without the authorized owners.

## Output

Return the contract baseline, entitlement-to-outcome map, population reconciliation, total-cost view, scenarios, confidence, approvals, decision, and realization review.

## Error Handling

| Condition | Response |
|---|---|
| Contract units cannot be reconciled | Mark savings unknown and resolve the source-of-record mismatch. |
| Adoption metric exposes individuals | Aggregate or suppress it according to policy. |
| A reduction breaks a workflow | Quantify migration and business impact before recommending it. |

## Example

```text
period=fy26; packages=contract-confirmed; population=reconciled; scenarios=3; negotiated-rates=restricted; decision=right-size-at-renewal
```

## Resources

- [Subscription services](https://www.mindtickle.com/legal/description-of-subscription-services/)
- [Mindtickle professional services](https://www.mindtickle.com/legal/professional-services-scope-and-services-description/)
- [Mindtickle Support Services](https://www.mindtickle.com/legal/support-services/)

## Next Steps

Assign owners and dates for approved changes and measure realized value after the next full operating cycle.
