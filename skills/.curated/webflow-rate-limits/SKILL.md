---
name: webflow-rate-limits
description: >-
  Design Webflow request budgets, queues, and retries from current plan and endpoint limits. Use when handling 429s, bulk sync throughput, polling, or Content Delivery caching. Trigger with "Webflow rate limit", "Webflow 429", or "throttle Webflow".
argument-hint: "[project-path] [site-plan] [endpoint]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- rate-limits
- reliability
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Rate-Limit Engineering

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Current general Data API budgets are 60 requests/minute for Starter and Basic, 120 for CMS, Ecommerce, and Business, and custom for Enterprise.
- Limits apply per API key. `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After` expose the active budget.
- Site Publish is limited to one successful publish per minute; other endpoint-specific limits belong to their endpoint pages.
- Cached Content Delivery responses effectively avoid plan limits, but a `MISS` or `BYPASS` reaches origin and counts. Never call the CDN unlimited without that qualifier.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Identify site plan, API keys, worker count, endpoints, request volume, and whether operations are reads, idempotent writes, or publishes.
2. Measure actual headers in a secret-safe client log and distinguish per-key capacity from application-wide concurrency.
3. Set a conservative shared queue below the documented budget and reserve capacity for interactive or recovery work.
4. Honor `Retry-After`; otherwise use exponential backoff with jitter and a bounded attempt/deadline policy.
5. Replace polling with documented webhooks where suitable and use Content Delivery only for supported published-item reads.
6. Load-test against fixtures or a development site, then report sustainable throughput and failure behavior.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| 429 despite local limiter | Find other workers sharing the key and coordinate through a shared budget. |
| CDN MISS/BYPASS | Treat the request as origin traffic and include it in the plan budget. |
| Publish throttled | Serialize publishes and verify prior completion before retrying. |

## Examples

For a CMS-plan sync, budget below 120 requests per minute across all workers sharing the token, batch supported operations, honor `Retry-After`, and route live published-item reads through the CDN with cache-status telemetry.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
