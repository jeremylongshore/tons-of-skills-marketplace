---
name: ideogram-prod-checklist
description: >-
  Gate an Ideogram production release across billing, auth, safety, async completion, asset persistence, observability, and rollback. Use when approving a launch or reviewing release readiness. Trigger with "ship Ideogram to production", "run Ideogram preflight", or "audit an Ideogram release".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<release-sha> <environment> <owner>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, release]
model: inherit
effort: high
compatibility: "Designed for Claude Code; production mutation requires explicit release approval"
---
# Ideogram Production Readiness Gate

## Overview

Produce a fail-closed release decision for an Ideogram integration. A visually successful test is only one signal; production readiness also requires owned billing, secure credentials, bounded capacity, moderation, durable assets, async reconciliation, telemetry, and a tested rollback.

## Prerequisites

- Immutable release SHA, target environment, change owner, approver, and deployment window.
- Current architecture, endpoint inventory, tests, SLOs, budgets, retention, and incident runbook.
- Staging parity and a synthetic canary that contains no customer-derived content.

## Current Contract

Live API calls require accepted terms, payment method, positive prepaid credit, and a valid `Api-Key`. Generation routes differ by endpoint and sync or async lifecycle. Safety is item-level, image URLs expire, and default capacity is documented as 10 in-flight requests.

## Authentication

Confirm a target-environment secret reference, server-only injection, correct `Api-Key` header, scoped application authorization, and exercised revocation. Never place a real key in the release artifact or checklist evidence.

## Instructions

1. Freeze the SHA and compare implemented endpoints, multipart fields, and schemas to current first-party docs.
2. Verify terms, positive credit, billing owner, alert thresholds, and a response to exhausted balance.
3. Prove secret handling, tenant authorization, media validation, safety and copyright policy, and retention controls.
4. Test sync and async success, unsafe output, every handled error class, webhook verification, polling fallback, duplicates, and terminal-state closure.
5. Confirm account-level concurrency, queue bounds, deadlines, storage download, expiring-URL removal, and object deletion.
6. Review dashboards, alerts, on-call ownership, support escalation, and content-free evidence.
7. Run a staging canary, execute rollback rehearsal, obtain explicit approval, then deploy a bounded production canary.
8. Reconcile final state and stop or roll back on any failed gate.

## Tool Discipline

Use Read, Glob, and Grep to inspect release evidence. Use Write and Edit only for approved fixes or release documentation. Do not deploy, add credit, rotate keys, alter policy, or run production generation by invocation alone.

## Approval Boundaries

The named approver owns live spend, production traffic, policy settings, and rollback acceptance. Missing evidence, unknown asset retention, unverified webhook signatures, or an untested rollback yields a no-go decision.

## Error Handling

- Stop on schema drift, secret exposure, unsafe-publication paths, unbounded queueing, or inability to persist output.
- Never waive a failed gate because the canary image looks correct.
- Roll back traffic before debugging a release that creates duplicate paid work or loses async state.

## Output

Return SHA, environment, gate-by-gate pass or fail, evidence identifiers, canary metrics, known risks, approver, deployment state, and rollback receipt. Exclude keys, prompts, images, and URLs.

## Examples

- Mark no-go when generation succeeds but the application retains only expiring vendor URLs.
- Mark go after verified signatures, polling fallback, safety handling, storage deletion, and rollback all pass.

## Validation

Rerun the exact release test set against the frozen SHA, verify evidence timestamps and owners, and compare deployed digest to approved digest. Confirm canary termination and rollback remain available after launch.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
