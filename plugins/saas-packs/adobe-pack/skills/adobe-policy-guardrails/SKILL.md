---
name: adobe-policy-guardrails
description: >-
  Analyze and enforce repository, runtime, data, spend, endpoint, and approval guardrails without guessing secret formats or content-policy rules. Use when the task requires adobe policy and execution guardrails. Trigger with "Adobe guardrails", "block unsafe Adobe calls", or "Adobe policy checks".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-or-service> <operations> <policy-owners>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, guardrails]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Policy and Execution Guardrails

## Overview

Analyze and enforce repository, runtime, data, spend, endpoint, and approval guardrails without guessing secret formats or content-policy rules. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Guardrails derive from current service docs and local policy: approved auth flows, hosts/versions, scopes/profiles, schemas, storage domains, budgets, data classes, and approval boundaries. Secret prefixes and prompt regexes are not authoritative security or content-policy controls. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Use mature secret scanners plus entropy/context rules and provider revocation procedures. Runtime authorization evaluates credential binding, entitlement, resource, operation, and approval.

## Instructions

1. Inventory all Adobe calls, credentials, endpoints, versions, payload classes, storage URLs, retries, jobs, events, and destructive operations.
2. Create allowlists for current hosts/versions/services and denylists for JWT, /sensei/cutout, and retired Lightroom Firefly Services.
3. Validate configuration/request/response schemas and redact tokens, signed URLs, prompts, and customer content.
4. Enforce data-purpose, owner, budget, concurrency, idempotency, and approval tokens before side effects.
5. Route Adobe policy outcomes to a human-readable denial path; never silently rewrite prompts or broaden scopes.
6. Test bypasses, stale docs, false positives, emergency disablement, exception expiry, and audit receipts.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Security/product/data/budget owners approve policy and exceptions. Generation, upload, deploy, webhook change, cancellation, replay, and deletion remain independently approved actions.

## Error Handling

- Do not claim Adobe secrets always have a specific prefix.
- Do not claim local regexes predict Firefly policy decisions.
- Fail closed when endpoint/version or approval evidence is unknown.

## Output

Return policy sources, allow/deny rules, enforcement points, test corpus, exceptions, receipts, drift monitor, and owners. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Block /sensei/cutout before network execution.
- Detect a signed URL in a log fixture and fail the gate.

## Validation

Exercise and record expected and observed results for:

- obsolete route
- unknown host
- secret leak
- policy outcome
- budget ceiling
- expired exception

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
