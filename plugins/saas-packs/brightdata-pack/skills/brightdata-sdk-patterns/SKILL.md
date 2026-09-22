---
name: brightdata-sdk-patterns
description: 'Wrap the official Bright Data Python SDK and REST contracts behind a typed, testable client boundary. Use when adding SDK calls, isolating provider upgrades, or normalizing scraper and Browser API results. Trigger with: "wrap the Bright Data SDK", "design a Bright Data client", "pin Bright Data Python dependencies".'
allowed-tools: Read, Grep, Write, Edit, Bash(python:*)
version: 2.0.0
argument-hint: "[client-module]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- sdk-patterns
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Typed Client Boundary

## Overview

Use the official Python SDK where it matches the workload, but keep product choice, authorization, retry policy, and domain schemas outside vendor objects. Pin the dependency and expose a small application-owned interface.

## Prerequisites

- A Python project with a lockfile and supported runtime
- An approved Bright Data product and credential mode
- Synthetic contract fixtures for every exposed operation

## Instructions

### Step 1: Pin and inspect

Read the lockfile and Grep for direct Bright Data imports. Pin the reviewed SDK release through the repository dependency workflow rather than embedding a version in this skill.

### Step 2: Define the port

Write an application interface that returns normalized records and provider receipts, not raw SDK response objects.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class CollectionReceipt:
    operation_id: str
    state: str
    records: int | None
    provider_code: str | None
```

### Step 3: Implement adapters

Keep API-key, proxy-zone, and Browser API adapters separate. Map documented terminal states and current `x-brd-*` errors into stable application failure classes.

### Step 4: Verify the seam

Use Bash(python:*) to run type checks and fixture tests. Compare the locked SDK behavior with the current official SDK docs before any upgrade.

## Tool Discipline

Use Read and Grep to locate dependency and transport boundaries. Use Write and Edit for the typed port, provider adapters, and tests. Use Bash(python:*) only for local type/test commands; live SDK calls require a separate authorized workflow.

## Output

- Pinned SDK dependency and application-owned port
- Separate credential/product adapters
- Normalized receipts and fixture-backed failure mapping

## Examples

Expose `trigger_collection`, `get_progress`, and `download_snapshot` through your own protocol. Keep a vendor response fixture at the boundary, map it once, and let downstream code depend only on `CollectionReceipt`.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| SDK object escapes the adapter | Provider coupling reaches domain code | Normalize the response at the boundary |
| Upgrade changes a field or state | Lockfile moved without contract review | Hold the upgrade and refresh fixtures from documentation |
| Client selects a product implicitly | Policy and cost behavior become hidden | Require an explicit product configuration |

## Resources

- [Python SDK](https://docs.brightdata.com/api-reference/SDK)
- [Authentication and API keys](https://docs.brightdata.com/api-reference/authentication)
- [Web Scraper API asynchronous requests](https://docs.brightdata.com/api-reference/rest-api/scraper/asynchronous-requests)
- [Browser API](https://docs.brightdata.com/products/scraping-browser/introduction)
