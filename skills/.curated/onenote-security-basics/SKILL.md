---
name: onenote-security-basics
description: >-
  Establish a security baseline for delegated identity, consent, token caches, notebook content, logs, writes, and tenant isolation. Use when designing or hardening a OneNote integration. Trigger with "secure OneNote integration", "audit OneNote permissions", or "review OneNote token handling".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<application> <tenant> <data-classification>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, security]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Security Baseline

## Overview

Establish a security baseline for delegated identity, consent, token caches, notebook content, logs, writes, and tenant isolation.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

OneNote access is user-bound and content-rich. Effective authority depends on the delegated scope, signed-in user, target location, notebook sharing, application policy, and operation; generic application permission rows do not override the OneNote service's app-only prohibition. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Use the minimum delegated Notes scope, encrypted token-cache storage, verified redirect URIs, tenant and user binding, redacted telemetry, revocation handling, and short retention for diagnostic evidence.

## Instructions

1. Inventory app registrations, redirect URIs, tenants, account types, users, scopes, caches, roots, operations, logs, and destinations.
2. Calculate effective access for every read, create, update, binary, copy, and export operation.
3. Remove app-only paths, default-scope assumptions, token logging, shared caches, and production fallbacks.
4. Add fail-closed tenant and user assertions plus content classification and minimization.
5. Test consent denial, revocation, cache theft, cross-user swaps, unauthorized roots, and log canaries.
6. Assign rotation, reauthentication, incident, retention, access-review, and exception owners.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require security and identity approval for registrations, consent, redirects, caches, or multitenant distribution. Content owners approve roots, exports, writes, and retention.

## Error Handling

- Never decode an unverified token as proof of authorization.
- Stop on tenant, user, or root mismatch.
- Do not broaden from Notes.Read to write scopes merely to resolve an access error.

## Output

Return the threat model, effective-access matrix, control evidence, findings, corrective owners, exceptions, and recertification date. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Prove one user's cached session cannot access another user's job partition.
- Revoke consent and verify queued work pauses without token fallback.

## Validation

Exercise and record these paths with expected and observed results:

- least privilege
- redirect integrity
- cache theft
- cross-user swap
- revocation
- content leak

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
