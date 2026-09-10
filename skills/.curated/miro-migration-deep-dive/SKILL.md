---
name: miro-migration-deep-dive
description: "Analyze and execute this workflow: migrate v1 widgets and relationships to v2 item endpoints with translation, shadow comparison, and rollback. Use when modernizing a legacy Miro REST integration. Trigger with \"miro v1-to-v2 resource migration\"."
argument-hint: "[legacy-surface] [cohort]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- migration
- rest-v2
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro v1-to-v2 Resource Migration

## Overview

Modernize legacy resources without changing OAuth unnecessarily or flattening distinct v2 item schemas; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Approved Miro application, tenant, and board scope
- Current repository and deployment evidence
- Named owner, success criteria, and rollback or recovery boundary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- OAuth `/v1/oauth` is outside the resource migration.
- v2 replaces generic widgets with item-type endpoints.
- Connection objects became direct actions such as sharing.
- Several collections changed from offset to cursor pagination.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Inventory v1 endpoints, widgets, connections, pagination, timestamps, and consumers.
2. Map each operation to official v2 behavior and record no-equivalent cases.
3. Build typed translators retaining IDs, types, relationships, and unsupported fields.
4. Run v1/v2 shadow reads and compare normalized semantic state.
5. Canary bounded writes with read-after-write and rollback.
6. Cut over incrementally and remove v1 resource code only after retained evidence.

## Approval Boundaries

Bulk board copies, sharing changes, v1 data deletion, and OAuth changes require service and board-owner approval. Pause when the responsible owner or exact target is uncertain.

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
v1-calls=14; mapped=12; redesigned=2; shadow=4300-equal; canary=3; legacy=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [REST comparison](https://developers.miro.com/docs/rest-api-comparison-guide)
- [Reference guide](https://developers.miro.com/docs/rest-api-reference-guide)
