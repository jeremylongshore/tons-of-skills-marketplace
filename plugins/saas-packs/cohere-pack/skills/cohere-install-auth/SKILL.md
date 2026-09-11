---
name: cohere-install-auth
description: >-
  Install current Cohere v2 SDKs, store an API key safely, and verify access without spending inference tokens. Use when connecting a repository or runtime to Cohere. Trigger with "Cohere auth", "install Cohere SDK", or "CO_API_KEY setup".
argument-hint: "[repository-path] [typescript|python|rest]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- authentication
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Installation and Authentication

## Overview

Select the current v2 client for the repository, keep credentials outside source control, and prove access with a read-only Models API request.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- TypeScript uses `CohereClientV2`; Python uses `cohere.ClientV2`.
- Use `CO_API_KEY` as the local injection contract or pass an approved secret reference explicitly.
- Pin a compatible SDK range and commit the resolved lockfile; do not copy an unbounded install command into CI.
- Verify authentication by listing accessible models rather than generating billable output.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Inspect manifests, lockfiles, existing provider adapters, and secret-loading conventions.
2. Choose TypeScript, Python, or REST and pin the current compatible SDK major.
3. Document `CO_API_KEY` without writing its value, then update ignore rules if local environment files are used.
4. Initialize the v2 client with the injected key and an explicit timeout.
5. Run one read-only model-list probe and record the SDK version, status, and model count only.
6. Assign ownership for key creation, rotation, revocation, and environment separation.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| `401` | Confirm runtime injection and key state without printing the credential. |
| No models | Check team membership and deployment availability before changing code. |
| SDK shape mismatch | Compare the installed major with the official generated SDK reference. |
| Exposed key | Rotate or revoke it and scrub retained logs immediately. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
runtime=typescript; environment=ci; probe=models.list; secret=approved-reference
```

Expected handoff:

```text
client=v2; sdk=cohere-ai@resolved; auth=pass; key-value=redacted
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Create a v2 client](https://docs.cohere.com/docs/create-client)
- [Models API](https://docs.cohere.com/reference/list-models)
