---
name: brightdata-debug-bundle
description: 'Assemble a Bright Data support bundle that preserves diagnostic value while excluding credentials, target data, and secret-bearing URLs. Use when escalating a persistent proxy, Browser API, snapshot, or delivery incident. Trigger with: "build a Bright Data debug bundle", "prepare evidence for Bright Data support", "redact a Bright Data incident".'
allowed-tools: Read, Grep, Write, Edit, Bash(python:*)
version: 2.0.0
argument-hint: "[run-receipt]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- debug-bundle
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Redacted Support Bundle

## Overview

Build a deterministic manifest of configuration shape, timestamps, versions, provider codes, and operation identifiers. Default-deny all raw headers and payloads, then include only explicitly allowlisted diagnostic fields.

## Prerequisites

- A run receipt and named incident owner
- A private output directory with a retention deadline
- A redaction policy covering URLs, credentials, cookies, headers, and target data

## Instructions

### Step 1: Inventory inputs

Read the receipt and Grep candidate logs for secret names, proxy URLs, Bearer values, cookies, query strings, and target content before copying anything.

### Step 2: Create the manifest

Write a small metadata file with product, zone alias, client/runtime version, UTC window, operation ID, state, and current provider error fields.

```json
{"product":"web-scraper-api","zone_alias":"production-redacted","operation_id":"s_redacted","provider_code":"client_10000","raw_payload_included":false}
```

### Step 3: Redact and validate

Use Edit only to remove disallowed material from the private bundle. Use Bash(python:*) to scan for configured secret values and forbidden keys; fail closed if any match remains.

### Step 4: Seal the evidence

Record sorted file hashes, owner, purpose, recipient, and deletion time. Transmit only through the approved private support channel; never attach it to a public issue.

## Tool Discipline

Use Read and Grep for discovery and pre-copy review. Use Write and Edit only inside the exact private bundle path. Use Bash(python:*) for local redaction and checksum checks; it must not upload the bundle or call Bright Data.

## Output

- Private manifest plus allowlisted redacted diagnostics
- Zero-secret scan and sorted file-hash receipt
- Named recipient, retention deadline, and deletion owner

## Examples

Include `Proxy-Status`, `x-brd-err-code`, a rounded UTC window, and an opaque snapshot ID. Exclude proxy username/password, API key, target URL query, response body, cookies, and collected records.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| Secret scan finds a value | Redaction is incomplete | Quarantine the bundle and rebuild from the allowlist |
| Raw target content is required to reproduce | Support request exceeds the safe default | Obtain data-owner approval and use a separate controlled transfer |
| No operation identifier exists | Evidence cannot be correlated | Reproduce once against an approved test target |

## Resources

- [Proxy error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog)
- [Network status](https://brightdata.com/network-status)
- [Authentication and API keys](https://docs.brightdata.com/api-reference/authentication)
- [Acceptable use policy](https://docs.brightdata.com/general/policy/acceptable-use-policy)
