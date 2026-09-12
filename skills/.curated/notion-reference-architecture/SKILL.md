---
name: notion-reference-architecture
description: >-
  Define a production reference architecture for Notion access, operations, queues, reconciliation, and evidence. Use when standardizing multiple integration workloads. Trigger with "build Notion reference architecture", "standardize Notion services", or "review Notion platform design".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<tenant-model> <workloads> <recovery-objectives>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, reference-architecture]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Integration Reference Architecture

## Overview

Define a production reference architecture for Notion access, operations, queues, reconciliation, and evidence.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

A durable architecture separates transport, auth, tenant binding, object identity, schema mapping, operation logic, queues, idempotency, webhooks, reconciliation, telemetry, and evidence storage. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Centralize secret retrieval without centralizing plaintext. Bind every operation to connection, workspace, environment, capabilities, and approved content scope.

## Instructions

1. Define domain boundaries, sources of truth, tenant model, data classes, and service objectives.
2. Specify adapters for current pages, blocks, databases, data sources, search, files, and webhooks.
3. Place idempotency, checkpoints, backpressure, retry classification, and dead letters at explicit boundaries.
4. Add reconciliation as a first-class service independent of webhook delivery.
5. Define observability, evidence, privacy, retention, incident, and support interfaces.
6. Document deployment stages, compatibility policy, failure modes, and tested rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require architecture, security, and data-owner review before adopting shared tokens, shared queues, external processors, or cross-tenant stores.

## Error Handling

- Do not leak SDK response shapes directly into domain models.
- Do not make webhook delivery the only recovery path.
- Reject shared mutable state without tenant binding.

## Output

Return context and component views, contracts, trust boundaries, failure modes, capacity assumptions, operational ownership, and rollout plan. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Standardize query and write adapters behind domain operations.
- Recover missed webhook signals through scheduled reconciliation.

## Validation

Exercise and record these paths with expected and observed results:

- tenant isolation
- schema evolution
- duplicate write
- lost signal
- queue outage
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
