---
name: firecrawl-reference-architecture
description: >-
  Design a production Firecrawl v2 ingestion system with policy gateway, bounded acquisition, validation, provenance, storage, indexing, observability, and deletion. Use when building a reusable platform. Trigger with "Firecrawl reference architecture", "Firecrawl ingestion system", or "Firecrawl RAG pipeline".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workload-profile>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, architecture, ingestion]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Governed Ingestion Architecture

## Overview

Create explicit trust boundaries from request intake through deletion. Keep source discovery, content retrieval, validation, and downstream publication independently retryable and auditable.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Firecrawl v2 provides scrape, crawl, map, search, batch scrape, parse, JSON extraction, agentic, and browser surfaces with different async, credit, retention, and availability contracts. The SDK can auto-wait and paginate, while explicit start/status methods support durable orchestration. Provider webhooks supplement but do not replace reconciliation.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Define tenants, source authorization, freshness, scale, formats, data classification, SLO/RPO/RTO, retention, deletion, and cost constraints.
2. Place authentication, tenant isolation, URL canonicalization, policy versioning, endpoint/format allowlists, budgets, and idempotency at the intake gateway.
3. Separate discovery into map/search, retrieval into scrape/batch/crawl/parse, and model extraction into a validated stage. Use durable job records for asynchronous work.
4. Persist normalized provenance and job/page state before downstream writes. Complete pagination and deduplicate by tenant, canonical source, version, and content hash.
5. Run schema, origin-status, content-quality, malware/active-content, and prompt-injection gates before storage or agent context.
6. Use an outbox or equivalent for indexing and publication; make retries idempotent and support tombstones across raw, normalized, embedding, cache, and search stores.
7. Observe queue, job, origin, validation, freshness, spend, webhook, and deletion SLIs; test restore, reconciliation, cancellation, and regional/provider failure.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require architecture and security/data approval before adding a new endpoint class, authenticated source, model extraction, long-term store, cross-region flow, or self-hosted provider.

## Output

Return components and trust boundaries, sequence and state model, contracts, capacity and cost assumptions, security/privacy controls, failure and reconciliation paths, SLOs, tests, and phased rollout.

## Error Handling

- A stage lacks durable identity or idempotency: block asynchronous rollout.
- Provider completion and stored counts diverge: reconcile pagination and downstream receipts before publication.
- Deletion cannot propagate to derived stores: fail the data architecture review.

## Examples

- "Build a docs RAG pipeline" produces policy, acquisition, validation, outbox, index, and deletion stages.
- "Call crawl directly from the browser" is replaced with a server-side governed gateway.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
