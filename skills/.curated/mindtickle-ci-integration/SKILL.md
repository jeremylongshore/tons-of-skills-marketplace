---
name: mindtickle-ci-integration
description: 'Create a fail-closed CI lane for a Mindtickle adapter using contract fixtures, secret scanning, and an explicitly gated tenant smoke test. Use when hardening integration delivery. Trigger with "test Mindtickle in CI".'
argument-hint: "[project-path] [ci-provider]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, ci, contract-testing, security]
model: inherit
effort: high
compatibility: Designed for Claude Code; CI secrets, protected environments, and tenant smoke tests require repository and tenant-owner approval
---
# Fail-Closed Mindtickle Integration CI

## Overview

Gate adapter changes on contract integrity and sanitized behavior while keeping external tenant access isolated, read-only, and manually authorized.

## Prerequisites

- Deterministic local tests and sanitized fixtures from `mindtickle-local-dev-loop`
- Protected branches, pinned CI permissions, a secret scanner, and artifact retention policy
- A separately owned non-production tenant principal if a live smoke lane is justified

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect workflows and dependency locks, `WebFetch` for current CI and tenant contracts, and `Write` or `Edit` for workflow files, tests, and redacted evidence.

## Current Contract

The always-on lane must not depend on a live Mindtickle tenant. A live lane is optional and must use the customer's documented read-only operation, protected environment approval, bounded execution, and redacted logs.

## Authentication

Grant workflow tokens minimal repository permissions. Store any tenant credential in the CI secret provider, restrict it to the protected environment, prevent fork access, and never expose it to pull-request code.

## Instructions

1. Inventory CI triggers, permissions, third-party actions, caches, artifacts, and secret exposure paths.
2. Build an always-on lane for metadata validation, secret scanning, static checks, unit tests, contract fixtures, and generated-content drift.
3. Pin actions and dependencies according to repository policy and reject unreviewed network downloads.
4. Assert fixture sanitization, contract digest, tenant isolation, retry bounds, mutation denial, and stable output.
5. If justified, add a separate manual or protected-main smoke lane using one documented read-only operation and a strict timeout.
6. Ensure fork pull requests never receive tenant secrets and smoke logs record only status and safe identifiers.
7. Test success, missing secret, revoked access, contract mismatch, timeout, and artifact-redaction paths.
8. Record gate names, expected counts, owners, rollback, and credential rotation procedure.

## Approval Boundaries

Do not expose secrets to forks, run live writes, weaken branch protection, or make a tenant-dependent lane mandatory without repository and tenant-owner approval.

## Output

Return the CI threat model, gate graph, permissions, fixture and contract assertions, optional smoke boundary, failure tests, artifact policy, and verification receipt.

## Error Handling

| Condition | Response |
|---|---|
| Fork workflow requests a secret | Deny the secret and run only the fixture lane. |
| Contract digest changes | Fail closed and require the migration workflow. |
| Smoke response is ambiguous | Stop without retrying and reconcile through approved evidence. |

## Example

```text
fixture-lane=required; live-smoke=protected-read-only; fork-secrets=none; contract-digest=matched; gates=all-pass
```

## Resources

- [Mindtickle integrations](https://www.mindtickle.com/platform/integrations/)
- [Mindtickle Trust](https://www.mindtickle.com/trust/)

## Next Steps

Require the CI gate on protected branches and rehearse credential revocation without changing fixture coverage.
