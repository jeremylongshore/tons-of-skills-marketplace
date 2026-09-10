---
name: salesloft-prod-checklist
description: >-
  Produce a release-bound go or no-go decision for a Salesloft integration using auth, contract, data, rate, webhook, monitoring, rollback, and ownership evidence. Use when preparing to enable production traffic. Trigger with "Salesloft production checklist", "Salesloft go live", or "Salesloft release readiness".
argument-hint: "[repository-path] [release-sha]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- production-readiness
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Production Go-No-Go

## Overview

This skill binds production readiness to one release SHA and target environment. A checked box without evidence is not a passing gate.

## Prerequisites

- Immutable release SHA and deployment target
- Named Salesloft team, integration owner, and rollback owner
- Passing fixture, contract, security, and failure-path tests
- Approved auth, data retention, monitoring, and incident policies

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect release artifacts, tests, configuration, and runbooks. Use `WebFetch` only to reverify official Salesloft contracts. Use `Write` or `Edit` only for the approved release record or required fix.

## Current Contract

- Authentication flow must match partner, customer, or private-app use and use least-privilege scopes.
- Request and response types must preserve documented envelope and endpoint-specific content types.
- Rate control must be team-wide and use the current endpoint-cost and remaining-minute headers.
- Webhook verification uses raw-body SHA-1 HMAC plus callback-token validation and durable deduplication.
- CRM writes require target, payload, read-after-write, and reconciliation evidence.

## Authentication

Prove production credential availability and rotation without displaying secret values. Confirm callback URIs, team binding, scopes, and acting-user permissions.

## Instructions

1. Pin SHA, environment, Salesloft team, owners, and change window.
2. Attach test results for envelope, pagination, auth, rate, webhook, and failure contracts.
3. Verify secret references, tenant isolation, logging redaction, and rotation drill.
4. Run a bounded read-only identity smoke check against the production team.
5. Validate dashboards for latency, status, endpoint cost, remaining budget, queue lag, and reconciliation.
6. Rehearse rollback or disablement and confirm data-repair ownership.
7. Record PASS, FAIL, or WAIVED per gate and issue a final go/no-go decision.

## Approval Boundaries

Do not approve a release with an unowned failure, expired exception, missing rollback, or unverified production team. A canary write requires separate payload approval.

## Output

Return release SHA, target, gate table, evidence links, exceptions and expiry, rollback proof, owners, and final decision.

## Error Handling

| Condition | Response |
|---|---|
| Evidence is not SHA-bound | Rerun it on the release candidate. |
| Production team mismatch | Stop the rollout and repair credential mapping. |
| Rate headroom absent | Reduce canary traffic before proceeding. |
| Rollback fails | No-go until disablement and repair are proven. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
release=a1b2c3d; gates=12/12; exceptions=0; rollback=pass; decision=GO
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API basics](https://developers.salesloft.com/docs/platform/api-basics/)
- [Salesloft API Logs](https://developers.salesloft.com/docs/platform/guides/api-logs/)
