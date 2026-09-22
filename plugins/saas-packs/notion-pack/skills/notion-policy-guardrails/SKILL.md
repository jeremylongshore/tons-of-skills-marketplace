---
name: notion-policy-guardrails
description: >-
  Turn Notion security, privacy, access, version, and mutation rules into enforceable repository and runtime gates. Use when defining policy-as-code for integrations. Trigger with "add Notion guardrails", "enforce Notion policy", or "review Notion controls".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-or-service> <policy-scope> <environment>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, policy]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Integration Policy Guardrails

## Overview

Turn Notion security, privacy, access, version, and mutation rules into enforceable repository and runtime gates.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Useful guardrails cover secret handling, tested versions, object-type correctness, pagination, retries, capabilities, content sharing, tenant binding, webhook verification, destructive actions, and evidence retention. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Policy checks may inspect secret names and fingerprints but never values. Runtime checks must bind a credential to its expected workspace and environment.

## Instructions

1. Translate each policy statement into owner, scope, machine check, human gate, evidence, and exception expiry.
2. Add static checks for credentials, legacy object operations, unsafe logging, unbounded retries, and missing approvals.
3. Add tests for page/data-source identity, pagination, webhook signatures, idempotency, and tenant isolation.
4. Add runtime guards for environment, write scope, concurrency, payload size, and destructive operations.
5. Define signed, time-bounded exceptions with compensating controls.
6. Exercise allow, deny, bypass-expired, and rollback paths before enforcing the gate.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Security owns secret and webhook rules; data owners own content scope; release owners approve enforcement rollout; no single actor self-approves exceptions.

## Error Handling

- A warning-only secret rule is insufficient for production.
- Do not auto-fix object identity or destructive requests.
- Fail closed when policy evidence is missing.

## Output

Return the control catalog, implementation points, tests, gate outputs, exception register, owners, and rollout plan. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Block a credential literal before commit.
- Reject a write job lacking an approved scope and idempotency key.

## Validation

Exercise and record these paths with expected and observed results:

- allow path
- deny path
- expired exception
- tenant mismatch
- unsafe retry
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
