---
name: onenote-deploy-integration
description: >-
  Deploy a OneNote integration with delegated-user lifecycle, environment isolation, staged rollout, and rollback evidence. Use when promoting a service or client that calls Microsoft Graph OneNote. Trigger with "deploy OneNote integration", "promote OneNote worker", or "review OneNote release".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<artifact> <target-environment> <rollout-scope>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, deployment]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Delegated Integration Deployment

## Overview

Deploy a OneNote integration with delegated-user lifecycle, environment isolation, staged rollout, and rollback evidence.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

OneNote's service-specific contract requires a signed-in user context. A deployment must model interactive authorization, consent, token-cache protection, reauthentication, and user-bound work ownership instead of silently substituting client credentials. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Bind encrypted delegated token state to the correct environment, tenant, app registration, and user. Keep deployment identity separate from the user identity that authorizes OneNote work.

## Instructions

1. Verify the immutable artifact, dependency locks, configuration schema, tests, and rollback target.
2. Map environment, tenant, app registration, redirect URI, signed-in user, Notes scopes, and approved roots.
3. Confirm token-cache encryption, rotation, revocation, reauthentication, and operator ownership.
4. Deploy dark, run offline checks, then perform one approved read-only synthetic smoke test.
5. Canary a bounded user cohort and monitor auth failures, 429s, latency, queue age, and reconciliation.
6. Promote or roll back from declared thresholds and retain the release and cleanup receipt.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require release and content-owner approval for production activation. Require separate security approval for new consent, redirect URIs, or token storage and separate approval for writes.

## Error Handling

- Stop if the build or configuration differs from the reviewed artifact.
- Do not use app-only credentials as a fallback.
- Roll back if user binding, consent, or content scope is ambiguous.

## Output

Return the artifact identity, environment matrix, auth lifecycle, smoke evidence, canary metrics, decision, rollback, and owners. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Deploy a read-only canary for one synthetic notebook.
- Exercise revoked consent and prove the service pauses rather than broadening access.

## Validation

Exercise and record these paths with expected and observed results:

- artifact mismatch
- missing user session
- revoked consent
- 429
- rollback
- cleanup

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
