---
name: linear-cost-tuning
description: >-
  Analyze and reduce the infrastructure and quota cost of a Linear integration through workload accounting, query budgets, and push-based updates. Use when a sync is wasteful, throttled, or expensive to operate. Trigger with "reduce Linear API load", "budget Linear queries", or "tune Linear integration cost".
argument-hint: "[repository-path] [workload-or-budget]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- capacity-tuning
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Workload and Capacity Tuning

## Overview

Treat cost as the integration's compute, queue, storage, support, and quota consumption; do not claim a fixed Linear API price from cached documentation.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Linear publishes request and complexity budgets, not a universal per-request price; plan and contract entitlements are dynamic.
- Polling is discouraged; webhooks are the primary change signal when supported.
- Filtering, explicit page sizes, narrow field selection, and updated-time ordering reduce both query complexity and local processing.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Measure requests, complexity, payload bytes, queue time, retries, storage growth, and operator toil by workflow.
2. Separate required freshness from habitual polling and replace supported polling loops with verified webhooks.
3. Set per-workload request and complexity budgets below the applicable shared limits.
4. Reduce fields, page sizes, fan-out, duplicate reads, and retention while preserving correctness and audit needs.
5. Load-test with synthetic data and compare before/after throughput, freshness, and failure recovery.
6. Verify current plan terms with the workspace owner before presenting monetary savings.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| No baseline | Instrument the workload before proposing savings. |
| Quota confused with price | Report request/complexity consumption separately from commercial terms. |
| Webhook gap | Keep a bounded reconciliation job for unsupported or missed events. |
| Optimization changes semantics | Reject it and preserve correctness over a smaller metric. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
requests-hour=1800; complexity-hour=1200000; polling=60s; freshness-slo=5m
```

Expected handoff:

```text
push-candidates=identified; budget=headroom-set; price-claim=none
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
