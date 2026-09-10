---
name: miro-prod-checklist
description: "Analyze and execute this workflow: run a fail-closed Miro production-readiness review across authorization, data, resilience, rollback, and operations. Use when preparing to enable a Miro integration in production. Trigger with \"ship Miro integration\"."
argument-hint: "[release-sha] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- production
- release
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Production Readiness Gate

## Overview

Turn production approval into an evidence-backed decision bound to one immutable release and app configuration; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Immutable release candidate and deployment manifest
- Production app/team ownership and approved scopes
- Test, observability, incident, rollback, and data-handling evidence

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Production REST uses v2 resource endpoints and OAuth under `/v1/oauth`.
- Experimental features are not production contracts and must be isolated behind explicit risk acceptance.
- Rate capacity is credit-weighted and must include all callers for a user/application pair.
- Miro service status, token revocation, and tenant mismatch need operational responses before launch.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Bind the review to release SHA, dependency lock, app ID hash, scopes, redirect URIs, and environment.
2. Verify tenant isolation, expiring-token rotation, revocation, least privilege, and redaction controls.
3. Run unit, contract, bounded live-read, failure, rate, rollback, and recovery tests.
4. Confirm dashboards, alerts, runbooks, owner/on-call, status dependency, retention, and support escalation.
5. List every mutation and experimental dependency; require an explicit disposition for each.
6. Issue GO only when all blocking evidence is current; otherwise return NO-GO with owners and retest criteria.

## Approval Boundaries

Production deployment, new app installation, scope changes, initial write enablement, and risk acceptance require the designated owners' explicit approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return GO/NO-GO, immutable identity, gate table, evidence links, approvals, rollback trigger, residual risks, and expiry date. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Release identity changes | Invalidate the approval and rerun affected gates. |
| Evidence is missing or stale | Return NO-GO. |
| Rollback is untested | Return NO-GO for write-capable releases. |
| Experimental dependency is undisclosed | Stop and route for explicit risk review. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
sha=8f2c1a7; env=prod; gates=18/18; scopes=approved; rollback=passed; experimental=0; decision=GO
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Lifecycle policy](https://developers.miro.com/docs/lifecycle-policy)
- [Miro status](https://status.miro.com/)
