---
name: adobe-security-basics
description: >-
  Establish least privilege, credential rotation, webhook authenticity, signed-URL custody, log minimization, and destructive-action controls. Use when designing or hardening Adobe integrations. Trigger with "secure Adobe integration", "rotate Adobe secret", or "verify Adobe webhook".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<application> <services> <data-classification>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, security]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Integration Security Baseline

## Overview

Establish least privilege, credential rotation, webhook authenticity, signed-URL custody, log minimization, and destructive-action controls.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Effective authority combines credential type, organization/project/workspace, scopes, product profiles, service entitlement, resource ownership, and operation. Event authenticity requires recipient and signature validation or mTLS; a syntactically valid JSON body is not trusted. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Store secrets server-side, redact signed URLs as bearer capabilities, rotate by overlap-and-verify, and delete the old secret only after last-use evidence proves cutover.

## Instructions

1. Inventory credentials, users, scopes, profiles, projects, workspaces, webhooks, storage URLs, logs, and data flows.
2. Map effective read/write/generate/deploy/admin authority and remove stale or duplicate grants.
3. Add server-side secret storage, rotation alarms, host allowlists, request schemas, and structured redaction.
4. Validate webhook recipientclientid and digital signature/public-key host, or document the approved mTLS alternative.
5. Test credential theft, wrong organization, cross-environment swap, replay, forged key URL, and log canaries.
6. Assign recertification, rotation, incident, retention, deletion, and exception owners.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Security and organization owners approve credentials, scopes, product profiles, webhooks, and secret deletion. Data owners approve uploads, generated outputs, retention, sharing, and asset deletion.

## Error Handling

- Never fetch a verification key from an arbitrary event-supplied host.
- Never rotate by deleting the only working secret first.
- Never log Authorization headers, refresh tokens, signed URLs, prompts, or document content.

## Output

Return threat model, access matrix, rotation plan, webhook/storage controls, test evidence, findings, owners, and recertification date. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Reject a webhook whose recipient client ID differs.
- Rotate a sandbox secret with overlap and last-used verification.

## Validation

Exercise and record expected and observed results for:

- wrong organization
- stale secret
- forged webhook
- replay
- signed URL leak
- destructive approval

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
