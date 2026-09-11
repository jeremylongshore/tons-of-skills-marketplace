---
name: lucidchart-ci-integration
description: 'Gate Lucid REST, Standard Import, and Extension API changes with deterministic checks. Use when adding CI to a Lucid integration. Trigger with "add Lucid CI".'
argument-hint: "[project-path] [integration-kind]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, ci, extensions, standard-import]
model: inherit
effort: medium
compatibility: Designed for Claude Code; live verification requires an authorized Lucid developer project and approval from the document, application, or account owner
---
# Lucid Integration CI Gate

## Overview

Build a secretless pull-request gate and a separately approved live verification lane for Lucid integrations.

## Prerequisites

- The integration kind: REST API, Standard Import, editor extension, or data connector
- Repository ownership rules and sanitized fixtures
- Current Lucid documentation for every API version, scope, and package command used

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect manifests, import archives, code, tests, and workflows. Use `WebFetch` only for current official Lucid pages. Use `Write` or `Edit` only within the approved repository scope.

## Current Contract

- REST requests use Bearer authorization and a valid resource-specific `Lucid-Api-Version`.
- Standard Import archives contain `document.json`; their rendered result can change as the format evolves.
- Official extension builds use `lucid-package`; pull-request jobs do not need production tokens.

## Authentication

Keep API keys, OAuth client secrets, access tokens, refresh tokens, authorization codes, and account tokens out of fork and pull-request jobs. A protected live lane may use only an approved secret, correct token type, least scopes, and exact redirect URI.

## Instructions

1. Classify the integration and list its authoritative manifest, schema, API-version, and scope inputs.
2. Inspect every workflow and fixture with Read, Glob, and Grep.
3. Add schema and archive checks for Standard Import, including unique IDs, required pages, media limits, and path safety.
4. For extensions, run the documented build and bundle commands in a pinned runtime and verify the manifest requests only used scopes.
5. Mock REST responses by endpoint and version; cover 401, 403, 429, 5xx, malformed payload, and timeout behavior.
6. Keep fork jobs synthetic. Put any live smoke test behind protected-environment approval and cleanup.
7. Save a redacted receipt naming inputs, versions, checks, and remaining manual verification.

## Approval Boundaries

Do not expose secrets to untrusted code, mutate real documents from fork CI, or treat mocks as proof of live access.

## Output

Return integration kind, protected paths, checks, fixture provenance, secret exposure count, required contexts, live lane, cleanup, and residual risk.

## Error Handling

| Condition | Response |
|---|---|
| Fork job requests a token | Replace the call with an endpoint-specific fixture. |
| Manifest scope is unused | Remove it and rebuild the bundle. |
| API version is guessed | Fetch the endpoint documentation and fail closed. |

## Example

```text
kind=standard-import; fixtures=3; fork-secrets=0; schema=pass; bundle=pass; live-lane=protected; result=pass
```

## Resources

- [Official documentation map](references/official-docs.md)

## Next Steps

Recheck package releases, endpoint versions, scopes, branch protection, and cleanup before each production release.
