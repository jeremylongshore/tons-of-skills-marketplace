---
name: together-prod-checklist
description: >-
  Review a Together AI production release across model policy, auth, data controls, dynamic limits, retries, observability, cost, deprecations, asynchronous recovery, and rollback. Use when reviewing go-live or a material model change. Trigger with "Together production checklist", "Together go live", or "Together readiness review".
argument-hint: "[repository-path] [environment] [model-or-endpoint]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- production-readiness
model: inherit
effort: high
compatibility: Designed for Claude Code; verification may require deployment, telemetry, billing, and Together project access
---
# Together AI Production Checklist

## Overview

This skill produces a release decision backed by current provider, application, security, reliability, quality, and cost evidence.

## Prerequisites

- A pinned release artifact and environment configuration
- Model/endpoint quality, latency, availability, and cost thresholds
- Secret, data handling, monitoring, incident, and rollback owners
- Current Together model, limit, pricing, and deprecation evidence

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect configuration, model policy, retry logic, tests, and runbooks. Use `WebFetch` for current Together contracts. Use `Write` or `Edit` only for approved remediation or the release record.

## Current Contract

- Resolve model IDs and deprecation status at review time; do not trust an old README.
- Read dynamic limit headers and bound concurrency, tokens, retries, and queues.
- Separate serverless, batch, fine-tuning, and dedicated failure/recovery paths.
- Dedicated replicas require explicit cost shutdown; batches require output/error reconciliation.

## Authentication

Verify environment-specific project keys, secret-manager injection, rotation/revocation, fork isolation, and log redaction. Never prove readiness by displaying a credential or authorization header.

## Instructions

1. Pin artifact, SDK major, configuration, model policy, and environment identity.
2. Verify authentication, data classification, redaction, retention, and tenant isolation.
3. Run offline tests and a bounded live canary for response shape, latency, quality, usage, and limits.
4. Exercise `401`, `402`, `404`, `429`, `503`, timeout, partial batch, and model-deprecation paths.
5. Reconcile spend forecasts with billing analytics and confirm alerts and dedicated teardown.
6. Execute rollback/degradation evidence, assign all exceptions, and issue go, conditional-go, or no-go.

## Approval Boundaries

Do not waive a failed security, quality, cost, or recovery control. Conditional approval must name the owner, deadline, monitoring, and rollback trigger.

## Output

Return a control-by-control evidence matrix, exceptions, owners, current-provider snapshot, rollback result, cost state, and release verdict.

## Error Handling

| Condition | Response |
|---|---|
| Model is deprecated or redirected | Re-evaluate behavior and migrate before go-live. |
| Live probe cannot run | Do not report it passed; issue an explicit exception or no-go. |
| Cost/usage is unreconciled | Block capacity changes and assign the billing owner. |
| Rollback fails | No-go until a recoverable path is proven. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
artifact=pinned; auth=pass; model=current; limits=measured; rollback=pass; verdict=go
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Deprecations](https://docs.together.ai/docs/deprecations)
- [Dynamic rate limits](https://docs.together.ai/docs/serverless/rate-limits)
- [Error codes](https://docs.together.ai/docs/error-codes)
