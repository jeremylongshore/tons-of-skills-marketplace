---
name: firecrawl-prod-checklist
description: >-
  Run a release gate for a Firecrawl v2 integration covering contracts, scope, identity, spend, retention, reliability, observability, and rollback. Use when preparing a production launch or major change. Trigger with "Firecrawl production checklist", "launch Firecrawl", or "Firecrawl go-live review".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <release-ref>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, production, release]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Production Readiness Gate

## Overview

Produce evidence for a go/no-go decision. A checked box without an artifact, test, owner, or exact release reference is not evidence.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

The release must use current v2 endpoints or an explicitly isolated legacy path, the official SDK surface, complete async pagination, documented retryability, signed webhooks, explicit crawl/batch limits, current billing controls, and approved cache/retention behavior. Self-hosted releases require their own production controls beyond Compose evaluation.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Pin the application release, dependency/lockfile, Firecrawl contract source, configuration hashes, environment, owners, target policy, and rollback candidate.
2. Verify secret-managed identity, team ownership, key/format/endpoint/IP restrictions where available, rotation, fork-CI isolation, and no secret in source or artifacts.
3. Verify domain authorization, URL canonicalization, explicit scope/limits, allowed formats/actions/headers/proxies, retention/cache/ZDR choices, and deletion.
4. Test SDK/REST response handling, origin status, pagination, cancellation, 402/403/429, Retry-After, bounded server retries, partial results, webhook HMAC/idempotency, and downstream deduplication.
5. Verify cost ceilings, pay-as-you-go policy, queue/concurrency headroom, dashboards, SLO alerts, incident ownership, vendor escalation, and degraded modes.
6. Run one bounded staging canary with approved content-free assertions; then test rollback without replaying or duplicating accepted pages.
7. Issue go only when required gates pass and approvals are attached; record exceptions with owner and expiry.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require named security/data/product/operations approval for their controls and release-owner approval for go-live, plan/spend changes, exceptions, and rollback waivers.

## Output

Return a release scorecard with evidence links, exact versions, gate verdicts, canary and rollback results, exceptions, owners, expiry, and final go/no-go decision.

## Error Handling

- Required evidence is missing: mark the gate failed, not unknown-pass.
- Canary content or spend exceeds policy: stop rollout and execute rollback.
- Rollback duplicates downstream records: keep release blocked until idempotency is repaired.

## Examples

- "Are we ready to launch?" returns evidence-backed gate verdicts and open owners.
- "Ship despite unsigned webhooks" remains no-go until verification or polling-only architecture is approved.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
