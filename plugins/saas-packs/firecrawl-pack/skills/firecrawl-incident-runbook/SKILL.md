---
name: firecrawl-incident-runbook
description: >-
  Analyze and mitigate Firecrawl integration incidents involving outage, credits, throttling, policy denial, job failure, webhook loss, or unsafe content. Use when responding to active production impact. Trigger with "Firecrawl incident", "Firecrawl outage", or "Firecrawl crawl failure".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<incident-id> <severity>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, incident-response, operations]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Incident Response

## Overview

Stabilize the affected workflow, preserve privacy-safe evidence, and restore service through a tested degraded mode or rollback. Separate Firecrawl service health, target-origin behavior, and internal pipeline failures.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Firecrawl's error catalog defines retryability; async operations expose job/status/cancellation surfaces; queue status helps distinguish capacity pressure; status polling remains the recovery path when webhooks are delayed or exhausted. A crawl webhook set does not include a crawl.failed event in the current documented event list.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Declare incident owner, severity, affected operation/environment, start time, customer impact, data risk, approved communication channel, and next update time.
2. Pause or bound producers before investigating if retries, crawl scope, or pay-as-you-go could amplify cost or target load.
3. Check internal deployments and dependencies, Firecrawl service evidence, credentials, credits, team restrictions, queue/concurrency, job state, webhook delivery, and target-origin status.
4. Classify the failure with the official error catalog. Retry only documented retryable classes, honor Retry-After, and cap attempts.
5. Choose a reversible mitigation: reduce concurrency, narrow limits, switch to polling, serve last known approved content, disable an expensive option, or roll back the application release.
6. Verify recovery with a synthetic or approved canary and confirm queue drain, error rate, output quality, data integrity, and spend stabilization.
7. Communicate resolution, retain redacted evidence, and create owned corrective actions for detection, prevention, runbook, and rollback gaps.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require incident-command approval before key rotation, plan or pay-as-you-go changes, traffic failover, target-scope changes, disabling security/retention controls, or vendor disclosure.

## Output

Return the timeline, impact, classification, mitigations, approvals, canary and recovery evidence, residual risk, next update, and post-incident actions.

## Error Handling

- Service state is ambiguous: hold producers and collect bounded evidence rather than mass retrying.
- Mitigation changes data quality or freshness: label degraded output and obtain product-owner acceptance.
- Potential credential or content exposure: invoke the security incident path and preserve evidence without broad collection.

## Examples

- "Crawls stopped completing" checks deployment, queue, job status, errors, and target status before retrying.
- "Webhooks stopped" switches to bounded status polling while signature and delivery failures are investigated.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
