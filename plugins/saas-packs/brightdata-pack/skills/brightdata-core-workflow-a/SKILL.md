---
name: brightdata-core-workflow-a
description: 'Analyze an approved JavaScript-rendered task through Bright Data Browser API with bounded interaction and evidence. Use when a static request cannot satisfy an authorized public-data workflow and browser rendering is required. Trigger with: "use Bright Data Browser API", "connect Playwright to Bright Data", "collect a rendered public page".'
allowed-tools: Read, Grep, Write, Edit, Bash(python:*)
version: 2.0.0
argument-hint: "[browser-task-manifest]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- core-workflow-a
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Browser API Run

## Overview

Treat Browser API as a remote-browser data plane, not an unlimited browsing identity. Bind one browser zone, a public-target manifest, an interaction ceiling, and a minimal output schema before connecting.

## Prerequisites

- A Browser API zone username/password stored in the runtime secret manager
- An approved public target and interaction manifest
- Playwright plus the reviewed Bright Data Python SDK or current documented client

## Instructions

### Step 1: Approve the task

Read the task manifest and Grep for login, account creation, purchase, message, or other prohibited interactions. Refuse any nonpublic or abusive workflow.

### Step 2: Connect through the SDK

Build the connect URL with the official client and keep credentials out of logs.

```python
from brightdata import BrightDataClient

client = BrightDataClient(
    browser_username=browser_user,
    browser_password=browser_password,
)
# Pass client.browser.get_connect_url() only to Playwright connect_over_cdp.
```

### Step 3: Constrain the page

Allow only the manifest host set, cap navigation and wall time, block unnecessary assets where appropriate, and extract only named public fields. Do not add evasion behavior after a policy denial.

### Step 4: Review and close

Use Bash(python:*) for fixture-backed browser tests. Persist the task ID, target class, field counts, provider errors, and policy decision; discard raw page content unless retention was explicitly approved.

## Tool Discipline

Use Read and Grep to verify the manifest and existing browser adapter. Use Write and Edit for the bounded task, schema, and tests. Use Bash(python:*) for offline tests; connecting a live browser still requires the recorded authorization gates.

## Output

- A bounded Browser API task manifest
- Schema-validated public fields and redacted run receipt
- Explicit close, retry, or policy-escalation result

## Examples

Use Browser API for an approved public page that requires JavaScript to render a price table. Navigate only to allowlisted hosts, extract the three approved fields, close the browser in `finally`, and reject any redirect to authentication.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| Connection is rejected | Zone credentials, entitlement, or egress is wrong | Verify the owned zone; do not expose the connect URL |
| Page redirects to login | The task crossed into nonpublic data | Stop and mark the target out of scope |
| Policy error is returned | Product or target is not authorized | Escalate; never add bypass behavior |

## Resources

- [Browser API](https://docs.brightdata.com/products/scraping-browser/introduction)
- [Python SDK](https://docs.brightdata.com/api-reference/SDK)
- [Acceptable use policy](https://docs.brightdata.com/general/policy/acceptable-use-policy)
- [Proxy error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog)
