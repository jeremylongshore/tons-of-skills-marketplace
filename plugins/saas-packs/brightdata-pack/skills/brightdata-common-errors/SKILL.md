---
name: brightdata-common-errors
description: 'Analyze Bright Data proxy and dataset failures using current provider codes without bypassing policy controls. Use when diagnosing 407, 403, 429, 502, snapshot, or delivery failures. Trigger with: "diagnose a Bright Data error", "what does this x-brd code mean", "triage a failed snapshot".'
allowed-tools: Read, Grep, Bash(curl:*)
version: 2.0.0
argument-hint: "[redacted-response]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- common-errors
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Failure Triage

## Overview

Separate provider, target, client, and policy failures using HTTP status, `Proxy-Status`, and current `x-brd-*` fields. Never treat an access or compliance denial as a cue to rotate products, regions, or identities.

## Prerequisites

- A redacted response or snapshot receipt
- The zone, product, operation ID, and approved target class
- Access to the current Bright Data error catalog and network-status page

## Instructions

### Step 1: Collect minimal evidence

Read the receipt and Grep for status, `Proxy-Status`, `x-brd-err-code`, `x-brd-error`, `x-brd-err-msg`, snapshot state, and request time. Exclude credentials, full URLs, and bodies.

### Step 2: Identify the layer

Classify authentication (407/client), policy (403/policy), throttling (429), peer/target (408/502), provider incident, or dataset lifecycle failure.

### Step 3: Reproduce safely

Use Bash(curl:*) only for one authorized provider test endpoint or a read-only status check. Do not reproduce against a sensitive target or change network type to defeat a denial.

### Step 4: Choose the response

Fix deterministic client/auth errors; back off transient/provider errors within budget; pause policy, target-data, account, empty, or persistent errors for owner review.

## Tool Discipline

Use Read and Grep to analyze redacted evidence. Use Bash(curl:*) only for a bounded provider-controlled test. This workflow never writes raw response data, prints credentials, or authorizes product or identity switching.

## Output

- Failure layer and documented provider code
- Retry, repair, pause, or escalate decision
- Redacted evidence bundle identifier and owner

## Examples

For `429` with a per-IP code, reduce pressure and review distribution; do not automatically rotate to more identities. For a policy 403, stop. For a provider-wide incident, preserve the receipt and wait for recovery.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| Only an HTTP status is available | Provider detail was discarded | Capture current redacted headers on the next approved attempt |
| Legacy header is the only parser path | `x-luminati-*` support is stale | Migrate to `Proxy-Status` and `x-brd-*` |
| Failure repeats after bounded retry | Classification or provider state is unresolved | Open support escalation with sanitized identifiers |

## Resources

- [Proxy error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog)
- [Network status](https://brightdata.com/network-status)
- [Download snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/download-snapshot)
- [Acceptable use policy](https://docs.brightdata.com/general/policy/acceptable-use-policy)
