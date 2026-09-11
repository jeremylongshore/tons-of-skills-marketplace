---
name: cohere-local-dev-loop
description: >-
  Build a deterministic local Cohere development loop with a provider adapter, fixtures, and an opt-in live smoke test. Use when developing or testing Cohere features locally. Trigger with "Cohere local dev", "mock Cohere", or "Cohere test loop".
argument-hint: "[repository-path] [test-command]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- development
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Local Development Loop

## Overview

Keep normal development offline and deterministic while preserving one tightly bounded path that proves the real v2 contract.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Mock the application-owned provider interface, not generated SDK internals.
- Store representative v2 Chat, Embed, Rerank, stream, error, and tool-call fixtures with secrets removed.
- Gate real calls behind an explicit environment switch and a protected evaluation key.
- Treat model IDs and SDK response types as external contracts covered by adapter tests.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Locate the provider boundary and existing test framework before adding files.
2. Define a narrow Cohere port for the operations the application actually needs.
3. Add sanitized fixtures for success, rate limit, timeout, and malformed response paths.
4. Write offline contract tests for request mapping, response parsing, and redaction.
5. Add one opt-in live smoke test with a single request and hard timeout.
6. Document the exact offline and live commands and ensure the default test command makes no network call.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Fixture drift | Refresh from a redacted live response and review the diff. |
| Accidental spend | Fail closed unless the explicit live-test switch is set. |
| Flaky test | Replace SDK/network dependence with the local provider port. |
| Secret in snapshot | Revoke if real, scrub history, and add a regression assertion. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
framework=vitest; default=offline; live-switch=COHERE_LIVE_TESTS
```

Expected handoff:

```text
offline=pass; network-calls=0; live-smoke=opt-in; fixtures=sanitized
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [TypeScript SDK](https://github.com/cohere-ai/cohere-typescript)
- [API v2 migration](https://docs.cohere.com/docs/migrating-v1-to-v2)
