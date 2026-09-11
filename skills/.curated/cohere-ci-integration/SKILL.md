---
name: cohere-ci-integration
description: >-
  Configure offline Cohere contract tests plus a protected, bounded live verification lane in CI. Use when testing Cohere integrations in pull requests or releases. Trigger with "Cohere CI", "Cohere GitHub Actions", or "Cohere integration tests".
argument-hint: "[repository-path] [ci-provider]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- ci
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Continuous Integration

## Overview

Make the required CI path deterministic and secret-free while preserving a trusted lane that detects real SDK and API drift.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Required pull-request checks should mock the application provider port and make no Cohere network calls.
- Fork pull requests must never receive Cohere secrets.
- A trusted branch, schedule, or manual workflow may run one bounded live probe with explicit spend and timeout limits.
- Pin runtime, SDK, action, and lockfile versions so failures are reproducible.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Identify required checks, fork behavior, secret scopes, and the existing provider adapter.
2. Add offline request-mapping, response, stream, error, retry, and redaction fixtures.
3. Make the offline lane required and assert that no network fallback is possible.
4. Add a separate protected live job with concurrency control, one request, timeout, and model discovery.
5. Upload sanitized test metadata without prompts, credentials, or customer content.
6. Document who may trigger the live lane and how model/API drift is triaged.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Secret unavailable | Skip only the optional live job; required offline tests must still run. |
| Fork event | Never switch to a privileged event that executes untrusted code with secrets. |
| Live `429` | Stop the probe and classify capacity rather than retrying repeatedly. |
| Fixture drift | Refresh from a reviewed redacted response. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
provider=github-actions; required=offline; live=protected-main; max-requests=1
```

Expected handoff:

```text
offline=required-pass; fork-secrets=none; live=bounded; artifacts=redacted
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [TypeScript SDK](https://github.com/cohere-ai/cohere-typescript)
- [Rate limits](https://docs.cohere.com/docs/rate-limits)
