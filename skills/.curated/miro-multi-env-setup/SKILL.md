---
name: miro-multi-env-setup
description: "Analyze and execute this workflow: separate Miro development, staging, and production apps, redirects, tokens, teams, and boards with hard guards. Use when configuring multiple environments. Trigger with \"miro multi-environment isolation\"."
argument-hint: "[environments] [deployment-model]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- environments
- configuration
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Multi-Environment Isolation

## Overview

Make environment confusion detectable before a request leaves the process; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Approved Miro application, tenant, and board scope
- Current repository and deployment evidence
- Named owner, success criteria, and rollback or recovery boundary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Each app has independent identity, redirects, scopes, token mode, and installations.
- Access-token context must match the intended tenant.
- Production credentials never belong in local or preview environments.
- Token-expiration mode can differ because it is fixed at app creation.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Build an environment matrix of app hash, redirects, token mode, scopes, team, boards, store, and owner.
2. Fail startup on missing, duplicated, or inconsistent mappings.
3. Resolve credentials only through each environment's approved server-side reference.
4. Assert token context before enabling operations.
5. Test that production identifiers cannot appear in lower-environment config.
6. Exercise rotation, revocation, promotion, and rollback per environment.

## Approval Boundaries

Creating/installing production apps, copying tokens, and changing production redirects/scopes require explicit owner approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return scope, observed contract, proposed or completed actions, verification evidence, approvals, residual risks, and next owner. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Tenant or board context mismatches | Stop before mutation and quarantine the credential mapping. |
| Current docs contradict the implementation | Treat the official current contract as a blocker and design an explicit migration. |
| A mutation result is ambiguous | Reconcile state before retrying. |
| Required evidence is unavailable | Return a blocked decision with the smallest safe next probe. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
envs=3; unique-apps=3/3; context=3/3; cross-env-tests=passed; drift=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Token context](https://developers.miro.com/reference/get-access-token-context)
- [OAuth guide](https://developers.miro.com/docs/getting-started-with-oauth)
