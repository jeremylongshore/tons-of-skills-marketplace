---
name: miro-cost-tuning
description: "Analyze and execute this workflow: reduce Miro API credit consumption while preserving freshness, completeness, and user experience. Use when right-sizing polling or synchronization. Trigger with \"reduce Miro API usage\"."
argument-hint: "[workload] [freshness-slo]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- credits
- efficiency
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Credit-Efficiency Planning

## Overview

Treat API credits as capacity, not currency. Attribute demand by operation and caller, then remove waste without inventing a dollar price; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Request and rate-header telemetry by operation
- Documented endpoint credit levels
- Freshness, completeness, and priority requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Miro documents credits and request capacity, not a per-credit billing price.
- REST levels currently cost 50, 100, 500, or 2,000 credits per call.
- Bulk creation remains charged Level 2 per item, so batching reduces round trips but not necessarily credit total.
- Retired REST webhooks are not an available zero-polling substitute.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Attribute calls and credits to tenants, features, endpoints, schedules, retries, and operators.
2. Separate required freshness from inherited polling frequency and duplicate consumers.
3. Model options: narrower scope, cursor checkpoints, deduplication, cache, coalescing, or reduced cadence.
4. Estimate credit reduction and quantify freshness, completeness, memory, and operational tradeoffs.
5. Test the selected policy against representative change bursts and full-reconciliation recovery.
6. Roll out with per-tenant fairness and alerts for credits, staleness, backlog, and missed-state indicators.

## Approval Boundaries

Do not represent credits as direct monetary savings or weaken contractual freshness/completeness without product and service-owner approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return baseline credits, waste sources, options, selected policy, expected reduction, SLO tradeoffs, test results, and rollback threshold. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| No operation-level telemetry | Instrument before claiming savings. |
| Savings depend on retired webhooks | Reject that option. |
| Cache invalidation is unproved | Limit cache scope/TTL and retain reconciliation. |
| One tenant monopolizes budget | Enforce per-tenant queues and priority reserves. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
baseline=74000cr/min; duplicates=18%; selected=cursor+dedupe; forecast=51000cr/min; freshness=5m; completeness=daily-reconcile
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Rate limits](https://developers.miro.com/reference/rate-limiting)
- [Webhooks removal](https://developers.miro.com/changelog/removed-experimental-webhooks-support)
