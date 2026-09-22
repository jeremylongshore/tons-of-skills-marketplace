---
name: brightdata-install-auth
description: 'Bootstrap Bright Data access without mixing proxy-zone credentials and REST API keys. Use when onboarding an integration, changing credential ownership, or proving least-privilege access. Trigger with: "set up Bright Data access", "configure a Bright Data zone", "separate proxy and API credentials".'
allowed-tools: Read, Grep, Write, Edit, Bash(python:*)
version: 2.0.0
argument-hint: "[integration-root]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- install-auth
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Access Bootstrap

## Overview

Establish the product, identity, zone, target, and secret boundaries before any live collection. Native proxy clients use a zone username/password, while REST API clients use a named-user API key; treat them as different credentials with different blast radii.

## Prerequisites

- An approved public-data purpose and target allowlist
- A Bright Data account owner who can grant only the required product and zone
- A secret manager and a non-production validation environment

## Instructions

### Step 1: Inventory the access path

Read the integration and Grep for existing Bright Data hosts, environment names, and secret references. Classify each call as native proxy, Browser API, or REST API before choosing credentials.

### Step 2: Define the secret contract

Write an example-only configuration that declares names but contains no values.

```dotenv
BRIGHTDATA_API_KEY=
BRIGHTDATA_PROXY_USERNAME=
BRIGHTDATA_PROXY_PASSWORD=
BRIGHTDATA_ZONE=
```

### Step 3: Bind ownership

Record the named owner, permitted zone, approved target classes, expiry or review condition, and revocation path. Do not reuse an account-wide API key when a zone credential is sufficient.

### Step 4: Validate without disclosure

Use Bash(python:*) only to check that required names are present and mutually consistent; never print values. Run one separately approved smoke test through the product-specific workflow.

## Tool Discipline

Use Read and Grep to inventory existing access. Use Write and Edit only for approved example, configuration, and runbook paths. Use Bash(python:*) for local presence/schema checks that never print secret values; this skill does not authorize a live request.

## Output

- Credential-mode decision: native proxy or REST API
- Named secret bindings, owner, scope, and revocation receipt
- An approved smoke-test handoff with no credential material

## Examples

For a Web Scraper API worker, bind one named-user API key in the deployment secret manager and keep proxy username/password variables absent. For a Playwright proxy client, bind only the approved zone credentials. Stop if the product or target authorization is ambiguous.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| Both credential modes are populated | Integration boundaries are mixed | Split the clients and remove unused secrets |
| Zone is inactive or missing | Wrong account, spelling, or entitlement | Have the account owner verify the zone; do not broaden access |
| Secret appears in logs | Unsafe diagnostics or command construction | Revoke it, scrub retained output, and correct the logging path |

## Resources

- [Authentication and API keys](https://docs.brightdata.com/api-reference/authentication)
- [Proxy API authentication](https://docs.brightdata.com/api-reference/proxy/proxy_api_auth)
- [Users management](https://docs.brightdata.com/general/account/users-management)
- [Acceptable use policy](https://docs.brightdata.com/general/policy/acceptable-use-policy)
