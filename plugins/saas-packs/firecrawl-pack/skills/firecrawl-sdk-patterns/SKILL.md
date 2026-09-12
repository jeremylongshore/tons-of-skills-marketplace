---
name: firecrawl-sdk-patterns
description: >-
  Build a typed, testable Firecrawl v2 adapter for Node or Python with current methods, explicit options, errors, pagination, and dependency control. Use when implementing reusable client code. Trigger with "Firecrawl SDK patterns", "wrap Firecrawl", or "typed Firecrawl client".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> [node|python]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, sdk, architecture]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl v2 SDK Boundary

## Overview

Keep Firecrawl behind a narrow application-owned interface so provider changes, policy, retries, and tests do not leak across the codebase.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Node uses the named Firecrawl client from the firecrawl install surface; Python uses Firecrawl from firecrawl-py. Current top-level v2 methods include scrape, crawl, startCrawl, getCrawlStatus, map, batchScrape, startBatchScrape, getBatchScrapeStatus, search, parse, and agent surfaces. Feature-frozen v1 lives behind a separate compatibility boundary.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Inspect the runtime, official package and resolved version, compiler settings, existing HTTP/client layer, and exact operations required.
2. Define application request/result types containing only approved fields, explicit scope/limits, provenance, origin status, terminal state, and pagination metadata.
3. Construct one client per process boundary from validated configuration; inject it into services and tests rather than creating clients inside business logic.
4. Map provider documents and errors into a discriminated result model. Keep API failures, captured origin errors, validation rejection, partial results, and cancellation distinct.
5. Expose waiter methods only where blocking fits the deadline; otherwise expose submit/status/cancel and durable pagination through an owned job service.
6. Centralize bounded retry, policy, redaction, metrics, and version reporting. Do not erase SDK types with any or dictionary-shaped pass-throughs.
7. Add synthetic contract tests, pin the dependency through the lockfile, and document the reviewed upgrade and rollback process.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before adding/upgrading the SDK, exposing a new Firecrawl operation, relaxing types, changing retry policy, or accepting a provider response directly in domain code.

## Output

Return the adapter interface, current package/source/version, method mapping, configuration contract, error and pagination model, policy hooks, tests, and upgrade rollback.

## Error Handling

- Docs and installed types disagree: pin evidence and resolve before coding.
- Required result field is absent: return a typed partial/failure state rather than a fabricated default.
- Legacy and v2 methods are mixed: isolate legacy compatibility and create a migration plan.

## Examples

- "Create a Firecrawl service" yields a narrow typed adapter with injected client and synthetic tests.
- "Return the SDK object everywhere" is rejected because it couples domain code to provider drift.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
