---
name: algolia-cost-tuning
description: >-
  Audit Algolia usage drivers and propose measurable cost controls without hard-coded plan prices. Use when search spend, request volume, record count, replicas, or optional features need investigation. Trigger with "Algolia cost audit", "reduce Algolia usage", or "Algolia bill".
argument-hint: "[repository-path] [billing-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- cost
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Usage and Cost Review

## Overview

This skill correlates current Algolia billing and usage evidence with application behavior. It deliberately avoids embedding plan names, prices, free allowances, or assumptions that indexing is unmetered because commercial terms can change.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Treat the account's current invoice, usage dashboard, and contract as the authority for billable units.
- Separate search traffic, records, replicas, indexing activity, analytics or AI features, and non-production duplication.
- Measure request amplification caused by keystrokes, federated queries, retries, bots, and duplicate clients.
- Recommend controls only when they preserve relevance, freshness, security, and product requirements.

## Authentication

Use read-only account access or exported billing evidence. Do not put billing, usage, Analytics, or Admin credentials in frontend code or reports.

## Instructions

1. Define the billing window, applications, indices, environments, replicas, and contract source in scope.
2. Capture current usage and invoice line items without copying secret values.
3. Trace major units back to callers, UI interactions, scheduled jobs, duplicated records, and optional features.
4. Quantify each candidate change with a baseline, expected delta, uncertainty, and product tradeoff.
5. Test request debouncing, caching, record trimming, environment retention, or replica changes in a safe environment.
6. Reconcile the next usage window and retain a rollback trigger for relevance or freshness regressions.

## Approval Boundaries

Do not delete indices, remove replicas, change plans, disable analytics, or cache personalized results without owner approval and measured impact.

## Output

Return the evidence window, current drivers, ranked opportunities, estimated ranges rather than false precision, validation plan, approvals, and post-change reconciliation.

## Error Handling

| Condition | Response |
|---|---|
| Invoice and dashboard disagree | Record the reporting windows and ask account support before concluding. |
| No caller attribution | Add bounded request instrumentation before optimizing. |
| Savings harms relevance | Rollback and preserve the measured comparison. |
| Plan terms unavailable | State the gap; never substitute remembered pricing. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
window=last-complete-billing-cycle; environments=prod,stage; pricing-source=current-invoice
```

Expected handoff:

```text
finding=duplicate-stage-replicas; estimate=range; change=pending-owner-review
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Algolia pricing](https://www.algolia.com/pricing/)
- [Usage API](https://www.algolia.com/doc/rest-api/usage)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
