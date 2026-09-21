---
name: brightdata-upgrade-migration
description: 'Migrate Bright Data SDK, API, product, or response-header contracts with fixture evidence and a reversible canary. Use when upgrading the Python SDK, moving dataset endpoints, renaming Scraping Browser to Browser API, or removing legacy headers. Trigger with: "upgrade Bright Data", "migrate x-luminati headers", "change a Bright Data API contract".'
allowed-tools: Read, Grep, Write, Edit, Bash(python:*)
version: 2.0.0
argument-hint: "[current-to-target-contract]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- upgrade-migration
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Contract Migration

## Overview

Inventory the exact current behavior before changing dependencies or products. Treat an SDK update, API endpoint change, Browser API rename, and product migration as separate changes with separate rollback boundaries.

## Prerequisites

- A pinned current dependency or configuration and documented target contract
- Golden synthetic fixtures plus representative redacted receipts
- A dual-read or feature-flag path and rollback owner

## Instructions

### Step 1: Build the delta

Read the lockfile, adapter, and runbooks; Grep for `x-luminati`, old product names, obsolete endpoints, raw vendor response coupling, and undocumented ports.

### Step 2: Update one boundary

Write the target dependency, API, or header mapping. Current diagnostics use `Proxy-Status` and `x-brd-*`; Browser API replaces the former Scraping Browser name. Do not invent version transitions.

### Step 3: Verify compatibility

Edit fixture tests for success, authentication, policy, throttle, lifecycle, schema, and delivery states. Use Bash(python:*) for the pinned type and test suite and compare normalized outputs.

### Step 4: Canary and retire

Run an authorized feature-flag canary, compare data and operational receipts, then remove the old path only after rollback expiry and owner signoff.

## Tool Discipline

Use Read and Grep for the migration inventory. Use Write and Edit for dependency, adapter, fixture, and runbook changes. Use Bash(python:*) for local tests; it does not authorize live migration traffic or credential changes.

## Output

- Current-to-target contract matrix
- Passing old and new fixture comparison and canary receipt
- Rollback path plus explicit old-contract retirement decision

## Examples

First replace parsing of `x-luminati-error` with current `x-brd-error` and `Proxy-Status` fixtures. Keep a short dual-read window for retained historical receipts, but require current fields from new live responses.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| Migration combines product and SDK changes | Failure attribution is impossible | Split the rollout into independently reversible steps |
| Golden fixture contains live data | Test evidence is unsafe | Replace it with a synthetic contract fixture |
| New path changes normalized output | Downstream behavior would drift | Hold promotion and reconcile the schema |

## Resources

- [Python SDK](https://docs.brightdata.com/api-reference/SDK)
- [Proxy error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog)
- [Browser API](https://docs.brightdata.com/products/scraping-browser/introduction)
- [Web Scraper API asynchronous requests](https://docs.brightdata.com/api-reference/rest-api/scraper/asynchronous-requests)
