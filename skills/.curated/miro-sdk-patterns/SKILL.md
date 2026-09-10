---
name: miro-sdk-patterns
description: "Analyze and execute this workflow: choose and harden Miro Node client or raw REST patterns with typed boundaries, pagination, and tenant isolation. Use when designing a Miro API adapter. Trigger with \"review Miro SDK pattern\"."
argument-hint: "[runtime] [operation-set]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- sdk
- architecture
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Client and Schema Patterns

## Overview

Keep vendor transport details behind a narrow adapter so auth rotation, response drift, retries, and test doubles stay independently verifiable; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Runtime and deployment constraints
- Required REST operations and response schemas
- Official client version or pinned OpenAPI contract

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- `@mirohq/miro-api` is Miro's official Node.js client for REST API v2.
- `Miro` manages OAuth-oriented flows and storage; `MiroApi` represents an access-token-bound API client.
- Collection helpers can be asynchronous iterators; callers must preserve pagination and bounded termination.
- Official examples simplify storage and sessions; production adapters must supply durable tenant-bound implementations.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Inventory current HTTP/SDK calls, token lookup, retries, pagination, and response assumptions.
2. Choose raw REST when protocol control is required or the official client when its surface is verified and sufficient.
3. Expose domain operations through an adapter that accepts tenant context rather than raw credentials.
4. Validate external responses at the boundary and retain unknown fields for drift diagnosis.
5. Centralize safe retry classification, rate headers, timeouts, and redacted error metadata.
6. Pin dependencies, run contract fixtures plus a bounded live read, and record the observed API/client versions.

## Approval Boundaries

Do not swap clients, regenerate from OpenAPI, or change retry semantics across production callers without owner approval and compatibility evidence. Pause when the responsible owner or exact target is uncertain.

## Output

Return client choice, pinned version, operation map, pagination contract, validation boundaries, tenant-isolation tests, and migration risks. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| SDK method differs from docs | Inspect the pinned package types/source and fall back to a verified raw request if approved. |
| Schema validation fails | Quarantine the response and record a redacted structural diff. |
| Iterator does not terminate | Enforce page/cursor and item ceilings. |
| Tenant context is absent | Refuse to construct a client. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
client=@mirohq/miro-api@pinned; operations=boards-read,items-read; tenant-tests=passed; unbounded-iterators=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Node.js client](https://developers.miro.com/docs/miro-nodejs-api-client)
- [REST reference](https://developers.miro.com/reference/overview)
