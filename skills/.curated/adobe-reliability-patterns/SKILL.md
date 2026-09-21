---
name: adobe-reliability-patterns
description: >-
  Analyze and design idempotency, bounded polling, per-service circuits, durable queues, DLQ/replay, degradation, and reconciliation for Adobe workloads. Use when the task requires adobe async reliability controls. Trigger with "Adobe reliability", "Firefly retry design", or "PDF job recovery".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<services> <failure-model> <recovery-objectives>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, reliability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Async Reliability Controls

## Overview

Analyze and design idempotency, bounded polling, per-service circuits, durable queues, DLQ/replay, degradation, and reconciliation for Adobe workloads. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Adobe services fail independently and async submission may succeed before the caller sees a response. Reliability is a state machine: planned, approved, submitted, acknowledged, running, terminal, artifact verified, downstream acknowledged, and cleaned. Unknown is not failed or safe to replay. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Idempotency records and job evidence use aliases and hashes, never tokens, signed URLs, or content. Credential failure and content/policy failure have different containment owners.

## Instructions

1. Map operations, side effects, states, identifiers, retryability, time budgets, dependencies, and reconciliation sources.
2. Create per-service circuits and queues so one Adobe product does not exhaust all workers.
3. Persist submission intent before network call and bind returned job/status/cancel evidence atomically.
4. Poll returned status URLs with jitter, terminal-state validation, cancellation, and strict elapsed-time budget.
5. Route exhausted/unknown work to quarantine or DLQ; replay only after reconciliation and approval.
6. Exercise crashes, timeouts, 429/5xx, revocation, vendor outage, duplicate events, and recovery objectives.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Workload owner approves replay/degradation; budget owner approves resubmission; data owner approves artifact custody; security owns credential failures; cancellation/deletion require explicit approval.

## Error Handling

- No fixed timeout table substitutes for measured objectives.
- Never retry unknown submissions blindly.
- Fallback output must be labeled and must not bypass policy or approval.

## Output

Return state model, retry/idempotency matrix, circuit/queue design, reconciliation and replay runbooks, drills, SLOs, and owners. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Recover after a crash between submission and response persistence.
- Reconcile an unknown job before approved replay.

## Validation

Exercise and record expected and observed results for:

- 429
- 5xx
- ambiguous timeout
- credential revocation
- duplicate event
- vendor outage

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
