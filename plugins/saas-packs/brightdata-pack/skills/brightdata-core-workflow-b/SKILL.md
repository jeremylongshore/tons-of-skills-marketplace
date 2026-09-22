---
name: brightdata-core-workflow-b
description: 'Analyze and operate the Bright Data Web Scraper API async snapshot lifecycle with terminal-state and delivery controls. Use when collecting an approved batch, polling a snapshot, or downloading large structured results. Trigger with: "run a Bright Data dataset job", "poll a Bright Data snapshot", "download Web Scraper API results".'
allowed-tools: Read, Grep, Write, Edit, Bash(curl:*)
version: 2.0.0
argument-hint: "[dataset-run-manifest]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- core-workflow-b
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Async Snapshot Pipeline

## Overview

Implement the documented trigger, progress, and download lifecycle as a state machine. Keep dataset identifiers and approved inputs separate from the API key; cap polling, validate terminal states, and stream results rather than loading arbitrary payloads into memory.

## Prerequisites

- A reviewed dataset ID and approved public input manifest
- A named-user Bright Data API key in the runtime secret manager
- A retention, schema, maximum-record, and maximum-byte policy

## Instructions

### Step 1: Validate the manifest

Read the requested dataset/inputs and Grep for disallowed target classes or fields. Hash the approved input manifest before submission.

### Step 2: Trigger once

Use Bash(curl:*) only against the fixed Bright Data API origin with the API key as a Bearer header.

```bash
curl --fail-with-body --request POST \
  'https://api.brightdata.com/datasets/v3/trigger?dataset_id=DATASET_ID' \
  --header "Authorization: Bearer $BRIGHTDATA_API_KEY" \
  --header 'Content-Type: application/json' \
  --data-binary @approved-inputs.json
```

### Step 3: Poll deliberately

Persist the returned `snapshot_id`; poll `GET /datasets/v3/progress/SNAPSHOT_ID` with bounded attempts and provider-directed delay. Handle `ready`, `failed`, empty, expired, and still-building states explicitly.

### Step 4: Download and verify

Stream `GET /datasets/v3/snapshot/SNAPSHOT_ID` in the approved format. Use parts for large results, hold format/compression parameters constant, enforce byte/record ceilings, and validate the schema before promotion.

## Tool Discipline

Use Read and Grep for policy and schema checks. Use Write and Edit only for the manifest, state machine, tests, and redacted receipt. Use Bash(curl:*) for fixed-origin Bright Data API calls after authorization; never print the Bearer value or raw result data.

## Output

- Input-manifest hash and snapshot identifier
- Bounded state-transition log without target data or credentials
- Schema/size validation and a promoted-or-quarantined result

## Examples

Submit a small approved URL batch, record the returned snapshot ID, poll until `ready`, and stream JSON to quarantine. Reject a response whose schema, record count, or byte count exceeds the manifest even if the provider marks it ready.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| 400 validation response | Dataset ID or input shape is invalid | Correct the manifest; do not retry unchanged input |
| 429 or too many jobs | Tenant or dataset concurrency is exhausted | Pause new triggers and wait for owned jobs |
| Snapshot expired or empty | Result cannot be promoted | Trigger a newly approved run or investigate inputs |

## Resources

- [Web Scraper API asynchronous requests](https://docs.brightdata.com/api-reference/rest-api/scraper/asynchronous-requests)
- [Download snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/download-snapshot)
- [Scraper async requests guide](https://docs.brightdata.com/products/scrapers/scrapers-library/async-requests)
- [Authentication and API keys](https://docs.brightdata.com/api-reference/authentication)
