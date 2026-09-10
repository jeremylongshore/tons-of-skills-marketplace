---
name: miro-core-workflow-a
description: "Analyze and execute this workflow: plan and execute governed Miro board and item mutations with preconditions, bounded batches, and rollback evidence. Use when creating or changing Miro content. Trigger with \"update Miro board\"."
argument-hint: "[board-id] [requested-change]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- boards
- items
- writes
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Governed Board and Item Writes

## Overview

Convert a requested canvas change into an explicit write set. Confirm board identity and permissions before any mutation, then reconcile what Miro actually persisted; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Approved target board and expected team
- OAuth installation with only the required board scopes
- Desired state, ownership, rollback, and collision policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Board and item writes require `boards:write`; reads use `boards:read`.
- The v2 API exposes item-type endpoints rather than the polymorphic v1 widget model.
- Bulk item creation accepts at most twenty items, is transactional, and charges Level 2 credits per item.
- A successful mutation response must be followed by a read when persisted state matters.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Resolve token context, team, board, and current permissions; stop on any mismatch.
2. Read the target objects and calculate a deterministic create/update/delete plan.
3. Present counts, affected types, destructive actions, credit estimate, and rollback before writing.
4. Apply the smallest approved operation or a maximum-twenty-item transactional bulk create.
5. Re-read affected IDs and compare normalized desired versus observed state.
6. Return a redacted receipt and rollback outcome; never retry an ambiguous write blindly.

## Approval Boundaries

Require explicit approval for board creation/deletion, sharing changes, member changes, or deleting/replacing existing items. Do not infer a target from a board name alone. Pause when the responsible owner or exact target is uncertain.

## Output

Return board/team confirmation, planned and applied counts by item type, credit estimate, reconciliation result, rollback handle, and exceptions. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| 409 conflict | Re-read state, recompute the plan, and request approval if intent changes. |
| Ambiguous timeout | Search or re-read by known IDs/markers before retrying. |
| Bulk create fails | Treat the operation as uncommitted, then verify before any replay. |
| Permission changed mid-run | Stop remaining writes and preserve completed-action evidence. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
board=hash:8d2; create=6; update=2; delete=0; estimated-credits=800; reconciled=8/8; rollback=ready
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Create items in bulk](https://developers.miro.com/reference/create-items)
- [Create board](https://developers.miro.com/reference/create-board-1)
