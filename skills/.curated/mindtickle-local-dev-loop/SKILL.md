---
name: mindtickle-local-dev-loop
description: 'Build a fast, secret-free local development loop for a Mindtickle adapter using frozen tenant-contract fixtures. Use when developing without live learner data. Trigger with "set up Mindtickle local development".'
argument-hint: "[project-path] [contract-fixture]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, local-development, fixtures, testing]
model: inherit
effort: medium
compatibility: Designed for Claude Code; live tenant access is outside the local loop and requires separate approval
---
# Mindtickle Contract-Fixture Development Loop

## Overview

Make adapter development deterministic by separating domain behavior from the tenant transport and exercising only sanitized, versioned fixtures locally.

## Prerequisites

- An authorized tenant contract digest and sanitized success and failure examples
- A product-specific adapter boundary from `mindtickle-sdk-patterns`
- A secret scanner and repository policy for generated or confidential artifacts

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code and fixtures, `WebFetch` only to refresh approved contract sources, and `Write` or `Edit` for local adapters, fixtures, tests, and documentation.

## Current Contract

Public Mindtickle pages establish API families but not a public emulator or universal SDK. Local mode must therefore emulate the frozen customer contract, identify synthetic values clearly, and fail closed when an unrecorded operation appears.

## Authentication

Local mode accepts no real credential. Represent auth outcomes with synthetic fixtures and reserve any tenant smoke test for a separately approved integration lane.

## Instructions

1. Record the contract digest, fixture provenance, sanitization method, and supported operation list.
2. Route domain code through the adapter interface; reject direct network calls outside the transport module.
3. Add deterministic fixtures for success, empty results, pagination, validation, authorization, throttling signal, timeout ambiguity, and schema drift.
4. Validate fixtures against internal schemas and scan them for secrets and identifying data.
5. Provide a fake clock, stable identifiers, bounded randomness, and deterministic retry scheduling.
6. Run focused tests after every change and compare normalized outputs rather than vendor-specific ordering unless documented.
7. Fail the local server when code requests an unknown route, tenant, or fixture instead of silently returning a generic response.
8. Document the exact command, expected test count, contract expiry, and handoff to the integration lane.

## Approval Boundaries

Do not copy production responses wholesale, enable fallback network access, or accept real tokens in local mode.

## Output

Return the adapter boundary, fixture inventory and digest, sanitization receipt, deterministic commands, test results, unsupported operations, and contract refresh date.

## Error Handling

| Condition | Response |
|---|---|
| Fixture contains sensitive data | Quarantine and replace it with a minimal synthetic case. |
| Contract and fixture diverge | Fail tests and update through the authorized contract-change workflow. |
| Code attempts live access | Block the request and report the calling path. |

## Example

```text
contract-sha256=...; fixtures=8; synthetic=true; secrets=0; tests=24-pass; network=blocked
```

## Resources

- [Mindtickle integrations and API families](https://www.mindtickle.com/platform/integrations/)
- [Mindtickle Trust](https://www.mindtickle.com/trust/)

## Next Steps

Promote the same fixtures to CI and keep the live smoke lane explicitly opt-in.
