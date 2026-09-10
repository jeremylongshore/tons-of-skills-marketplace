---
name: miro-deploy-integration
description: "Analyze and execute this workflow: deploy a Miro service with isolated configuration, health checks, canaries, and rollback. Use when promoting a Miro-backed release. Trigger with \"miro integration deployment\"."
argument-hint: "[environment] [release-sha]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- deployment
- operations
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Integration Deployment

## Overview

Promote one immutable artifact while keeping authorization configuration and write enablement separately controlled; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Approved Miro application, tenant, and board scope
- Current repository and deployment evidence
- Named owner, success criteria, and rollback or recovery boundary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- OAuth redirects must exactly match the environment's Miro app configuration.
- REST secrets remain server-side and out of Web SDK bundles.
- A read-only context probe precedes write enablement.
- Retired experimental webhooks cannot be a health dependency.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Bind the release to SHA, dependency lock, app hash, scopes, redirects, and environment.
2. Deploy secret references and configuration with Miro writes disabled.
3. Run service health, token-context, and bounded board-read probes.
4. Canary approved tenants against error, latency, credit, and semantic thresholds.
5. Enable writes only after approval and reconcile the first mutations.
6. Exercise rollback and verify all pre-rollback writes.

## Approval Boundaries

Production deployment, tenant rollout, redirect/scope changes, and write enablement require explicit owner approval. Pause when the responsible owner or exact target is uncertain.

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
sha=4b6a2de; env=staging; context=matched; canary=5; writes=off; rollback=passed
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [OAuth guide](https://developers.miro.com/docs/getting-started-with-oauth)
- [Security guidelines](https://developers.miro.com/docs/security-guidelines)
