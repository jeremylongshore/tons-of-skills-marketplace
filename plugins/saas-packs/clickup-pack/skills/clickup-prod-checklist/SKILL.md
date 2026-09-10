---
name: clickup-prod-checklist
description: >-
  Issue an evidence-backed go or no-go decision for a ClickUp integration across auth, versions, plans, data, limits, webhooks, recovery, and ownership. Use when reviewing a production launch or major change. Trigger with "ClickUp production checklist", "ClickUp go-live", or "review ClickUp release".
argument-hint: "[release-ref] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- production-readiness
model: inherit
effort: high
compatibility: Designed for Claude Code; approval requires service, Workspace, security, and data owners
---
# ClickUp Production Readiness Review

## Overview

Turn launch readiness into verifiable controls and named blockers rather than a generic checkbox list.

## Prerequisites

- A release candidate, endpoint/version inventory, Workspace/environment matrix, and rollback artifact
- Current plan/feature facts, auth ownership, data policy, SLOs, and incident runbook
- Offline and bounded live test receipts

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- v2/v3 routes are reviewed individually; auth and plan success in one endpoint does not prove another.
- Rate behavior is tested using per-token headers and bounded retry policy.
- Webhook readiness includes HTTPS, raw-body HMAC, idempotency, queue durability, health monitoring, and reconciliation.
- No launch is approved with unresolved cross-Workspace writes or secret/content leakage.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Verify artifact provenance, dependency locks, endpoint versions, schema fixtures, and rollback.
2. Verify personal/OAuth ownership, redirect/state controls, secret injection, rotation, and Workspace guards.
3. Review data minimization, logging, retention, deletion, backup, and incident access.
4. Exercise rate, pagination, timeout, 5xx, webhook retry/suspension, queue replay, and partial-write paths.
5. Run a bounded read-only live probe and any separately approved synthetic canary.
6. Record PASS/FAIL/NA evidence, owners, expiry dates, blockers, and final decision.

## Approval Boundaries

The skill may recommend but not self-approve launch, paid plan changes, production writes, ACL changes, or acceptance of a security/data exception.

## Output

Return go/no-go, control results with evidence, blocker owners/dates, canary result, rollback target, and approval record.

## Error Handling

| Condition | Response |
|---|---|
| Required owner is absent | Return no-go. |
| Evidence is stale or environment-mismatched | Re-run the control; do not reuse it. |
| Rollback is untested | Return no-go for write-bearing release. |
| Live probe leaks content | Stop launch and remediate. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
release=2026.09.10; controls=31-pass/2-fail/3-na; live-read=pass; writes=0; decision=no-go
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Get started](https://developer.clickup.com/docs/Getting%20Started)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
