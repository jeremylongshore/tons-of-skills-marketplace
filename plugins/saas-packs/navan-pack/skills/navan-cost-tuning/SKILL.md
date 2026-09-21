---
name: navan-cost-tuning
description: >-
  Analyze Navan travel, expense, integration, and operating costs without freezing mutable prices. Use when setting budgets or evaluating workflow tradeoffs. Trigger with "reduce Navan cost", "Navan budget", or "control travel spend".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<program> <period> <budget-owner>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, cost]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan T&E Cost Control

## Overview

Analyze Navan travel, expense, integration, and operating costs without freezing mutable prices. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Navan publicly describes policy controls, real-time spend visibility, analytics, travel, expense, and enterprise offerings. Actual fees, savings definitions, program terms, and tenant entitlements come from the current agreement and account.

## Authentication

Use read-only reporting access for analysis. Policy, card, reimbursement, booking, contract, or budget changes remain separate privileged actions.

## Instructions

1. Define the business period, entities, currencies, and decision owner.
2. Separate vendor fees, travel spend, expense spend, payment costs, integration operations, and exception handling.
3. Capture current agreement terms and account reports as dated evidence.
4. Normalize currencies and distinguish forecast, authorized, booked, incurred, reimbursed, and settled amounts.
5. Model savings options with traveler impact, control risk, and implementation cost.
6. Approve changes separately and measure realized outcomes against the baseline.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Pricing negotiations, policy changes, booking restrictions, card controls, reimbursement rules, or production architecture changes require authorized owners.

## Error Handling

- Do not treat marketing savings claims as tenant results.
- Never mix booked, incurred, and settled amounts.
- A cheaper control that harms duty of care or compliance is not an optimization.

## Output

Return the cost model, evidence dates, currency method, options, risks, approvals, and measurement plan. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Compare integration operating cost with manual exception handling.
- Measure policy changes using approved aggregate analytics.

## Validation

Reconcile totals to authoritative reports and test currency, cancellations, refunds, late charges, and incomplete periods. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
