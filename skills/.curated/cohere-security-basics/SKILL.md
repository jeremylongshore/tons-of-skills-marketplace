---
name: cohere-security-basics
description: >-
  Apply a Cohere security baseline for keys, tenant isolation, input controls, output handling, safety modes, and logs. Use when building or reviewing a Cohere integration. Trigger with "Cohere security", "secure Cohere key", or "Cohere safety review".
argument-hint: "[repository-path] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- security
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Security Baseline

## Overview

Protect the credential and the data path around the model; safety modes complement but do not replace application security controls.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Keep keys in an approved secret manager, separate them by environment, and rotate on exposure.
- Authorize retrieval and tool execution in application code before any data leaves its trust boundary.
- Cohere safety modes are model- and feature-dependent; tools or documents can constrain the available mode.
- Treat model output, citations, tool arguments, and retrieved text as untrusted data.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Map data classes, tenants, endpoints, tools, logs, and credential owners.
2. Enforce server-side key injection, outbound host allowlisting, timeouts, and request-size limits.
3. Apply tenant filters before retrieval and authorize every tool call independently of model intent.
4. Choose and test the supported safety mode for each resolved model and feature combination.
5. Redact logs and validate output before rendering, persistence, or side effects.
6. Test key exposure, prompt injection, cross-tenant retrieval, unsafe output, and tool escalation.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Unsupported safety mode | Fail closed or use the approved supported mode after review. |
| Cross-tenant result | Stop the release and treat it as a security incident. |
| Prompt injection | Keep instructions and authorization outside retrieved content. |
| Key exposure | Rotate or revoke and investigate retained copies. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
environment=production; features=rag,tools; tenants=multi; data=confidential
```

Expected handoff:

```text
keys=isolated; retrieval=tenant-filtered; tools=authorized; safety=tested
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Safety modes](https://docs.cohere.com/docs/safety-modes)
- [Cohere security](https://cohere.com/security)
