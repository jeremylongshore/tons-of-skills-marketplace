---
name: algolia-core-workflow-a
description: >-
  Implement or review a single-index Algolia search contract with filters, facets, pagination, and highlighting. Use when building product or content search against the JavaScript v5 client. Trigger with "Algolia search workflow", "add facets", or "searchSingleIndex".
argument-hint: "[repository-path] [index-name]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- search
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Search Contract

## Overview

This skill defines the read path between application input and Algolia search results. It keeps query construction, allowed filters, pagination, and result projection explicit so UI behavior can be tested independently.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Use `searchSingleIndex` for one index and pass `indexName` plus `searchParams` on the v5 client.
- Treat filters and facet filters as structured application inputs; do not concatenate untrusted syntax.
- Request only attributes the interface needs and preserve `objectID` as the stable result identity.
- Enable click analytics only when the product also implements the query ID and event contract.

## Authentication

Browser search should use the search-only key or a backend-generated secured key. Write-capable credentials remain server-side.

## Instructions

1. Inspect the installed client version, index settings, record schema, and current UI query state.
2. Define a typed search input with bounded query length, page, hits per page, filters, and facets.
3. Translate application filters through an allowlist rather than accepting raw filter strings.
4. Call the v5 search boundary and map hits into the application result type.
5. Test empty query, no results, special characters, pagination edges, and unavailable facets.
6. Verify returned attributes do not disclose fields the interface should not expose.

## Approval Boundaries

Do not change index settings, enable analytics, or expose additional attributes as part of a read-path implementation without explicit review.

## Output

Return the typed input/output contract, query builder, relevant tests, credential boundary, observed response metadata, and any required index-setting change.

## Error Handling

| Condition | Response |
|---|---|
| Invalid filter syntax | Reject or normalize at the application boundary. |
| Facet missing | Confirm the attribute is configured before changing the UI. |
| Unexpected fields returned | Tighten retrieval and index visibility settings. |
| No query ID | Enable click analytics only with an approved event design. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
query=boots; facets=brand,size; page=0; credential=search-only
```

Expected handoff:

```text
hits=24; exposed-fields=objectID,name,price; raw-filter-input=blocked
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Search API client](https://www.algolia.com/doc/libraries/javascript)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
- [Sending events](https://www.algolia.com/doc/guides/sending-events)
