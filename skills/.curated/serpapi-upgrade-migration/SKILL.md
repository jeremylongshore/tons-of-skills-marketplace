---
name: serpapi-upgrade-migration
description: 'Migrate legacy SerpAPI Python or JavaScript packages and response assumptions to current official clients with contract tests and rollback. Use when performing dependency or API upgrades. Trigger with "migrate a SerpAPI client".'
argument-hint: "[python|javascript] [from-version] [to-version]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit, Bash(python3:*), Bash(npm:*)
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, migration, python, javascript]
model: inherit
effort: high
compatibility: Designed for Claude Code; dependency installation, live comparison, and production rollout require repository and account-owner approval
---
# SerpAPI Client Upgrade and Migration

## Overview

Inventory actual legacy behavior, introduce the current official client behind a seam, and prove response and failure compatibility before removing the old path.

## Prerequisites

- Current dependency locks, imports, call sites, engine parameters, fixtures, and runtime support matrix
- Target official client release notes and migration documentation
- Search budget, canary environment, rollback owner, and immutable baseline

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inventory dependencies and behavior, `WebFetch` to verify current official packages, `Write` or `Edit` for the adapter and tests, and `Bash(python3:*)` or `Bash(npm:*)` only for approved installs and test execution.

## Current Contract

The recommended Python distribution is `serpapi`, distinct from the legacy `google-search-results` distribution. Its `Client.search` returns a `SerpResults` mapping with helpers such as `as_dict()` and pagination methods. The current JavaScript `serpapi` package supports promises and callbacks; migration from `google-search-results-nodejs` must preserve engine parameters and error behavior explicitly.

## Authentication

Keep the existing server-side `SERPAPI_KEY` boundary unchanged during migration. Never copy credentials into migration scripts, lockfiles, fixtures, dual-run telemetry, or exception snapshots.

## Instructions

1. Pin the baseline and inventory package names, versions, imports, engine-specific classes, callbacks, result conversions, pagination, timeouts, retries, and error handling.
2. Re-fetch target release notes and build a behavior matrix for requests, result type, archive access, pagination, and exceptions.
3. Add an application-owned gateway and run both implementations against the same sanitized fixtures.
4. Update Python code from legacy engine classes to current client calls, or JavaScript callbacks to the chosen promise/callback form, without mixing semantic changes.
5. Regenerate the dependency lock and run static, unit, fixture, failure-path, and packaging tests.
6. With approval, compare one harmless live request through each path or use a single captured response when duplicate searches are unnecessary.
7. Canary the new path behind a flag, reconcile outputs and capacity, then remove the legacy dependency only after rollback criteria hold.

## Output

Return the baseline and target versions, behavior matrix, changed call sites, lockfile diff, fixture/live comparison, canary evidence, legacy removal decision, and rollback plan.

## Error Handling

| Condition | Response |
|---|---|
| Result treated as an exact plain `dict` | Update types to the documented mapping or call `as_dict()` where an exact dictionary is required. |
| Error behavior changes | Normalize exceptions in the gateway before rollout. |
| Engine parameters drift | Restore parity and test each engine independently. |
| Dual-run doubles usage | Stop duplicate live calls and compare from one sanitized capture. |

## Example

```python
# Current official Python client
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=10)
result = client.search({"engine": "google", "q": "coffee"})
plain_result = result.as_dict()
```

## Resources

- [Official Python client](https://github.com/serpapi/serpapi-python)
- [Official JavaScript client](https://github.com/serpapi/serpapi-javascript)
- [JavaScript migration guide](https://github.com/serpapi/serpapi-javascript/blob/master/MIGRATION.md)

## Next Steps

Remove the feature flag only after a full observation window and archive the rollback receipt.
