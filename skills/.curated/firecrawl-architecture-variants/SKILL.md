---
name: firecrawl-architecture-variants
description: >-
  Select a Firecrawl v2 architecture for interactive scrape, governed batch, scheduled crawl, search enrichment, or self-hosted processing. Use when designing or reviewing a Firecrawl system. Trigger with "Firecrawl architecture", "design a crawl pipeline", or "cloud versus self-hosted Firecrawl".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workload-and-slo>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, architecture, design]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Architecture Selection

## Overview

Turn workload, freshness, compliance, throughput, and recovery requirements into an explicit architecture decision. Prefer the smallest Firecrawl surface that meets the outcome.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Scrape is a synchronous single-resource primitive; crawl and batch scrape support asynchronous jobs, pagination, webhooks, and status retrieval; map discovers URLs without retrieving page content; search discovers external sources; parse handles local file bytes. The default self-hosted Compose stack does not provide every Cloud capability and is not a production security design.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Inventory the source domains, ownership or authorization basis, expected page volume, freshness target, output formats, data classification, and recovery objective.
2. Choose scrape for bounded single pages, map plus selective scrape for curated URL sets, batch scrape for known URL collections, and crawl for recursive site discovery.
3. Choose polling, WebSocket streaming, or signed webhooks for asynchronous delivery based on network topology and recovery needs.
4. Decide Cloud versus self-hosting using required capabilities, data flows, operator staffing, availability target, and upgrade ownership. Record unsupported self-hosted features explicitly.
5. Place a policy gateway before Firecrawl for domain authorization, request shaping, budgets, key selection, and audit receipts. Keep content storage and indexing downstream.
6. Define queue limits, explicit crawl limits, retention/cache choices, idempotency keys, pagination ownership, and degraded modes.
7. Validate the chosen variant with one approved canary and document failure, retry, cancellation, and rollback paths.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before selecting self-hosting, introducing a new external provider, permitting authenticated-page capture, enabling Cloud-only capabilities, or broadening domains and retention.

## Output

Return an architecture decision record containing workload facts, chosen endpoints, sequence, trust boundaries, data flows, capacity assumptions, recovery path, alternatives rejected, validation evidence, and open approvals.

## Error Handling

- Requirements conflict: surface the conflict and propose bounded variants instead of hiding it in implementation.
- Self-host feature is unsupported: choose Cloud or identify and validate the required external service.
- Recovery path is undefined: block launch until cancellation, replay, and deduplication behavior is owned.

## Examples

- "Design a nightly documentation ingest" selects a bounded crawl or map-plus-batch variant with async recovery.
- "Keep all traffic inside our infrastructure" evaluates self-hosted capability gaps and operating cost before choosing it.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
