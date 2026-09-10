---
name: miro-data-handling
description: "Analyze and execute this workflow: govern Miro reads, storage, exports, redaction, retention, and deletion by purpose and data class. Use when processing collaborative board content. Trigger with \"miro board data handling\"."
argument-hint: "[workflow] [data-class]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- privacy
- data-governance
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Board Data Handling

## Overview

Assume collaborative canvases can contain personal, confidential, regulated, or credential-like material; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Approved Miro application, tenant, and board scope
- Current repository and deployment evidence
- Named owner, success criteria, and rollback or recovery boundary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Board read scope can expose metadata, members, and item content.
- Resource URLs and payloads must not enter logs or debug bundles.
- Enterprise export/audit/organization scopes require plan and role checks.
- Stored Miro data needs application-layer authentication and authorization.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Map each field to purpose, source, class, owner, destination, retention, and deletion.
2. Minimize boards, item types, fields, windows, and tenants.
3. Pseudonymize operational identifiers and keep content out of telemetry.
4. Enforce tenant authorization, encryption, access logs, expiry, and deletion paths.
5. Test deletion, revoked access, cross-tenant denial, redaction, and backup expiry.
6. Block any field without purpose, owner, retention, or access policy.

## Approval Boundaries

Exporting, persisting, training on, or transmitting board content requires data-owner, privacy, and security approval. Pause when the responsible owner or exact target is uncertain.

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
boards=12; stored=id,type,hash; content=no; deletion=passed; cross-tenant=denied
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Scopes](https://developers.miro.com/reference/scopes)
- [Security guidelines](https://developers.miro.com/docs/security-guidelines)
