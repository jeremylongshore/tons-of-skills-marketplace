---
name: mistral-sdk-patterns
description: >-
  Design a pinned Mistral client adapter with typed results, cancellation, retry classification, and usage accounting. Use when implementing or refactoring SDK access. Trigger with "wrap the Mistral SDK", "review Mistral client code", or "standardize Mistral calls".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<runtime> <client-version> <application-boundary>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, sdk]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral SDK Boundary Patterns

## Overview

Prevent provider-specific shapes and volatile client behavior from spreading. Centralize configuration, normalize results and errors, and expose cancellation and usage as first-class fields.

## Prerequisites

- A locked official client version and matching documentation.
- An application interface for chat, embeddings, and optional streams.
- Defined timeout, retry, observability, and redaction policies.

## Current Contract

Mistral documents official Python and TypeScript clients, but signatures can move independently of application code. REST endpoints remain the verification boundary for the pinned client.

## Authentication

Inject `MISTRAL_API_KEY` into one server-side client factory. Return no key or authorization metadata from the adapter.

## Instructions

1. Inventory imports, transport overrides, model strings, and response shapes.
2. Define normalized types including request ID, usage, finish state, and error class.
3. Create one factory with explicit host, timeout, user agent, and dependency pin.
4. Retry only classified transient failures while honoring deadline, cancellation, and budget.
5. Keep stream assembly and tool-call validation in separate tested components.
6. Add characterization tests before migrating call sites.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Require approval for dependency, transport, retry, fallback-model, or live characterization changes. Never execute returned tool arguments automatically.

## Error Handling

- Retrying every exception can multiply spend and hide invalid requests.
- Import-time client construction makes rotation and tests unsafe.
- Returning raw SDK objects couples the app to undocumented fields.

## Output

Return client pin, adapter surface, timeout/retry matrix, normalized fields, affected call sites, tests, and rollback.

## Examples

- Wrap chat and embeddings behind explicit adapter methods.
- Map `429` as retryable only within the operation deadline and budget.

## Validation

Prove only the adapter imports the SDK, errors remain typed, cancellation propagates, usage survives, and secrets do not.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
