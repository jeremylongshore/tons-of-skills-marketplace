---
name: brightdata-hello-world
description: 'Prove one authorized Bright Data proxy request and capture a redacted connectivity receipt. Use when validating a new zone, testing egress, or separating proxy failures from target failures. Trigger with: "test my Bright Data proxy", "verify this zone", "run a safe Bright Data smoke test".'
allowed-tools: Read, Grep, Bash(curl:*)
version: 2.0.0
argument-hint: "[approved-test-target]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- hello-world
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Authorized First Request

## Overview

Run the smallest possible request against Bright Data's test endpoint. Keep proxy credentials out of the URL and process output, inspect current `x-brd-*` and `Proxy-Status` headers, and stop after one bounded proof.

## Prerequisites

- An active non-production proxy zone and zone username/password
- Authorization to reach `geo.brdtest.com` from the test environment
- A log sink configured to redact authorization and proxy credentials

## Instructions

### Step 1: Confirm the target

Read the runbook and Grep the allowlist for `geo.brdtest.com`. Refuse arbitrary or authenticated targets for this proof.

### Step 2: Run one request

Pass proxy authentication separately from the proxy host so the credential does not appear in the URL.

```bash
# 33335 is Bright Data's documented proxy gateway port.
curl --silent --show-error --include \
  --proxy http://brd.superproxy.io:33335 \
  --proxy-user "$BRIGHTDATA_PROXY_USERNAME:$BRIGHTDATA_PROXY_PASSWORD" \
  https://geo.brdtest.com/welcome.txt
```

### Step 3: Classify the response

Record the HTTP status plus redacted `Proxy-Status`, `x-brd-err-code`, `x-brd-error`, and `x-brd-err-msg` values. Never retain the proxy authorization header or full username.

### Step 4: Close the proof

Store the timestamp, zone alias, target, result class, and owner decision. A successful test proves connectivity only; it does not authorize production collection.

## Tool Discipline

Use Read and Grep to confirm the approved target and redaction policy. Use Bash(curl:*) for exactly the bounded Bright Data test request shown here. Do not write target content, rotate identities, or retry policy denials.

## Output

- One connectivity result tied to a zone alias and approved target
- Redacted provider error metadata when the request fails
- A clear pass, retry-later, or owner-escalation decision

## Examples

Use a dedicated development zone and run one request to `geo.brdtest.com`. A 200 with expected provider metadata is a connectivity pass. A 407 is an access failure; a policy 403 is a stop condition, not a reason to switch networks.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| 407 with `client_10000` or related code | Invalid or missing zone credentials | Verify the zone binding without printing credentials |
| Policy 403 | Target or network is not permitted | Stop and escalate to the authorization owner |
| 429 | Account, target, or per-IP throttling | Stop the smoke test and follow the rate-control workflow |

## Resources

- [Proxy API authentication](https://docs.brightdata.com/api-reference/proxy/proxy_api_auth)
- [Proxy error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog)
- [Proxy configuration options](https://docs.brightdata.com/proxy-networks/config-options)
- [Acceptable use policy](https://docs.brightdata.com/general/policy/acceptable-use-policy)
