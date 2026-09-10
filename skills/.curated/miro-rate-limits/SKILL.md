---
name: miro-rate-limits
description: "Design and implement repository-side Miro REST traffic controls from credit weights, supplied headers, bounded queues, and reset-aware retries. Use when preventing or recovering from Miro 429 responses. Trigger with \"Miro rate limit\"."
argument-hint: "[traffic-window] [workload]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- rate-limits
- capacity
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Credit-Budget and Rate-Limit Control

## Overview

Plan capacity in credits rather than raw request count and preserve headroom across every caller sharing a user/application quota; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Sanitized rate-limit headers and recent 429 history
- Endpoint inventory with documented credit levels
- Caller priorities, freshness targets, and retry SLO

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary. These declared tools do not call authenticated Miro APIs or deployment CLIs; implement client, configuration, and test changes, then return exact operator commands or an approval-gated handoff for live execution.

## Current Contract

- REST limiting is per user and application with a published global budget of 100,000 credits per minute.
- Level 1 costs 50 credits, Level 2 costs 100, Level 3 costs 500, and Level 4 costs 2,000 per call.
- At the global budget those levels correspond to 2,000, 1,000, 200, and 50 calls per minute respectively when used alone.
- Responses expose `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and Unix-epoch `X-RateLimit-Reset`; published limits are subject to change.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Inventory users/apps, callers, endpoints, weights, bursts, and retry loops.
2. Capture current headers from bounded authorized requests and validate reset conversion.
3. Model each operation in credits, including bulk-create Level 2 cost per item.
4. Allocate priority budgets with explicit interactive and incident-recovery headroom.
5. Queue requests with jitter, a maximum elapsed retry time, and no token sharding to evade limits.
6. Load-test synthetic traffic and verify fairness, queue age, header telemetry, and bounded 429 recovery.

## Approval Boundaries

Do not add installations or identities to multiply quota, request Enterprise capacity, or starve interactive traffic without account and service-owner approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return observed budget/reset, weighted demand, allocations, headroom, queue policy, test results, and 429 recovery evidence. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Headers conflict with assumed limits | Trust the authorized observation and re-check current official docs. |
| Reset is malformed | Stop automatic retry and use conservative review. |
| Queue exceeds freshness SLO | Reduce demand or seek an approved architecture change. |
| Retry storm appears | Open the circuit and drain through one scheduler. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
budget=100000cr/min; demand=62000; reserved=20000; headroom=18%; queue-p95=3.8s; 429=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [REST rate limits](https://developers.miro.com/reference/rate-limiting)
- [Bulk create](https://developers.miro.com/reference/create-items)
