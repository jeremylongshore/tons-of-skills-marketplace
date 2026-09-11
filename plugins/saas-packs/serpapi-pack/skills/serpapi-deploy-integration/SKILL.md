---
name: serpapi-deploy-integration
description: 'Deploy a server-side SerpAPI gateway with secret isolation, input policy, capacity controls, canary evidence, and rollback. Use when promoting a search integration. Trigger with "deploy a SerpAPI gateway".'
argument-hint: "[platform] [environment] [route]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, deployment, gateway, canary]
model: inherit
effort: high
compatibility: Designed for Claude Code; deployment, secret, routing, and production search changes require explicit platform and account-owner approval
---
# SerpAPI Gateway Deployment

## Overview

Promote a narrow backend gateway through preview, canary, reconciliation, and rollback without exposing the SerpAPI key or an open search proxy.

## Prerequisites

- A fixture-tested gateway, deployment owner, route, caller identity, and rollback target
- Approved secret manager, data classification, SLO, capacity budget, and observability
- Platform-specific release and health-check conventions

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect application and infrastructure changes, `WebFetch` to verify current SerpAPI contracts, and `Write` or `Edit` for deployment configuration, policies, probes, tests, and redacted receipts.

## Current Contract

SerpAPI search calls require a private key and engine-specific parameters. Account capacity is discoverable through Account API. Public browser clients should call an authenticated application backend rather than SerpAPI directly.

## Authentication

Inject `SERPAPI_KEY` from the target platform's server-side secret store. Authenticate gateway callers separately, validate their authorization to the requested use case, and never return vendor account or credential data.

## Instructions

1. Review the deploy diff, dependency lock, secret references, route exposure, caller authentication, input allowlist, output projection, and data retention.
2. Define readiness without a billable search; expose only internal health and configuration status, not Account API details.
3. Set finite client and request timeouts, concurrency/admission limits, cache policy, retry budget, and maximum pagination.
4. Deploy to an isolated preview with no production key and run fixture, authorization, abuse, redaction, and rollback tests.
5. Present the production mutation, live-search budget, monitoring, owner, and exact rollback command for approval.
6. Deploy a small canary, execute one approved harmless search, and reconcile status, search ID, latency, errors, and capacity.
7. Promote gradually only while SLO, correctness, privacy, and allowance thresholds hold; otherwise roll back immediately.

## Approval Boundaries

Do not create or change a production secret, public route, caller policy, traffic allocation, or live canary without named approval.

## Output

Return the deploy diff, access and secret model, preview tests, canary receipt, capacity and SLO evidence, promotion decision, rollback proof, and owners.

## Error Handling

| Condition | Response |
|---|---|
| Key appears in client assets | Block and rotate under incident procedure. |
| Gateway accepts arbitrary parameters | Fail the release and enforce a use-case allowlist. |
| Canary breaches errors, latency, or capacity | Roll back and preserve redacted search IDs. |
| Health endpoint leaks account facts | Remove the fields before exposure. |

## Example

```text
environment=production; callers=authenticated; key=server-secret; preview=pass; canary_searches=1; capacity=healthy; promotion=approved; rollback=verified
```

## Resources

- [SerpAPI error guide for web applications](https://serpapi.com/blog/fix-serpapi-errors-guide/)
- [Account API](https://serpapi.com/account-api)
- [SerpAPI security](https://serpapi.com/security)

## Next Steps

Observe a complete workload cycle and rehearse rollback and key rotation with the owning teams.
