---
name: firecrawl-core-workflow-a
description: >-
  Implement current Firecrawl v2 scrape and crawl flows with bounded discovery, pagination, content validation, and durable receipts. Use when collecting one page or a governed site corpus. Trigger with "Firecrawl scrape", "crawl this site", or "build a Firecrawl corpus".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<url> [scrape|crawl]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, scrape, crawl]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Scrape and Crawl Workflow

## Overview

Use scrape for one URL and crawl for recursive discovery. Keep the authorization basis, scope, cost ceiling, result completeness, and storage decision explicit.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

The current Node client is Firecrawl from the firecrawl package; Python uses Firecrawl from firecrawl-py. Use scrape for a single URL, crawl as the waiter, startCrawl for asynchronous submission, getCrawlStatus for status and pagination, and cancelCrawl for cancellation. REST uses the /v2 routes and Bearer authentication.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Confirm the target is authorized, normalize its origin, and document allowed paths, excluded paths, subdomain/external-link policy, desired formats, and freshness.
2. Create the client from FIRECRAWL_API_KEY for authenticated work. Keep the key in a secret manager and never place it in source, arguments, logs, or generated examples.
3. For one page, call scrape with only the required formats and options. Validate the returned document, metadata.sourceURL, metadata.statusCode, and required content fields.
4. For a site, set an explicit crawl limit and path/depth policy. Use crawl when blocking is acceptable or startCrawl when another worker owns status and cancellation.
5. Retrieve every required result page. Preserve the next cursor or URL until pagination is complete, and record partial completion separately from terminal success.
6. Deduplicate by canonical source URL and content hash, validate output quality, and write only approved fields to the downstream store.
7. Emit counts, creditsUsed when returned, cache state, failures, policy version, and rollback/cancellation outcome without logging page bodies.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before authenticated-page scraping, external-link traversal, increasing scope or limit, enabling sensitive headers/actions, or retaining raw HTML, screenshots, or personal data.

## Output

Return normalized scope, endpoint and SDK method, job ID where applicable, pagination completion, accepted/rejected counts, content-quality checks, retention decision, and a redacted run receipt.

## Error Handling

- Captured origin error page: quarantine by metadata.statusCode and do not index it as successful content.
- Async job exceeds its deadline: cancel when safe, persist the cursor and receipt, and require an explicit resume decision.
- Output fails schema or quality checks: retain only permitted evidence and route the page to review.

## Examples

- "Scrape this release note" selects one v2 scrape and validates the returned document.
- "Crawl our docs" requires path rules, an explicit limit, pagination ownership, and a cancellation plan.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
