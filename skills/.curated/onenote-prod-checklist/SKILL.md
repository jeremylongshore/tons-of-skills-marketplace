---
name: onenote-prod-checklist
description: >-
  Decide whether a OneNote integration is ready for production from evidence across delegated access, content safety, correctness, limits, operations, and rollback. Use when reviewing a launch or material change. Trigger with "review OneNote production readiness", "OneNote go-live checklist", or "approve OneNote launch".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<release> <environment> <change-scope>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, readiness]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Production Readiness Decision

## Overview

Decide whether a OneNote integration is ready for production from evidence across delegated access, content safety, correctness, limits, operations, and rollback.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

A launch is ready only when the actual user-bound auth lifecycle, approved content roots, supported v1.0 operations, pagination, HTML semantics, throttling, monitoring, and reconciliation are evidenced together. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Verify delegated scope, consent owner, token-cache protection, tenant and user binding, revocation, and reauthentication. App-only fallback is a launch blocker.

## Instructions

1. Verify immutable artifact, dependency, configuration, migration, and test receipts.
2. Confirm account type, tenant, user, app registration, delegated scopes, and approved user, group, or site roots.
3. Review reads, writes, HTML, binary parts, paging, errors, limits, and unsupported-feature assumptions.
4. Review data classification, logs, retention, queues, monitoring, incidents, and support custody.
5. Exercise canary, failure, revocation, 429, rollback, and reconciliation paths.
6. Issue GO, CONDITIONAL GO, or NO-GO with owners, expirations, and rollback triggers.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Named release, security, identity, content, and operations owners approve their controls. Any content mutation or broad consent requires separate explicit approval.

## Error Handling

- NO-GO on app-only auth, undocumented delta or webhook calls, unbounded retries, or incomplete pagination.
- A skipped negative or rollback test remains an open condition.
- Do not waive tenant or user binding as operational detail.

## Output

Return the signed control matrix, evidence links, failed gates, decision, conditions, owners, expiry, and rollback authority. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Reject a release that assumes Retry-After on OneNote 429s.
- Approve a read-only canary only after revoked-consent handling passes.

## Validation

Exercise and record these paths with expected and observed results:

- app-only blocker
- pagination
- HTML mismatch
- 429
- revocation
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
