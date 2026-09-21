---
name: workhuman-core-workflow-a
description: 'Plan and execute a governed Workhuman recognition workflow from program rules through approval and reconciliation. Use when launching or changing nominations and awards. Trigger with "run a Workhuman recognition workflow".'
argument-hint: "[program-brief] [audience]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, recognition, awards, governance]
model: inherit
effort: high
compatibility: Designed for Claude Code; recognition submissions, approvals, award values, communications, and spend changes require program-owner approval
---
# Governed Workhuman Recognition Workflow

## Overview

Turn approved recognition policy into a controlled nomination or program change with eligibility, award, privacy, spend, and reconciliation evidence.

## Prerequisites

- Program rules, eligible population, company values, award policy, approvers, and budget owner
- Current tenant documentation for the supported user or integration path
- A synthetic pilot cohort, communication owner, support path, and rollback plan

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect policy and rosters, `WebFetch` to verify current Workhuman and tenant contracts, and `Write` or `Edit` for plans, fixtures, previews, and redacted receipts.

## Current Contract

Workhuman Social Recognition supports recognition connected to company values, while Admin Hub supports award management, delegate assignment, spend control and monitoring, program analysis, alerts, recommendations, and misuse detection. Exact award structures and workflow states are customer-configured.

## Authentication

Use the documented end-user, administrator, managed-integration, or API principal for each step. Do not make a service principal impersonate a nominator unless the authorized contract explicitly permits it.

## Instructions

1. Freeze purpose, eligible nominators and recipients, exclusions, value taxonomy, award policy, approvals, visibility, locales, and measurement.
2. Reconcile the eligible audience with its authoritative HCM source and quantify duplicates, inactive workers, and unresolved identities.
3. Confirm the current customer configuration and exact supported submission path; never infer award levels or payload fields.
4. Validate message policy, sensitive-data exclusions, accessibility, taxation ownership, spend controls, and misuse rules.
5. Pilot with synthetic or approved users and verify nomination, approval, notification, ledger, reporting, and cancellation behavior.
6. Present exact mutations, counts, spend exposure, approvers, schedule, communications, rollback, and support ownership.
7. After approval, execute through the supported path with idempotency or duplicate controls and bounded concurrency.
8. Reconcile expected nominations, approvals, awards, spend, and exceptions; retain a redacted receipt.

## Approval Boundaries

Do not nominate people, approve awards, change eligibility, alter award values, send communications, or spend program funds without named approval.

## Output

Return the frozen policy, audience reconciliation, contract evidence, pilot result, mutation preview, approvals, execution receipt, exceptions, and rollback status.

## Error Handling

| Condition | Response |
|---|---|
| Worker eligibility is ambiguous | Exclude the record and ask the HCM or program owner to resolve it. |
| Submission outcome is unknown | Do not resubmit until the authoritative record or support channel resolves it. |
| Spend threshold is crossed | Stop new awards and alert the budget owner; never downgrade awards silently. |

## Example

A redacted completion receipt might look like this:

```text
program=values-recognition; eligible=420; pilot=8-pass; spend-cap=approved; submitted=37; exceptions=2-held; reconciliation=exact
```

## Resources

- [Workhuman Social Recognition](https://www.workhuman.com/platform/social-recognition/)
- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)

## Next Steps

Review outcome, equity, participation, spend, and misuse signals with the program owner on the agreed cadence.
