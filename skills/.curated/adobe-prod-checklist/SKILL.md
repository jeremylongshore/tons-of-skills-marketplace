---
name: adobe-prod-checklist
description: >-
  Issue an evidence-backed production decision across Adobe auth, entitlements, API versions, data custody, async reliability, spend, observability, and rollback. Use before launch or a material integration change. Use when this Adobe operator workflow is needed. Trigger with "Adobe production checklist", "approve Adobe launch", or "Adobe go-live review".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<release> <environment> <change-scope>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, readiness]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Production Readiness Decision

## Overview

Issue an evidence-backed production decision across Adobe auth, entitlements, API versions, data custody, async reliability, spend, observability, and rollback.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

A launch is ready only when the deployed artifact and actual organization/project/workspace, credentials, product profiles, service versions, storage, queues, events, monitoring, support, and rollback are evidenced together. Passing a token call or happy path is insufficient. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Verify secret lifecycle, user consent if applicable, least privilege, entitlement, rotation, revocation, and environment isolation. JWT, Photoshop v1, and retired Lightroom Firefly Services references are launch blockers.

## Instructions

1. Verify immutable artifact, dependencies, configuration, generated assets, tests, migrations, and rollback target.
2. Confirm organization/project/workspace, auth flow, scopes, profiles, entitlement, storage, and owner matrices.
3. Review every service version, async job, retry/idempotency, rate/spend, event authenticity, and EOL guard.
4. Review data classification, signed URLs, logs, retention, deletion, incident response, and vendor support custody.
5. Exercise canary, denial, 429, unknown status, rollback, reconciliation, and cleanup paths.
6. Issue GO, CONDITIONAL GO, or NO-GO with evidence, owners, expirations, and rollback authority.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Named release, security, data, budget, and operations owners approve their controls. Deploy, generation, upload, webhook replacement, secret deletion, and asset deletion remain separate actions.

## Error Handling

- NO-GO on obsolete endpoints, missing entitlement, unbounded polling/retries, or unverified rollback.
- A skipped negative test remains an open condition.
- Do not waive content or signed-URL leakage as observability detail.

## Output

Return the signed control matrix, evidence links, failed gates, decision, conditions, owners, expiry, and rollback triggers. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Reject a release containing /sensei/cutout.
- Approve a canary only after unknown-job and credential-revocation paths pass.

## Validation

Exercise and record expected and observed results for:

- obsolete API
- entitlement
- 429
- unknown job
- secret revocation
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
