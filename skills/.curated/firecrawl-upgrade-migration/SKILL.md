---
name: firecrawl-upgrade-migration
description: >-
  Upgrade a Firecrawl client from legacy v0/v1 routes and methods to the current v2 SDK and API with contract, parity, and rollback evidence. Use when modernizing an existing Firecrawl integration. Trigger with "upgrade Firecrawl", "migrate Firecrawl v1 to v2", or "replace scrapeUrl".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <current-version>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, upgrade, migration]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl v1-to-v2 Upgrade

## Overview

Treat the version change as a behavior migration, not a search-and-replace. Inventory method, option, response, cache, extraction, pagination, and billing differences before switching traffic.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

The current top-level SDK defaults to v2. Key mappings include scrapeUrl to scrape, crawlUrl to crawl, asyncCrawlUrl to startCrawl, checkCrawlStatus to getCrawlStatus, mapUrl to map, batchScrapeUrls to batchScrape, asyncBatchScrapeUrls to startBatchScrape, and checkBatchScrapeStatus to getBatchScrapeStatus. The legacy extract format became a json format object; v2 cache defaults and option shapes also changed.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Pin the current dependency, routes, methods, options, response assumptions, fixtures, usage, and rollback release. Identify intentional feature-frozen v1 callers.
2. Read current migration, SDK, endpoint, billing, and error references; build a per-call mapping including renamed, removed, defaulted, and behavior-changing fields.
3. Add golden synthetic tests for requests, direct SDK versus REST responses, metadata fields, origin status, JSON extraction, crawl/batch jobs, pagination, errors, and cost-sensitive options.
4. Introduce a typed v2 adapter behind a feature flag. Keep v1 compatibility isolated and do not silently fall back from v2 on failure.
5. Run offline contract tests, then shadow approved canaries with content hashes, schema coverage, latency, cache state, and credits rather than raw body diffs.
6. Shift traffic gradually, monitor errors, partial results, quality, freshness, queue, and spend, and exercise rollback before removing the flag.
7. After the observation window, remove legacy packages/routes/secrets, update docs/fixtures, and verify no v0/v1 strings remain except migration evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before changing the SDK major, accepting changed cache/retention behavior, increasing credits, switching production traffic, or removing the legacy rollback path.

## Output

Return the exact before/after package and API surface, mapping table, changed defaults/options, parity tests, canary metrics, rollout state, rollback evidence, and cleanup results.

## Error Handling

- No documented mapping exists: keep the old path and resolve against source/types.
- v2 output or cost is materially different: stop rollout and decide whether to adapt requirements.
- Fallback masks v2 failures: remove automatic fallback and make the version decision observable.

## Examples

- "Replace scrapeUrl" also verifies options and returned document shape.
- "Upgrade the package and hope" is replaced with mapping, shadow parity, staged traffic, and rollback.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
