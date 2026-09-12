---
name: ideogram-upgrade-migration
description: >-
  Upgrade an Ideogram adapter against current OpenAPI and endpoint contracts while preserving rollback. Use when moving versions, fields, or transport behavior without redesigning the product workflow. Trigger with "upgrade Ideogram API", "check Ideogram schema drift", or "migrate an Ideogram endpoint".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<current-contract> <target-contract> <traffic-slice>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, migration]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live cutover requires change approval and paid canaries"
---
# Ideogram Contract Upgrade

## Overview

Move a bounded adapter contract to a current Ideogram route without mixing the change with a broad product migration. Diff OpenAPI and endpoint documentation, update owned types and fixtures, run shadow comparisons, and preserve an explicit traffic rollback.

## Prerequisites

- Current adapter SHA, endpoint inventory, target contract, consumers, and accountable owner.
- Captured sanitized fixtures and compatibility requirements.
- Canary budget, traffic control, storage parity, and rollback deadline.

## Current Contract

The current surface spans V4, P-Image, V3, outcome-focused tools, custom training, and routes labeled Legacy Endpoints. V4 generation uses endpoint-specific multipart forms; `text_prompt` and `json_prompt` are mutually exclusive, and current V4 `FLASH` support must not be inferred from V3 examples.

## Authentication

Keep the same server-side `Api-Key` boundary unless a documented first-party auth change is part of the reviewed diff. Never copy production credentials or payloads into migration fixtures.

## Instructions

1. Inventory current routes, methods, fields, enums, errors, async states, safety fields, and downstream storage assumptions.
2. Retrieve current OpenAPI and endpoint docs, then classify additive, changed, deprecated, legacy, and undocumented differences.
3. Update owned types and route adapters while preserving unknown fields needed for drift detection.
4. Build sanitized before-and-after fixtures for success, unsafe output, validation, throttling, capacity, webhook, polling, and URL expiry.
5. Run offline contract tests and a staging shadow that does not double-publish or overwrite assets.
6. Canary a bounded live slice within an approved credit ceiling and compare status, latency, safety, output count, and storage outcomes.
7. Promote only after convergence; retain the prior route and state reconciliation until the rollback window closes.

## Tool Discipline

Use Read, Glob, and Grep for routes, schemas, consumers, and fixtures. Use Write and Edit for approved adapter, test, and migration documentation changes. Do not change live traffic or run parallel paid generation without approval.

## Approval Boundaries

Require owners for endpoint choice, compatibility exceptions, model or rendering changes, extra spend, safety differences, and production cutover. Removing a legacy route requires proof that no consumer or in-flight generation depends on it.

## Error Handling

- Stop when the target schema is undocumented or response safety fields cannot be reconciled.
- Do not coerce a V3 enum into V4 merely because names look similar.
- On canary divergence, halt target traffic, preserve identifiers, and reconcile stored assets before rollback.

## Output

Return source and target contracts, diff classes, changed files, test matrix, shadow and canary metrics, spend, unresolved drift, traffic state, and rollback receipt. Exclude content, credentials, and URLs.

## Examples

- Replace a legacy `/generate` adapter with V4 multipart behind a feature flag.
- Reject a migration that blindly carries `FLASH` into the current V4 request.

## Validation

Re-run contract, consumer, storage, and rollback tests against immutable SHAs. Verify the deployed traffic split and confirm no duplicate objects, orphaned generations, or retained temporary URLs remain.

## Resources

- [Current first-party evidence map](references/official-docs.md)
