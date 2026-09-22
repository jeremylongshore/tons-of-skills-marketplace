---
name: brightdata-local-dev-loop
description: 'Build a local Bright Data development loop that defaults to synthetic fixtures and makes live traffic explicit. Use when implementing parsers, retry classification, or snapshot handling without spending credits or collecting data. Trigger with: "mock Bright Data locally", "test a Bright Data adapter offline", "add a safe live-test switch".'
allowed-tools: Read, Grep, Write, Edit, Bash(npm:*)
version: 2.0.0
argument-hint: "[adapter-path]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- local-dev-loop
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Local Fixture Loop

## Overview

Separate transport from parsing so ordinary development is deterministic and credential-free. The live lane is opt-in, target-allowlisted, budgeted, and incapable of silently replacing fixtures.

## Prerequisites

- A repository-owned Bright Data adapter boundary
- Synthetic or approved redacted fixtures with expected schemas
- A test runner and a protected live-test environment

## Instructions

### Step 1: Map the boundary

Read the adapter and Grep for direct proxy/API calls in business logic. Move transport behind a narrow interface before recording fixtures.

### Step 2: Create explicit modes

Write configuration with `fixture` as the default and `live` requiring three independent gates.

```yaml
brightdata:
  mode: fixture
  live_requires:
    - BRIGHTDATA_LIVE_TEST=1
    - approved_target_manifest
    - bounded_cost_budget
```

### Step 3: Test contract behavior

Add fixtures for success, 407, policy 403, 429, building, ready, failed, empty, and expired states. Test parsers against provider fields rather than copied HTML.

### Step 4: Run the loop

Use Bash(npm:*) for unit and contract tests. Permit the live suite only in a protected environment, against an approved target, with a one-job ceiling and redacted receipt.

## Tool Discipline

Use Read and Grep for discovery. Use Write and Edit only for the adapter, fixtures, tests, and documented configuration. Use Bash(npm:*) for the named local suites; never let a default test command send live Bright Data traffic.

## Output

- A fixture-first transport adapter
- Deterministic success and failure fixtures
- A separately gated live-test receipt and explicit budget

## Examples

A parser change should pass against a synthetic snapshot and recorded provider-error metadata with no credentials present. A maintainer may later enable one protected live job; its output updates no fixture automatically and is reviewed before adoption.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| Unit tests attempt network access | Transport leaked into parsing code | Block network and refactor through the adapter |
| Fixture contains target data | Captured live content was committed | Remove it and replace it with synthetic minimal data |
| Live gate has only one switch | Accidental execution remains possible | Require environment, target manifest, and budget gates |

## Resources

- [Web Scraper API asynchronous requests](https://docs.brightdata.com/api-reference/rest-api/scraper/asynchronous-requests)
- [Download snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/download-snapshot)
- [Proxy error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog)
- [Acceptable use policy](https://docs.brightdata.com/general/policy/acceptable-use-policy)
