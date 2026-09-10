---
name: miro-ci-integration
description: "Analyze and execute this workflow: build hermetic and bounded live Miro CI gates with schema-faithful fixtures, test-board isolation, and cleanup proof. Use when adding Miro checks to CI. Trigger with \"test Miro in CI\"."
argument-hint: "[pipeline] [test-scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- ci
- testing
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro CI Contract Tests

## Overview

Keep pull-request checks credential-free and reserve live Miro calls for protected, explicitly scoped lanes. A test must never mutate a collaboration board by accident; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- CI trust-boundary and fork policy
- Pinned schemas/fixtures and test command
- Dedicated app, team, board, identity, and cleanup owner for live tests

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Untrusted fork workflows must not receive Miro credentials.
- Live traffic consumes production-like per-user/application credits even on test resources.
- Bulk create is transactional but cleanup still needs an explicit inventory and board guard.
- OAuth refresh rotation can invalidate concurrent jobs sharing one installation.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Split formatting, unit, schema, security, and fixture tests from the protected live lane.
2. Assert that PR/fork lanes have no credential context and cannot invoke live helpers.
3. Pin dependencies and validate captured fixtures against current official response contracts.
4. Serialize protected live jobs per installation, assert app/team/board guards, and use bounded read-first tests.
5. Mark any created item with the run identity, reconcile it, then clean only confirmed run-owned IDs.
6. Fail the gate on leaked data, ambiguous writes, cleanup residue, unexpected schema, or quota-policy breach.

## Approval Boundaries

Do not expose credentials to forks, share one rotating token across parallel jobs, or enable destructive live tests without repository and board-owner approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return lane/trust map, fixture provenance, protected-resource guards, test results, credits used, cleanup receipt, and gate conclusion. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Fork lane can read secrets | Disable the live path and repair workflow permissions before merging. |
| Refresh collision occurs | Serialize jobs or isolate installations. |
| Cleanup cannot prove ownership | Leave content intact and fail the lane. |
| Rate headroom is low | Skip live mutations and report capacity pressure. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
unit=46/46; schemas=12/12; fork-secrets=0; live-read=passed; live-writes=0; cleanup-residue=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [OAuth guide](https://developers.miro.com/docs/getting-started-with-oauth)
- [Rate limits](https://developers.miro.com/reference/rate-limiting)
