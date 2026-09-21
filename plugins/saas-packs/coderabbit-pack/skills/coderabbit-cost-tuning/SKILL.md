---
name: coderabbit-cost-tuning
description: >-
  Review plan, seat, limit, and pay-as-you-go usage from current billing evidence without hard-coded prices. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "reduce CodeRabbit cost".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, billing, cost-control, seats]
---
# CodeRabbit Cost and Usage Review

## Overview

Build an approval-ready cost decision from current dashboard and plan evidence. Prices, allowances, and entitlements are time-sensitive.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- The plans page is authoritative for current prices and hourly allowances.
- Seats and administrative roles are separate controls.
- The usage-based add-on can extend eligible PR and CLI reviews.
- Mid-cycle changes can create prorated charges.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Capture plan, cadence, seats, add-on state, and usage for one period.

2. Separate unused seats, avoidable overage, repository scope, and capacity needs.

3. Model keep, right-size, and upgrade scenarios with dated prices.

4. Present savings, impact, owner, effective date, and rollback constraints.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Never buy credits, change plans, remove seats, or alter access without billing and organization-owner approval. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A dated baseline, scenario table, evidence links, recommendation, and approval record. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Identify inactive assigned seats before a downgrade.

### Example 2

Compare a higher plan with usage credits using current evidence.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
