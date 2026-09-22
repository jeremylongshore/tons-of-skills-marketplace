---
name: brightdata-ci-integration
description: 'Build an offline-default CI contract lane for Bright Data and isolate any authorized live probe behind protected controls. Use when adding provider checks to pull requests or release workflows. Trigger with: "test Bright Data in CI", "add a Bright Data contract job", "secure the live CI probe".'
allowed-tools: Read, Grep, Write, Edit, Bash(npm:*)
version: 2.0.0
argument-hint: "[workflow-or-test-path]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- ci-integration
- operations
compatibility: 'Requires offline Bright Data fixtures; an optional live lane requires protected CI secrets and an explicitly approved target'
---
# Bright Data CI Contract Lane

## Overview

Keep pull-request verification credential-free and deterministic. Test the Bright Data adapter against fixtures by default, then place any necessary live probe in an independent protected job with a dedicated credential, approved target, and one-operation budget.

## Prerequisites

- A repository test command and representative sanitized success and failure fixtures
- The CI workflow and Bright Data adapter paths
- Maintainer approval before creating an optional live lane

## Instructions

### Step 1: Audit the workflow boundary

Read the workflow and Grep for secrets, direct provider calls, artifact uploads, and execution from untrusted forks. Map every test to either the offline contract lane or the protected live lane.

### Step 2: Add the required offline lane

Write or Edit the workflow so the required job runs `npm ci` and `npm run test:brightdata:contract` with `BRIGHTDATA_MODE=fixture`. Cover success, authentication denial, policy denial, 429, provider 5xx, malformed output, and redaction without network access.

### Step 3: Isolate the optional live lane

Make the live job independent of fork and pull-request execution. Require a protected environment, maintainer authorization, an approved public target, a dedicated least-privilege secret, a single-operation ceiling, a timeout, and redacted logs.

### Step 4: Prove negative behavior

Use Bash(npm:*) to run contract tests with missing and sentinel credentials. Confirm the offline job remains green without secrets and that failure artifacts contain neither credentials nor collected payloads.

## Tool Discipline

Use Read and Grep to inspect workflows, adapters, and secret references. Use Write and Edit for the workflow, fixtures, tests, and runbook. Use Bash(npm:*) only for dependency installation and repository test commands; do not use it to make live Bright Data requests.

## Output

- A required credential-free offline contract job
- An optional, independent protected live-probe job
- Negative-test and redaction receipts

## Examples

A forked pull request runs synthetic proxy and snapshot fixtures only. A maintainer-triggered release workflow may perform one approved provider operation through a protected environment and records only status, latency, and redacted error class.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| A fork can access a provider secret | Trust boundary is broken | Disable the live job and remove the secret exposure |
| Offline tests require the network | Contract lane is nondeterministic | Replace provider traffic with sanitized fixtures |
| A live artifact contains raw output | Data boundary is broken | Delete the artifact and retain only redacted metrics |

## Resources

- [Proxy error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog)
- [Acceptable use policy](https://docs.brightdata.com/general/policy/acceptable-use-policy)
- [Proxy API authentication](https://docs.brightdata.com/api-reference/proxy/proxy_api_auth)
- [Asynchronous scraper requests](https://docs.brightdata.com/api-reference/rest-api/scraper/asynchronous-requests)
