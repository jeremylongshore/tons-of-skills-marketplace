---
name: cohere-debug-bundle
description: >-
  Collect a minimal redacted Cohere diagnostic bundle with versions, request shape, timing, status, and reproduction evidence. Use when escalating a persistent Cohere problem. Trigger with "Cohere debug bundle", "Cohere support evidence", or "collect Cohere diagnostics".
argument-hint: "[incident-id] [output-directory]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- diagnostics
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Support-Ready Debug Bundle

## Overview

Produce evidence that support can act on without copying credentials, prompts, customer data, or an unrestricted environment dump.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Collect only allowlisted environment-variable names and redact values.
- Record endpoint, SDK/runtime versions, model ID, status, latency, retry count, and provider request identifier when available.
- Represent request and response structures with synthetic or hashed content.
- Keep the bundle local until a human approves its recipients and data classification.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Create a dedicated output directory with restrictive permissions and a retention deadline.
2. Capture runtime, SDK, lockfile, network path, timestamp, and Cohere status metadata.
3. Serialize a redacted request-shape summary and the smallest synthetic reproduction.
4. Include bounded probe output, application correlation ID, and sanitized stack trace.
5. Scan the bundle for key formats, authorization headers, emails, prompts, and customer identifiers.
6. Return the manifest and checksum for human review; do not transmit it automatically.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Secret detected | Stop packaging, remove the value, and rotate if exposure occurred. |
| Customer text present | Replace it with a synthetic reproducer or approved hash. |
| Oversized bundle | Drop unrelated logs and narrow the time window. |
| No reproduction | Document observed evidence and mark the failure intermittent. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
incident=INC-42; window=10m; reproduction=synthetic; destination=local-only
```

Expected handoff:

```text
bundle=ready; secrets=0; customer-content=0; checksum=recorded
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Error reference](https://docs.cohere.com/reference/errors)
- [Cohere support guidance](https://docs.cohere.com/docs/cohere-faqs)
