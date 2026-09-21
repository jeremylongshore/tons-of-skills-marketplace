---
name: firecrawl-advanced-troubleshooting
description: >-
  Isolate difficult Firecrawl v2 failures by separating caller, authentication, request, queue, rendering, origin, and result-processing evidence. Use when routine fixes fail or results are empty, partial, slow, or inconsistent. Trigger with "debug Firecrawl deeply", "empty Firecrawl result", or "stuck Firecrawl job".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <failing-operation-or-job-id>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, troubleshooting, operations]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Layered Troubleshooting

## Overview

Diagnose a failing integration without leaking API keys or scraped content. Change one variable at a time and distinguish Firecrawl transport failures from target-site behavior and downstream parsing defects.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Treat the v2 endpoint reference and the installed SDK types as the contract. SDK calls return the data object directly, REST errors normally return success false plus an error string, and completed crawl or batch results may require pagination. Use metadata.statusCode to distinguish a captured origin error page from a Firecrawl request failure.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Record the client package, resolved version, runtime, endpoint family, request class, opaque request or job ID, and first failing timestamp. Redact URLs when their paths or queries are sensitive.
2. Reproduce with one approved public or synthetic URL and the smallest output format. If that succeeds, the credential and base route are probably sound; do not infer that the target is healthy.
3. Compare the failing request with the current v2 schema. Remove optional actions, headers, proxy choices, JSON extraction, and cache overrides one at a time.
4. For async work, inspect queue status, job state, pagination cursor, crawl errors, and terminal status. Do not call a running job failed only because the first status page has no documents.
5. Classify the result as request validation, authentication, credits, rate/concurrency, rendering, origin response, extraction/schema, retention-policy conflict, or downstream processing.
6. Retry only statuses marked retryable by the official error catalog. Honor Retry-After when present, use bounded jittered backoff, and retain the original idempotency decision.
7. Reintroduce options individually, verify the smallest fix on a canary, and produce a redacted evidence receipt before rollout.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before testing a private or authenticated target, changing proxy or location policy, increasing a crawl limit, weakening retention controls, rotating a key, or sending evidence to Firecrawl support.

## Output

Return a layer-by-layer diagnosis, minimal reproducer, retry classification, redacted evidence, confirmed root cause or remaining hypotheses, proposed fix, canary result, and rollback condition.

## Error Handling

- No reproducible failure: preserve the evidence and add targeted telemetry instead of guessing.
- Origin returns 403 or 404 as a document: stop automatic retries and review target authorization and policy.
- Evidence would expose content or credentials: replace it with hashes, sizes, statuses, and opaque IDs.

## Examples

- "The crawl is stuck" inspects job state, queue pressure, pagination, and crawl errors before changing code.
- "Markdown is empty" compares a minimal scrape, metadata.statusCode, rendering options, and downstream filters.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
