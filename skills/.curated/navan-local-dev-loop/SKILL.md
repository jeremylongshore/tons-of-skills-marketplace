---
name: navan-local-dev-loop
description: >-
  Develop Navan integrations against sanitized contract fixtures with networking denied by default. Use when changing adapters, mappings, or reconciliation logic. Trigger with "develop Navan locally", "mock Navan data", or "add Navan fixtures".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <fixture-set> <test-command>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, development]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Offline Development Loop

## Overview

Develop Navan integrations against sanitized contract fixtures with networking denied by default. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Local development should exercise the application-owned contract, not depend on a live tenant. Fixtures must preserve structural edge cases while removing traveler, payment, itinerary, and credential data.

## Authentication

Local tests require no Navan credential. An optional live smoke uses a separate non-production secret and must be explicitly enabled outside the normal test command.

## Instructions

1. Capture a schema from authorized documentation or a sanitized response.
2. Build minimal success, empty, paginated, corrected, denied, throttled, and malformed fixtures.
3. Validate fixtures against local types and sensitivity rules.
4. Run the adapter with networking blocked and a deterministic clock.
5. Exercise mapping, deduplication, checkpoint, and rollback behavior.
6. Keep live smoke configuration separate, bounded, and disabled by default.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Live tenant access, new fixtures derived from real data, dependency changes, and fixture publication require explicit approval.

## Error Handling

- Never commit raw tenant responses.
- A fixture that contains plausible personal data still needs review.
- Fail when an offline test unexpectedly opens a socket.

## Output

Return fixture provenance, covered contracts, test results, network-denial evidence, uncovered fields, and optional live-smoke plan. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Model a late booking correction with synthetic identifiers.
- Test an expense reversal without a real receipt.

## Validation

Scan fixtures for secrets and personal data, run twice for determinism, and verify a network attempt fails. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
