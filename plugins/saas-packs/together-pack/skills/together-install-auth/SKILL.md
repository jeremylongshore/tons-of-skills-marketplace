---
name: together-install-auth
description: >-
  Install Together AI SDK v2 and configure a project-scoped API key with least-privilege storage and a read-only model-list verification. Use when connecting a service or workstation to Together AI. Trigger with "Together auth", "install Together SDK", or "TOGETHER_API_KEY setup".
argument-hint: "[repository-path] [python|typescript|rest]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- authentication
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and a Together AI project key
---
# Together AI Installation and Authentication

## Overview

This skill selects the current Together client, keeps credentials outside source control, and proves access with a non-generating model-list request.

## Prerequisites

- A Together AI project and an administrator-approved key owner
- Python 3.10+ for `together>=2.0.0`, Node.js for the TypeScript SDK, or an HTTPS client
- An approved secret manager for deployed environments
- The repository and runtime that will consume the credential

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect dependency manifests, environment-variable names, and existing client wrappers. Use `WebFetch` only for current Together documentation. Use `Write` or `Edit` only after confirming the target files; never write a real key or `.env` value.

## Current Contract

- New Python integrations target the v2 SDK: `together>=2.0.0`.
- SDK clients read `TOGETHER_API_KEY` by default; REST uses `Authorization: Bearer <token>`.
- API keys are scoped to a Together project. Separate development, CI, and production keys.
- Verify with `client.models.list()` or `GET /v1/models`; do not spend inference tokens for an auth probe.

## Authentication

Create the key in the intended Together project, copy it once into the approved secret store, and inject it at runtime as `TOGETHER_API_KEY`. Redact the value, authorization header, and secret-manager path from logs and examples. Rotation means creating a replacement, deploying it, verifying, and revoking the old key.

## Instructions

1. Inventory the language, package manager, existing OpenAI-compatible client, and deployment environments.
2. Pin the current major SDK and record the resolved version in the lockfile.
3. Define `TOGETHER_API_KEY` in local documentation and deployment configuration without adding a value to the repository.
4. Initialize the native Together client, or configure an OpenAI client with `https://api.together.ai/v1`.
5. Run or hand off one read-only model-list probe and record only status, project alias, SDK version, and model count.
6. Document key ownership, rotation, revocation, and environment separation.

## Approval Boundaries

Do not create, reveal, broaden, rotate, or revoke a production key without the owning project administrator. Do not add a credential to tracked files, command history, test fixtures, or CI available to untrusted forks.

## Output

Return the selected client, pinned version, environment-variable contract, secret reference, read-only verification result, and rotation owner.

## Error Handling

| Condition | Response |
|---|---|
| `401` | Confirm injection and project selection; never print the key. |
| `402` | Report the billing/spend-limit condition to the project owner. |
| `404` on an OpenAI model ID | Resolve a current Together model ID; do not retry the foreign name. |
| Key exposed | Revoke or rotate it and scrub retained logs immediately. |

## Examples

Input:

```text
runtime=python; environment=ci; probe=GET /v1/models; secret=approved-reference
```

Expected handoff:

```text
sdk=together-v2; auth=bearer-project-key; probe=pass; secret-value=redacted
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication](https://docs.together.ai/docs/api-keys-authentication)
- [Quickstart](https://docs.together.ai/docs/quickstart)
- [Model-list API](https://docs.together.ai/reference/models)
