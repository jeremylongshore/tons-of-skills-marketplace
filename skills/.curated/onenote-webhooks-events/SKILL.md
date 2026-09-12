---
name: onenote-webhooks-events
description: >-
  Design bounded OneNote change detection without claiming unsupported webhooks or delta queries. Use when a workflow must discover page changes on a documented polling schedule. Trigger with "monitor OneNote changes", "poll OneNote safely", or "reconcile OneNote pages".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<approved-sections> <freshness-objective> <checkpoint-store>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, reconciliation]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Change Polling and Reconciliation

## Overview

Design bounded OneNote change detection without claiming unsupported webhooks or delta queries.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

OneNote resources are absent from the current Microsoft Graph supported lists for change notifications and delta query. Use scheduled, section-scoped page metadata reads with complete next-link traversal, overlap windows, periodic full reconciliation, and an explicit freshness contract. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Run as an approved delegated user bound to tenant, environment, and roots. Store checkpoints and metadata without page bodies unless content access is separately approved.

## Instructions

1. Define approved sections, freshness objective, overlap window, deletion strategy, and reconciliation cadence.
2. Capture an initial complete per-section page metadata manifest using selected fields and every next link.
3. Poll each section on a bounded schedule and compare stable page IDs plus documented modification metadata.
4. Use overlap and deduplication so clock skew or partial runs do not drop changes.
5. Checkpoint only after all pages and downstream acknowledgements for the cycle succeed.
6. Run periodic full reconciliation and surface deletions, moves, denied sections, and unsupported assumptions.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require content and workload owners before polling. Any page-body retrieval, downstream write, broadened root, or deletion action requires separate approval.

## Error Handling

- Do not call OneNote resources through the Graph subscriptions endpoint.
- Do not call an undocumented OneNote delta route.
- Do not advance a checkpoint after partial paging or downstream failure.

## Output

Return the support evidence, polling contract, checkpoint schema, page ledger, deduplication rules, freshness metrics, reconciliation, and gaps. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Recover a partial cycle from the prior committed checkpoint.
- Detect a moved or inaccessible page during full reconciliation without inventing a delete event.

## Validation

Exercise and record these paths with expected and observed results:

- multi-page cycle
- clock overlap
- duplicate
- partial failure
- denied section
- full reconciliation

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
