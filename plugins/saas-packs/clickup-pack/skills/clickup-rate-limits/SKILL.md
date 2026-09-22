---
name: clickup-rate-limits
description: >-
  Analyze and control ClickUp request concurrency from plan-aware per-token limits, response headers, bounded queues, and reset-based retries. Use when preventing or recovering from ClickUp 429 responses. Trigger with "ClickUp rate limit", "ClickUp 429", or "size ClickUp concurrency".
argument-hint: "[workspace-plan] [traffic-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- rate-limits
model: inherit
effort: high
compatibility: Designed for Claude Code; live analysis requires sanitized ClickUp response headers
---
# ClickUp Rate-Limit Control

## Overview

Size traffic from the token's observed budget and workload rather than hard-coded optimistic concurrency. Preserve headroom for every caller sharing that token.

## Prerequisites

- Sanitized `X-RateLimit-Limit`, `Remaining`, and Unix `Reset` values plus 429 history
- The Workspace plan hosting the token and inventory of all callers sharing it
- Queue, freshness, retry, and priority requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Limits apply per personal or OAuth token and vary by the hosting Workspace plan.
- Current published limits are 100 requests/minute for Free Forever, Unlimited, and Business; 1,000 for Business Plus; 10,000 for Enterprise.
- A 429 response includes `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset`; reset is a Unix timestamp.
- Plan values are ceilings, not target throughput; leave headroom for interactive and recovery traffic.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Inventory tokens, Workspaces, plans, callers, endpoints, request bursts, and retry loops.
2. Capture current headers from bounded calls and convert reset timestamps safely.
3. Allocate budgets by priority and reserve explicit headroom for user and recovery operations.
4. Implement a bounded queue/token bucket with jitter and a maximum elapsed retry time.
5. Pause at 429 until reset; do not fan out retries or switch tokens to bypass policy.
6. Load-test with synthetic work and verify throughput, fairness, queue age, and zero lost operations.

## Approval Boundaries

Do not upgrade a plan, add tokens to multiply limits, or starve interactive traffic without account and service-owner approval.

## Output

Return observed limit/reset, caller inventory, concurrency and queue policy, headroom, test results, 429 rate, and alternatives.

## Error Handling

| Condition | Response |
|---|---|
| Headers conflict with assumed plan | Trust observed authorized headers and re-check account facts. |
| Reset value is malformed | Stop automatic retry and use conservative operator review. |
| Queue exceeds freshness SLO | Reduce demand or choose an approved architecture change. |
| Retry storm detected | Open the circuit and drain under a single scheduler. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
plan=business-plus; observed-limit=1000/min; allocated=720/min; headroom=28%; 429=0; queue-p95=9s
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
