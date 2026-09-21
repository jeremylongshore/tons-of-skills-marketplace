---
name: mistral-common-errors
description: >-
  Diagnose Mistral authentication, validation, throttling, model, transport, and provider failures without unsafe retries. Use when an integration fails. Trigger with "Mistral error", "fix a Mistral 429", or "debug a failed Mistral request".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<status-or-exception> <environment> <request-evidence>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, troubleshooting]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Error Triage

## Overview

Classify failure before changing code or replaying work. Separate local configuration, invalid request, account policy, rate boundary, transient provider, and application parsing failures.

## Prerequisites

- A timestamp, environment, operation, endpoint class, client pin, and sanitized error.
- The application deadline, idempotency class, and retry budget.
- Current endpoint and workspace-limit documentation.

## Current Contract

HTTP and client errors are evidence, not universal retry instructions. Workspace limits are shared across keys and current dimensions belong to the Admin Panel.

## Authentication

Never request or reproduce a key. Confirm only secret-reference resolution, expected host, and environment.

## Instructions

1. Freeze automatic retries and identify ambiguous side effects or state.
2. Normalize status, request ID, endpoint, model, client, attempts, and elapsed time.
3. Validate the request locally against the current endpoint contract.
4. Check account, model access, current usage limits, and billing with authorized evidence.
5. Classify and choose bounded mitigation: fix config/input, wait, reduce demand, or escalate.
6. Reproduce once with synthetic data only when approved; revert temporary diagnostics.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Require approval for replay, limit/spend increase, model substitution, upgrade, or support submission. Never blindly retry stateful work.

## Error Handling

- Repeated `401` calls will not repair a revoked key.
- Aggressive retries after `429` amplify queued demand.
- A timeout after submission may be ambiguous; reconcile before repeating.

## Output

Return classification, sanitized evidence, likely cause and confidence, ruled-out causes, replay risk, mitigation, owner, and checkpoint. Name the next safe diagnostic if evidence is still inconclusive.

## Examples

- Classify `429` from current workspace evidence and deadline.
- Treat timed-out batch creation as ambiguous until state is reconciled.

## Validation

Prove the fix follows from evidence, preserves idempotency, fits deadline/budget, and exposes no content or credentials.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
