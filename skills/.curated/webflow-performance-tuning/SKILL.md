---
name: webflow-performance-tuning
description: >-
  Improve Webflow integration latency and throughput with measured pagination, caching, Content Delivery, and bounded concurrency. Use when reads are slow, syncs are bursty, or origin budgets are tight. Trigger with "speed up Webflow", "Webflow CDN", or "optimize Webflow API".
argument-hint: "[project-path] [endpoint-or-workload]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- performance
- caching
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Integration Performance

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- The Content Delivery API mirrors only documented read-only live-item endpoints at `api-cdn.webflow.com`; it is not a write or staged-content API.
- Cache TTL is currently 120 seconds for Enterprise plans and 300 seconds for other plans.
- `cf-cache-status` distinguishes HIT from MISS or BYPASS. Only cached responses effectively avoid plan rate limits; origin requests count.
- Data API pagination and bulk limits are endpoint-specific. Read the exact endpoint rather than assuming one universal batch size.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Measure endpoint, p50/p95 latency, payload size, pages, cache status, rate headers, worker concurrency, and freshness needs.
2. Route eligible published-item reads to Content Delivery with a dedicated read-only token and preserve Data API for fresh or staged data.
3. Cache only data with an explicit freshness budget; include site, collection, locale, query, and API surface in cache keys.
4. Bound pagination and concurrency below the observed per-key budget. Avoid fetching full collections when a delta or webhook can drive work.
5. Use supported bulk endpoints after validating their exact item limit and partial-failure behavior.
6. Load-test against fixtures or a non-production site and report latency, origin request reduction, staleness, and error rates.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Stale live content | Check documented CDN TTL and `cf-cache-status`; use Data API only when freshness requires it. |
| Origin budget exhausted | Reduce cold-key fanout, stagger requests, and coordinate workers sharing the token. |
| Partial bulk failure | Reconcile item receipts and retry only failed records. |

## Examples

For a public content service, use Content Delivery for published items, key caches by collection and locale, log cache status, accept the documented freshness window, and retain Data API for editorial previews.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
