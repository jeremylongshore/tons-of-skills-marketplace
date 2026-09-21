---
name: mistral-reference-architecture
description: >-
  Design a Mistral integration from policy gateway through adapter, queues, state reconciliation, and audited output. Use when establishing architecture. Trigger with "design a Mistral architecture", "review a Mistral platform", or "standardize Mistral services".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workloads> <data-boundary> <deployment-context>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, architecture]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Governed Reference Architecture

## Overview

Create a workload-aware architecture separating identity, policy, transport, state, and side effects. Route each job to the simplest stable surface and isolate preview/stateful APIs.

## Prerequisites

- A workload inventory for chat, embeddings, classifiers, files/OCR, audio, batch, FIM, and orchestration.
- Identity, tenant, data, retention, spend, SLO, and incident requirements.
- Current endpoint/model evidence and owners for stateful stores.

## Current Contract

Mistral exposes distinct stateless and stateful surfaces including chat, embeddings, classifiers, files, OCR, audio, batch, Workflows, and Public Preview Agents/Conversations. Their contracts are not interchangeable.

## Authentication

Terminate app identity/authorization at a policy gateway; inject provider keys only in trusted adapters. Use approved service identity patterns when supported.

## Instructions

1. Map each workload to data class, latency, state, side effects, endpoint, and stability.
2. Place auth, tenancy, moderation, budgets, and bounds in the gateway.
3. Isolate provider calls behind typed adapters and preview APIs behind versioned boundaries.
4. Use queues/idempotency for async work; reconcile Files, Batch, Workflows, and app state.
5. Store approved data with tenant keys, provenance, retention, deletion, and audit.
6. Define observability, failure modes, rollout, rollback, provider exit, and test ownership.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Preview selection, uploads, persistent stores, tools, infrastructure, and live traffic require approval. Architecture review alone does not provision or mutate any component.

## Error Handling

- One generic completion wrapper cannot preserve file, batch, event, and conversation contracts.
- Provider auth does not enforce application tenancy.
- Untracked uploads create unmanaged data.

## Output

Return components and trust boundaries, workload mappings, stores, approvals, failure paths, owners, tests, and migration and rollback plans. Mark every preview dependency explicitly.

## Examples

- Route interactive chat directly and approved bulk work through idempotent batch.
- Keep beta conversation state behind a replaceable adapter.

## Validation

Walk happy, timeout, duplicate, cross-tenant, outage, rotation, deletion, and rollback paths for every workload. Confirm each stateful resource has reconciliation ownership.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
