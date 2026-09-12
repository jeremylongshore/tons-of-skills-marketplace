---
name: firecrawl-hello-world
description: >-
  Create the smallest current Firecrawl v2 scrape and verify its provenance, origin status, and output without leaking credentials. Use when testing a new installation. Trigger with "Firecrawl hello world", "first Firecrawl scrape", or "verify Firecrawl setup".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<approved-url> [node|python|curl]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, quickstart, verification]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl v2 First Verified Scrape

## Overview

Prove one controlled page can be retrieved through the current v2 surface. A successful transport is not enough: verify the document came from the expected URL and did not capture an origin error page.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

For Node, install firecrawl, import the named Firecrawl client, and call scrape. For Python, install firecrawl-py, import Firecrawl, and call scrape. REST uses POST https://api.firecrawl.dev/v2/scrape with Bearer authentication. The SDK returns the document data directly; REST wraps it in success and data.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Choose an approved public or synthetic URL with stable, non-sensitive content and record the expected title or marker.
2. Install the official SDK with the repository's locked package manager, or use REST. Record the resolved package version without changing unrelated dependencies.
3. Inject FIRECRAWL_API_KEY from the secret manager for authenticated use. Keyless evaluation is allowed only for the operations and limits currently documented.
4. Request markdown only and avoid actions, custom headers, screenshots, raw HTML, location, proxy overrides, and retention changes in the first test.
5. Assert the expected metadata.sourceURL, a successful metadata.statusCode, non-empty markdown, and the expected marker. Do not print the full body.
6. Record latency, cacheState and creditsUsed when returned, SDK/API surface, and redacted result size.
7. Remove temporary output, keep the minimal test as a synthetic smoke if useful, and document the next approved workflow.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before using a private URL, supplying site credentials or headers, retaining the response, or turning the example into a recurring job.

## Output

Return the exact install/runtime surface, approved URL classification, assertion results, content-free metrics, auth mode, and a concise pass/fail receipt.

## Error Handling

- 401: verify secret injection without printing the key.
- A returned document has origin status 403 or 404: fail the content assertion and review authorization or target behavior.
- Output marker is absent: do not widen options blindly; inspect current scrape guidance and target behavior.

## Examples

- "Verify Node setup" checks the firecrawl package and one markdown scrape with content-free assertions.
- "Use my customer portal for the demo" is blocked until target authorization and data handling are approved.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
