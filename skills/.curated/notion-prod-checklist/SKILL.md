---
name: notion-prod-checklist
description: >-
  Decide whether a Notion integration is ready for production from evidence across access, contracts, correctness, safety, and operations. Use when reviewing a launch or material change. Trigger with "review Notion production readiness", "Notion go-live checklist", or "approve Notion launch".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<release-id> <production-scope> <owner>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, production]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Production Readiness Review

## Overview

Decide whether a Notion integration is ready for production from evidence across access, contracts, correctness, safety, and operations.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Readiness covers selected API and SDK contracts, connection model, access, schema and object identities, pagination, limits, retries, idempotency, webhooks, data governance, observability, reconciliation, and rollback. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Verify production secret provenance, workspace binding, minimum capabilities, shared roots, rotation, revocation, and break-glass custody.

## Instructions

1. Bind the review to an immutable artifact, configuration digest, owners, environments, and change window.
2. Walk access, data, version, schema, operation, limit, retry, webhook, and destructive-action controls.
3. Run offline tests and approved non-production happy, denied, failure, restart, and rollback paths.
4. Verify dashboards, alerts, incident ownership, support escalation, queue controls, and reconciliation.
5. List open risks with explicit acceptance authority and expiry.
6. Issue GO, CONDITIONAL GO, or NO-GO with evidence and post-launch observation gates.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Production owner approves launch; security, data, and content owners approve their boundaries; destructive or irreversible migrations require an independent gate.

## Error Handling

- A Grade A document is not operational readiness evidence.
- Do not waive missing rollback or reconciliation as follow-up work.
- NO-GO when production identity or secret provenance is ambiguous.

## Output

Return the signed gate matrix, evidence links, risks, decision, launch window, rollback triggers, and observation plan. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Issue NO-GO for a write worker without idempotency tests.
- Issue CONDITIONAL GO for a read-only canary with a bounded follow-up.

## Validation

Exercise and record these paths with expected and observed results:

- credential revocation
- schema drift
- 429
- write timeout
- webhook replay
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
