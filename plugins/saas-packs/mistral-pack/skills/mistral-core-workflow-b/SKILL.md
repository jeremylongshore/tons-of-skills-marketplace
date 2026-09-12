---
name: mistral-core-workflow-b
description: >-
  Build Mistral embeddings, retrieval, and function-calling loops with tenant isolation and application-owned execution. Use when adding RAG or tools. Trigger with "build Mistral RAG", "use Mistral embeddings", or "add Mistral function calling".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<retrieval-corpus> <tool-policy> <tenant-boundary>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, rag]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Retrieval and Tool Execution

## Overview

Keep retrieval and tool use under application control. The model may propose queries or typed arguments; trusted code owns authorization, execution, side effects, and returned evidence.

## Prerequisites

- A tenant-scoped corpus with chunking, deletion, and re-embedding policy.
- A current embedding model selected from account evidence.
- A closed tool registry with schemas, authorization, deadlines, and idempotency.

## Current Contract

Embeddings use `POST /v1/embeddings`; tool calls use the current chat schema. Vector shape, model access, tool schemas, and parallel behavior must come from the selected current contracts.

## Authentication

Use Bearer auth only for Mistral. Every retrieved record and proposed action must separately pass application user and tenant authorization.

## Instructions

1. Define retrieval purpose, data class, tenant filter, deletion SLA, and evaluation set.
2. Store embedding model, preprocessing version, and observed vector shape with each index.
3. Retrieve with mandatory tenant filters and cap context before chat assembly.
4. Validate each proposed tool name and argument against the closed registry and strict schema.
5. Authorize and execute each side effect in trusted code with deadline and idempotency.
6. Evaluate retrieval quality, access negatives, tool denial, usage, latency, and rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Require approval before embedding customer data, creating an index, executing a mutation, widening corpus access, or allowing parallel actions.

## Error Handling

- Mixed-model indexes can corrupt similarity meaning.
- Prompt instructions cannot replace tenant filters or authorization.
- Malformed or repeated tool calls must be rejected or deduplicated, never broadened.

## Output

Return corpus/tenant boundary, model/preprocessing versions, retrieval metrics, tool decisions, idempotency IDs, usage, retention, and rollback.

## Examples

- Retrieve only records authorized for one tenant and cite opaque IDs.
- Let the model propose `lookup_order`; trusted code validates schema and entitlement.

## Validation

Test cross-tenant denial, deletion propagation, model mismatch, empty retrieval, malformed/duplicate tools, cancellation, and mutation denial.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
