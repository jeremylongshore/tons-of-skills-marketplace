---
name: miro-core-workflow-b
description: "Analyze and execute this workflow: read and reconcile Miro boards and items with cursor-safe pagination, bounded snapshots, and drift reports. Use when syncing or auditing Miro content. Trigger with \"reconcile Miro board\"."
argument-hint: "[board-id] [scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- boards
- reconciliation
- sync
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Board Read and Reconciliation

## Overview

Produce a consistent, bounded view of board state and distinguish indexing delay, pagination defects, and real drift before proposing changes; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Approved board and team scope
- OAuth installation with `boards:read`
- Field, item-type, pagination, freshness, and redaction requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Board collection filters other than team/project can have indexing delay.
- Collection endpoints use cursor pagination where documented; cursor presence, not page fullness, controls continuation.
- Different item types have distinct v2 schemas and must not be collapsed into a v1 widget shape.
- Resource URLs and board content are sensitive and may be time-bound or access-controlled.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Confirm token context and board ownership boundary.
2. Define item types, fields, page/item ceilings, freshness window, and comparison keys.
3. Traverse documented cursors while detecting repeats and enforcing termination limits.
4. Normalize item-specific fields without discarding type or parent relationships.
5. Compare the snapshot with the approved baseline and classify added, changed, missing, and uncertain records.
6. Return a redacted drift report; propose writes separately with a new approval boundary.

## Approval Boundaries

Do not expand from one board/team to an organization-wide inventory, follow download URLs, or persist content beyond the approved purpose without approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return board context, pages/items read, cursor termination reason, freshness caveats, drift counts, uncertain records, and a content-handling receipt. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Cursor repeats | Stop and report an incomplete snapshot. |
| Item type is unknown | Preserve its type and minimal raw structure; do not coerce it. |
| Index lag suspected | Wait a bounded interval and re-read before declaring loss. |
| Read scope is too broad | Reduce filters and fields before continuing. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
board=hash:41a; pages=4; items=263; cursor=end; added=2; changed=1; missing=0; uncertain=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Get items](https://developers.miro.com/reference/get-items)
- [REST comparison](https://developers.miro.com/docs/rest-api-comparison-guide)
