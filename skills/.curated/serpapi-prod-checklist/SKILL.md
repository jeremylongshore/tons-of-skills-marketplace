---
name: serpapi-prod-checklist
description: 'Issue an evidence-backed production-readiness decision for a SerpAPI integration across contract, security, reliability, cost, privacy, and operations. Use when preparing a launch or material change. Trigger with "review SerpAPI production readiness".'
argument-hint: "[service] [environment] [release-ref]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, production, readiness, governance]
model: inherit
effort: high
compatibility: Designed for Claude Code; this skill audits and prepares a decision but does not authorize production changes
---
# SerpAPI Production Readiness Review

## Overview

Fail closed on missing evidence and distinguish deterministic fixture confidence from the separately approved live canary.

## Prerequisites

- Immutable release reference, service owner, deployment plan, rollback target, and decision deadline
- Current SerpAPI documentation and Account API capacity evidence
- Test, security, privacy, reliability, cost, and operational receipts

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to verify repository and deployment evidence, `WebFetch` to re-check current vendor contracts, and `Write` or `Edit` only for the readiness record and redacted remediation evidence.

## Current Contract

Search behavior varies by engine and optional result sections; 429 can mean throughput or allowance exhaustion; standard records have documented retention while ZeroTrace changes storage and debugging behavior. Production readiness therefore depends on the selected engine, account, data class, and gateway—not a generic SDK smoke test.

## Authentication

Require server-side `SERPAPI_KEY`, an approved secret lifecycle, authenticated gateway callers, and proof that credentials and key-bearing URLs are absent from artifacts, logs, fixtures, and client bundles.

## Instructions

1. Pin the release SHA and verify dependency, schema, formatting, lint, unit, fixture, integration, security, and deployment gates.
2. Confirm engine-specific parameter allowlists, normalized optional schemas, bounded pagination, timeouts, and retry classifications.
3. Verify secret isolation, caller authorization, abuse controls, redaction, data purpose, cache/log retention, and ZeroTrace decision.
4. Compare forecast demand and concurrency with current Account API searches left and hourly throughput; reserve incident headroom.
5. Prove metrics, alerts, runbooks, support escalation, search-ID correlation, incident response, key rotation, and rollback.
6. Run preview failure paths and an explicitly approved one-search canary; reconcile result status, latency, and capacity.
7. Record PASS, CONDITIONAL, or FAIL with evidence per control, named exceptions, expiry dates, approvers, and rollback trigger.

## Approval Boundaries

This review does not grant deployment, secret, plan, retention, or live-search authority. Every mutation follows the owning system's approval process.

## Output

Return the pinned release, control matrix, evidence links, live-canary receipt, capacity snapshot, exceptions and expiries, decision, approvers, and rollback trigger.

## Error Handling

| Condition | Response |
|---|---|
| Required evidence is stale or missing | Mark the control failed; do not infer readiness. |
| Canary cannot run safely | Record the limitation and keep the launch blocked or explicitly conditional. |
| Capacity has insufficient headroom | Reduce demand or obtain an approved account change before launch. |
| Rollback is untested | Fail production readiness. |

## Example

```text
release=sha256:...; deterministic_gates=pass; secret_flow=pass; capacity=headroom-confirmed; canary=pass; rollback=pass; decision=PASS; approvals=recorded
```

## Resources

- [Account API](https://serpapi.com/account-api)
- [Status and error codes](https://serpapi.com/api-status-and-error-codes)
- [SerpAPI security](https://serpapi.com/security)

## Next Steps

Attach the signed decision to the release and schedule review of every time-bounded exception.
