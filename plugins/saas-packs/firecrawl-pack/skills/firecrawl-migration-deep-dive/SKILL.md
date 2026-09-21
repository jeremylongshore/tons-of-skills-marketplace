---
name: firecrawl-migration-deep-dive
description: >-
  Migrate a custom Puppeteer, Playwright, Cheerio, or third-party scraping workload to Firecrawl v2 with parity, policy, cost, and rollback evidence. Use when replacing an existing acquisition system. Trigger with "migrate to Firecrawl", "replace Playwright scraping", or "Firecrawl adoption".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <legacy-adapter>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, migration, architecture]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Workload Migration

## Overview

Replace a scraper only after defining observable equivalence. Preserve the old adapter until the new path meets content, policy, performance, and recovery gates.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Firecrawl can replace rendering, crawl discovery, mapping, search, parsing, and typed extraction, but one endpoint is not equivalent to every legacy workflow. Scrape, crawl, map, batch, parse, JSON extraction, actions, Browser, and Cloud/self-hosted capabilities have different contracts and costs.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Inventory legacy sources, login/session behavior, selectors/actions, discovery rules, formats, parsers, retries, proxies, schedules, storage, compliance controls, metrics, and operating cost.
2. Create a source-to-Firecrawl capability map. Mark unsupported, Cloud-only, self-host-dependent, behavior-changing, and policy-sensitive requirements.
3. Define an adapter contract and golden synthetic corpus with provenance, normalized content hashes, required-field coverage, latency, cost, and accepted variance.
4. Implement the smallest v2 path behind a feature flag. Keep target authorization, explicit scope/limits, cache/retention, cancellation, and error typing visible.
5. Shadow both paths on approved canaries, compare content and metadata without duplicating downstream writes, and investigate meaningful differences.
6. Shift traffic in stages only after parity, security, spend, load, and rollback gates pass. Keep the old path available through the observation window.
7. Remove legacy code and secrets only after rollback expiry, archive the decision and evidence, and verify dependency and data cleanup.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before replaying authenticated sessions, changing target behavior or proxies, enabling Cloud-only processing, increasing spend, shifting traffic, or deleting the legacy path.

## Output

Return the capability matrix, parity definition, adapter design, golden corpus, shadow results, cost and risk comparison, staged rollout, rollback evidence, and deferred gaps.

## Error Handling

- Required behavior has no Firecrawl equivalent: retain that legacy component or redesign explicitly.
- Shadow outputs contain sensitive differences: quarantine the comparison and use content-free metrics.
- Parity cannot be measured: block migration rather than accepting visual inspection alone.

## Examples

- "Replace our docs crawler" maps discovery, rendering, filters, retries, and indexing before shadowing.
- "Delete Playwright first" is rejected until Firecrawl parity and rollback are proven.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
