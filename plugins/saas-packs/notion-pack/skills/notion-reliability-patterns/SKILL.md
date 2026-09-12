---
name: notion-reliability-patterns
description: >-
  Analyze and apply retry, idempotency, checkpoint, circuit, dead-letter, and reconciliation patterns to a specific Notion operation. Use when hardening failure recovery. Trigger with "harden Notion reliability", "make Notion writes idempotent", or "design Notion recovery".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<operation> <failure-model> <recovery-objective>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, reliability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Reliability Pattern Selection

## Overview

Analyze and apply retry, idempotency, checkpoint, circuit, dead-letter, and reconciliation patterns to a specific Notion operation.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Reliability behavior depends on whether an operation is a read, create, update, webhook signal, paginated extraction, file lifecycle, or downstream side effect. Retry safety cannot be inferred from HTTP method alone. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Recovery stores and dead letters must protect workspace content and tenant identifiers to the same standard as the primary system.

## Instructions

1. Define success, acknowledgement, idempotency identity, checkpoint, timeout ambiguity, and compensation for the operation.
2. Classify permanent, transient, rate, conflict, access, and unknown failures.
3. Select bounded retry, idempotency record, lease, circuit, dead letter, or reconciliation only where its invariant is explicit.
4. Persist response identity before acknowledging creates and destination state before advancing read checkpoints.
5. Exercise duplicate, reorder, timeout, crash, poison item, and partial downstream failure.
6. Document operator recovery, replay authorization, observability, and rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require operation-owner approval for dead-letter replay, checkpoint rewind, backfill, compensation, or bypassing a circuit. Record the approver and bounded recovery window before execution.

## Error Handling

- Do not retry a timed-out create without deduplication evidence.
- Do not drop poison items to keep a queue green.
- Do not use stale cached content as an authoritative write source.

## Output

Return the operation state machine, invariants, retry matrix, recovery stores, test evidence, runbook, and residual risks. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Recover a timed-out page create without duplication.
- Resume a multi-page read after a worker crash without gaps.

## Validation

Exercise and record these paths with expected and observed results:

- duplicate
- timeout ambiguity
- out of order
- poison item
- checkpoint rewind
- circuit recovery

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
