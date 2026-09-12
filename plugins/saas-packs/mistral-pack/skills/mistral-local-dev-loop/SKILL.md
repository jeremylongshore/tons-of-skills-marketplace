---
name: mistral-local-dev-loop
description: >-
  Build an offline-first Mistral development loop with contract fixtures and an opt-in live smoke lane. Use when developing or testing an integration locally. Trigger with "mock Mistral locally", "speed up Mistral development", or "test Mistral without API spend".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<runtime> <test-framework> <fixture-policy>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, testing]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Deterministic Local Development Loop

## Overview

Make local iteration deterministic and free of accidental spend. Keep provider calls behind a narrow adapter, validate synthetic fixtures, and reserve live calls for a separately approved lane.

## Prerequisites

- A package lock, test framework, and selected official client.
- A provider-adapter boundary and synthetic fixture policy.
- A secret manager for the optional live lane; never a checked-in `.env` value.

## Current Contract

Official clients wrap a changing HTTP schema. Local tests should assert the application-owned adapter; a narrow live smoke detects drift without making every test network-dependent.

## Authentication

Offline tests must not resolve `MISTRAL_API_KEY`. The live test is disabled by default, reads a protected secret only after its gate is enabled, and redacts transport metadata.

## Instructions

1. Map direct client imports and move calls behind one application interface.
2. Define typed success, stream, tool-call, throttling, malformed, and terminal-error fixtures.
3. Add a transport seam so tests fail on unexpected network access.
4. Test usage normalization, error classification, idempotency, and redaction offline.
5. Create a separately named live smoke with explicit environment and budget gates.
6. Document fixture provenance, schema version, refresh method, and review owner.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Require approval before package changes, network access, provider-derived fixture capture, or a live test. Keep the default developer command entirely offline and credential-free.

## Error Handling

- Mocks coupled to private client internals create false drift.
- Any real prompt, file, or key in a fixture is a data incident.
- Passing offline tests does not prove live account configuration.

## Output

Return adapter path, test commands, fixture inventory, network-denial evidence, live gate, coverage gaps, and review date.

## Examples

- Inject a fake chat transport and assert normalized usage.
- Fail CI when offline tests attempt DNS or unexpectedly see the key.

## Validation

Run without network and credential, mutate fixtures to prove failures, then use the live lane only after approval.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
