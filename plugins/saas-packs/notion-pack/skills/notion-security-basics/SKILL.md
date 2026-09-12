---
name: notion-security-basics
description: >-
  Establish a security baseline for Notion credentials, capabilities, content access, webhooks, writes, logs, and tenant isolation. Use when designing, reviewing, or hardening an integration. Trigger with "secure Notion integration", "audit Notion security", or "review Notion token handling".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<connection-model> <data-classification> <environment>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, security]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Integration Security Baseline

## Overview

Establish a security baseline for Notion credentials, capabilities, content access, webhooks, writes, logs, and tenant isolation.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Security spans bearer-token custody, OAuth state and workspace binding, minimum capabilities, explicit content sharing, webhook signature verification, version-safe parsing, idempotent writes, telemetry redaction, and incident revocation. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Store credentials only in the approved secret system, encrypt public-connection tokens at rest, separate environments and tenants, and test rotation and revocation.

## Instructions

1. Inventory connections, owners, workspaces, capabilities, shared roots, secrets, callbacks, subscriptions, and processors.
2. Minimize access and prove denied paths for unshared or unauthorized content.
3. Threat-model OAuth state, callback binding, token storage, webhook verification, replay, SSRF, logs, caches, queues, and exports.
4. Add payload validation, unknown-field tolerance, request limits, retry budgets, idempotency, and destructive-action gates.
5. Instrument content-safe security events and define credential-compromise containment.
6. Exercise rotation, revocation, tenant swap, forged webhook, over-limit payload, and rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Security and workspace owners approve connection and capability changes; data owners approve content scope; production writes require operation-owner approval.

## Error Handling

- Never log bearer or webhook verification material.
- Do not trust a workspace ID supplied by an unbound client session.
- Reject webhook signatures using constant-time comparison after hashing the raw body.

## Output

Return the threat model, access matrix, secret lifecycle, control evidence, test results, exceptions, and incident contacts. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Reject a valid token bound to the wrong workspace.
- Rotate a production secret without exposing it or losing rollback custody.

## Validation

Exercise and record these paths with expected and observed results:

- revoked token
- tenant swap
- forged signature
- replay
- secret canary
- destructive denial

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
