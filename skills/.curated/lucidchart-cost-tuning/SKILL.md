---
name: lucidchart-cost-tuning
description: 'Review Lucid licensing, seats, plan capabilities, and integration operating effort without fabricating usage prices. Use when controlling Lucidchart total cost or right-sizing access. Trigger with "reduce Lucidchart cost".'
argument-hint: "[inventory-path] [review-period]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, licensing, governance, cost]
model: inherit
effort: medium
compatibility: Designed for Claude Code; plan, billing, seat, and pricing decisions require current Lucid commercial evidence and account-owner approval
---
# Lucid Cost and Value Review

## Overview
Produce an evidence-backed right-sizing plan for licenses, seats, plan-dependent capabilities, and integration operations. Lucid's public developer documentation does not establish a universal per-export or per-API-call price.

## Prerequisites
- Authorized seat, role, plan, renewal, and usage evidence
- Current contract or official pricing source supplied by the account owner
- Named business and data owners for affected integrations

## Tool Discipline
Use `Read`, `Glob`, and `Grep` for approved exports and repository evidence, `WebFetch` for current official plan documentation, and `Write` or `Edit` only for local analysis and a proposed action ledger.

## Current Contract
Separate verified commercial terms from technical limits and internal operating costs. Treat public list prices and plan features as time-sensitive; never extrapolate them from API traffic, archive size, or export count.

## Authentication
Prefer redacted offline exports. If account access is required, use read-only least privilege and never expose invoices, tokens, personal data, or contract terms beyond the approved audience.

## Instructions
1. Record evidence date, billing period, currency, contract source, current plan, and exclusions.
2. Inventory assigned seats, roles, active owners, dormant accounts, shared integrations, extensions, connectors, and critical documents.
3. Attribute cost only from invoices or current official commercial evidence; mark unknowns explicitly.
4. Measure operational effort separately: support, failures, connector hosting, observability, and manual reconciliation.
5. Propose reversible actions with owner, dependency, savings hypothesis, risk, and restoration path.
6. Present removals, role changes, plan changes, and integration shutdowns for approval.
7. After approved changes, compare realized invoices and service outcomes over a complete billing period.

## Approval Boundaries
Do not remove seats, downgrade plans, cancel services, or disable integrations based only on inactivity signals or estimated pricing.

## Output
Return evidence dates, verified and unknown costs, seat/role inventory, value signals, proposals, risks, approvals, and follow-up measurement dates.

## Error Handling
| Condition | Response |
|---|---|
| Price or feature differs across sources | Use the signed contract/account view and flag the discrepancy. |
| Usage evidence is incomplete | Label the conclusion provisional; do not reclaim access. |
| Integration owner is unknown | Quarantine the proposal pending ownership, not the service. |

## Example
```text
period=2026-Q3; assigned=84; review-candidates=7; verified-price-source=contract; destructive-actions=0
```

## Resources
- [Official documentation map](references/official-docs.md)

## Next Steps
Schedule the approved review against the next complete invoice and restore any capability whose service indicators regress.
