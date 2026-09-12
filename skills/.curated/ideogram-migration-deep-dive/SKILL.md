---
name: ideogram-migration-deep-dive
description: >-
  Plan and execute a staged migration across Ideogram legacy, V3, V4, P-Image, and tool endpoints with semantic comparison and rollback. Use when modernizing a production image workflow. Trigger with "migrate Ideogram legacy API", "move Ideogram V3 to V4", or "redesign an Ideogram image pipeline".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<source-surface> <target-surface> <migration-window>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, migration]
model: inherit
effort: high
compatibility: "Designed for Claude Code; dual-run generation requires an approved cost and data plan"
---
# Ideogram Production Migration

## Overview

Modernize a complete Ideogram image workflow without assuming endpoint names imply equivalent semantics. Inventory legacy and V3 behavior, select V4, P-Image, or outcome-focused tools by requirement, compare safe durable results, and preserve in-flight state and rollback.

## Prerequisites

- Source routes, payloads, traffic, consumers, stored assets, async state, quality rubric, and owners.
- Target use cases, model-control needs, latency, safety, rights, cost, and retention constraints.
- Feature flags, shadow destination, reconciliation plan, canary budget, and rollback window.

## Current Contract

First-party navigation labels `/generate`, `/edit`, `/remix`, `/reframe`, and `/describe` as Legacy Endpoints. Current surfaces include V3, V4 sync/async/transparent, P-Image, edit, remix, structured describe, magic prompt, outcome-focused tools, and custom training. Payload and rendering semantics differ.

## Authentication

Preserve the server-side `Api-Key` boundary and environment isolation throughout migration. Dual-run fixtures and receipts must exclude keys, prompts, uploaded images, generated assets, and temporary URLs.

## Instructions

1. Inventory each source route, field, enum, output, error, retry, safety, storage, consumer, and in-flight state.
2. Classify every use case by required model control, transparency, edit semantics, structured prompting, specialized outcome, latency, and cost.
3. Select a documented target route for each use case; record non-equivalence and retire unsupported assumptions.
4. Build owned translation at the application boundary instead of leaking mixed legacy and target schemas to consumers.
5. Compare sanitized fixtures, then run approved shadow or dual generation into isolated storage without double publication.
6. Evaluate transport, safety, useful quality, latency, cost, URL persistence, async reconciliation, and deletion.
7. Canary by tenant or use case, reconcile every known generation and asset, then remove legacy traffic only after the rollback window.

## Tool Discipline

Use Read, Glob, and Grep for routes, consumers, schemas, state, and evidence. Use Write and Edit for approved migration code, tests, and records. Do not dual-run paid customer traffic or delete legacy assets by invocation alone.

## Approval Boundaries

Require owners for target selection, model or quality changes, dual-run spend, customer-derived content, safety differences, cutover, and destructive retirement. A migration with no state and asset reconciliation plan is not ready.

## Error Handling

- Do not map legacy enums or rendering speed by string similarity.
- Stop on unexplained safety, output-count, aspect, storage, or quality divergence.
- On rollback, halt target admission first and reconcile accepted target work before restoring source traffic.

## Output

Return source inventory, target mapping, semantic gaps, translated contracts, fixture and shadow results, safety, quality, latency, spend, canary state, reconciled identifiers, retirement evidence, and rollback receipt.

## Examples

- Move legacy generation to V4 multipart while keeping consumer response compatibility behind an adapter.
- Replace a broad edit flow with a specific background or reframe tool only when direct model control is unnecessary.

## Validation

Run source and target contracts against the same approved synthetic cases, review visual quality separately from transport, verify durable storage and deletion, and exercise rollback under in-flight load.

## Resources

- [Current first-party evidence map](references/official-docs.md)
