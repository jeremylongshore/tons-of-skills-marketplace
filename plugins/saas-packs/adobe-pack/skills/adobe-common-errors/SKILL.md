---
name: adobe-common-errors
description: >-
  Classify Adobe failures from redacted response evidence and select the smallest bounded recovery. Use across auth, Firefly, Photoshop, PDF Services, Events, and App Builder. Use when this Adobe operator workflow is needed. Trigger with "fix Adobe error", "Adobe 403", or "Adobe API failed".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <operation> <status-or-error>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, errors]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Response-Led Error Triage

## Overview

Classify Adobe failures from redacted response evidence and select the smallest bounded recovery.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

HTTP status, product error code, request/job/activation identity, credential type, organization, entitlement, request validity, retry headers, and service state are separate evidence. There is no safe universal mapping from one status to one fix. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Record only credential aliases, scopes, profiles, and expiry class. A 403 may be organization, entitlement, product-profile, policy, or resource authority; do not solve it by blind privilege expansion.

## Instructions

1. Capture one sanitized request/response envelope, operation, environment, timestamp, and correlation identifiers.
2. Classify transport, authentication, authorization/entitlement, validation/policy, throttling, conflict, async-state, or vendor-service failure.
3. Compare host, method, version, schema, organization/project/workspace, scopes, profiles, and data ownership with current docs.
4. Apply the smallest class-specific correction and preserve the original evidence.
5. Retry only transient and idempotent work within Retry-After and strict attempt/time budgets.
6. Verify with the least consequential reproduction and package unresolved cases for Adobe support.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Scope/profile/credential changes require security and organization-owner approval. Prompt, document, asset, event registration, deploy, or retry changes require their respective owners.

## Error Handling

- Never infer a 24-hour token lifetime unless the actual token response proves it.
- Never accept 429 as a successful CI test.
- Do not dump raw HTTP traces containing Authorization or signed URLs.

## Output

Return the evidence envelope, fault class, ruled-out causes, minimal action, retry decision, verification, and escalation packet. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Distinguish missing entitlement from expired auth on a 403 path.
- Honor Retry-After on a synthetic 429 and stop at budget.

## Validation

Exercise and record expected and observed results for:

- 401
- 403
- validation/policy
- 429
- 5xx
- unknown async state

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
