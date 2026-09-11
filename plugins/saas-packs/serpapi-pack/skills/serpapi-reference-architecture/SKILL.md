---
name: serpapi-reference-architecture
description: 'Design a governed SerpAPI search service with engine adapters, policy enforcement, caching, capacity management, observability, and privacy boundaries. Use when conducting architecture review. Trigger with "design a SerpAPI architecture".'
argument-hint: "[use-case] [engines] [data-classification]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, architecture, governance, reliability]
model: inherit
effort: high
compatibility: Designed for Claude Code; architecture output is a review artifact and does not authorize infrastructure, account, or production changes
---
# SerpAPI Governed Reference Architecture

## Overview

Place SerpAPI behind an application boundary that controls identity, parameters, data, allowance, and failure behavior for every engine.

## Prerequisites

- Business use cases, caller identities, engines, data classes, freshness and latency objectives
- Volume model, account contract, downstream systems, and regulatory/retention requirements
- Security, product, finance, reliability, and platform owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to ground the design in repository and infrastructure topology, `WebFetch` to verify current vendor contracts, and `Write` or `Edit` for diagrams, decision records, interfaces, threat models, and rollout evidence.

## Current Contract

SerpAPI has engine-specific requests and variable response sections, private-key authentication, account-level search and throughput capacity, optional async/archive processing, one-hour exact-query server caching, and Enterprise ZeroTrace. Async depends on archive retrieval, while ZeroTrace intentionally prevents stored search records.

## Authentication

Keep `SERPAPI_KEY` in a server-side secret boundary. Authenticate application callers independently and enforce use-case authorization before the gateway maps input to allowlisted vendor parameters.

## Instructions

1. Map callers, trust zones, engines, queries, results, stores, consumers, data classes, and systems of record.
2. Define an authenticated gateway with use-case-specific input schemas, engine adapters, output projections, and policy enforcement.
3. Add an application cache with credential-free semantic keys, freshness TTLs, encryption and retention appropriate to the data class.
4. Coordinate admission, concurrency, pagination, retries, and background work against live Account API capacity.
5. Separate synchronous calls from async/archive jobs and prove that any ZeroTrace path does not rely on archive replay.
6. Emit safe metrics and search-ID correlation without query, result, key-bearing URL, or account leakage.
7. Design fixture-first tests, canary, reconciliation, degradation, support escalation, key rotation, disaster recovery, and rollback.
8. Record alternatives, constraints, approvals, unresolved risks, and a staged implementation plan.

## Approval Boundaries

Do not provision infrastructure, expose routes, create secrets, enable account features, or send production searches from an architecture exercise.

## Output

Return context and container diagrams, trust/data flows, gateway and adapter contracts, cache/capacity design, privacy decision, failure model, test/rollout plan, risks, and decision owners.

## Error Handling

| Condition | Response |
|---|---|
| Gateway is a generic parameter pass-through | Replace it with use-case schemas and allowlists. |
| Capacity is managed per instance only | Add shared admission control across credential-sharing workers. |
| ZeroTrace path requires replay | Redesign the diagnostic and recovery model. |
| Search results become a system of record | Define provenance, refresh, deletion, and reconciliation explicitly. |

## Example

```text
caller -> authenticated policy gateway -> engine adapter -> capacity limiter -> SerpAPI
                                      \-> semantic cache
search metadata -> redacted telemetry; normalized results -> governed consumer
```

## Resources

- [SerpAPI documentation](https://serpapi.com/)
- [Account API](https://serpapi.com/account-api)
- [ZeroTrace Mode](https://serpapi.com/zero-trace-mode)
- [Searches Archive API](https://serpapi.com/searches-archive-api)

## Next Steps

Validate the design with security, product, finance, and reliability owners before creating an implementation tranche.
