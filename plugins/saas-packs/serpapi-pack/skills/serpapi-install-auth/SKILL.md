---
name: serpapi-install-auth
description: 'Install an official SerpAPI client, configure the private API key for server-side use, and verify account access without leaking credentials. Use when starting or repairing a SerpAPI integration. Trigger with "configure SerpAPI access".'
argument-hint: "[python|javascript] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit, Bash(python3:*), Bash(npm:*), Bash(curl:*)
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, authentication, python, javascript]
model: inherit
effort: medium
compatibility: Designed for Claude Code; package installation, secret creation, account access, and live searches require operator approval
---
# SerpAPI Client Installation and Authentication

## Overview

Select an official client, keep the private key server-side, and prove access with the free Account API before spending a search.

## Prerequisites

- A SerpAPI account and private key from the account dashboard
- Python or Node.js project ownership and an approved secret store
- A named environment and owner for usage, rotation, and revocation

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect dependency and configuration files, `WebFetch` to re-check official client and Account API documentation, `Write` or `Edit` for secretless configuration, and `Bash(python3:*)`, `Bash(npm:*)`, or `Bash(curl:*)` only after the operator approves installation or a live check.

## Current Contract

SerpAPI's current official packages are `serpapi` for Python and `serpapi` for JavaScript. Search and Account APIs authenticate with the private `api_key`. The Account API reports current quota and throughput fields and does not count against the monthly search allowance.

## Authentication

Store the key as `SERPAPI_KEY` in a server-side secret manager. Never commit it, expose it to browser code, print it, place it in a fixture, or persist a command containing it in shell history. Do not assume OAuth, scopes, or multiple independently scoped keys unless current account documentation confirms them.

## Instructions

1. Inspect the runtime, package manager, existing SerpAPI packages, `.gitignore`, secret-loading convention, and deployment environment.
2. Re-fetch the official Python or JavaScript client documentation and pin a version under the repository's dependency policy.
3. Present the dependency and secret-store changes before installing anything.
4. Install with `python3 -m pip install serpapi` or `npm install serpapi` after approval.
5. Add `SERPAPI_KEY` to the approved local and deployment secret stores; add only variable names and redacted examples to tracked files.
6. Verify access through the official client Account API and retain only non-secret fields such as account status, plan name, searches left, and hourly throughput.
7. Run a live search only when the operator explicitly accepts that it may consume allowance.

## Output

Return the selected client and pinned version, changed files, secret-store location, redacted Account API receipt, live-search decision, and rotation/revocation owner.

## Error Handling

| Condition | Response |
|---|---|
| `401 Unauthorized` | Confirm that the correct secret is loaded; never echo the value. |
| `403 Forbidden` | Treat the account as unauthorized or disabled and stop. |
| `429 Too Many Requests` | Query Account API to distinguish hourly throughput from exhausted searches. |
| Package collision | Remove legacy packages only through a reviewed migration plan. |

## Example

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=10)
account = client.account()
print({key: account.get(key) for key in (
    "account_status", "plan_name", "plan_searches_left",
    "account_rate_limit_per_hour",
)})
```

## Resources

- [Official Python client](https://github.com/serpapi/serpapi-python)
- [Official JavaScript client](https://github.com/serpapi/serpapi-javascript)
- [Account API](https://serpapi.com/account-api)

## Next Steps

Run the hello-world workflow with a harmless query and record its search ID without recording the key.
