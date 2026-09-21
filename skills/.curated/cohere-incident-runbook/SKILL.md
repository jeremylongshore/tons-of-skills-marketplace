---
name: cohere-incident-runbook
description: >-
  Analyze and mitigate Cohere integration incidents with provider, model, capacity, data, and application evidence plus reversible actions. Use when responding to an outage or serious degradation. Trigger with "Cohere incident", "Cohere outage", or "Cohere on-call".
argument-hint: "[incident-id] [severity]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- incident-response
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Incident Runbook

## Overview

Restore a safe user experience first, preserve evidence, and distinguish provider incidents from local regressions before making changes.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Check Cohere's status page, but treat service-specific evidence as authoritative for your workload.
- Separate authentication, billing, throttling, model retirement, provider `5xx`, retrieval, and application failures.
- Use only pre-approved degradation paths such as queueing, cached answers, read-only mode, or an evaluated model route.
- Never debug by dumping keys, prompts, documents, or unrestricted environment variables.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Open the incident record and capture start time, impact, environment, endpoint, model, release, and correlation IDs.
2. Check provider status and compare control traffic, regions, models, and recent local changes.
3. Classify the failure and apply the smallest reversible mitigation within the incident authority matrix.
4. Protect data and side effects while monitoring recovery against explicit thresholds.
5. Escalate to Cohere with the redacted debug bundle when provider assistance is required.
6. After recovery, verify normal quality and capacity, document timeline and cause, and assign preventive work.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Unknown cause | Prefer traffic reduction or safe degradation over speculative code changes. |
| Credential suspected | Rotate through the security incident process. |
| Model retired | Use only a pre-evaluated replacement or hold affected traffic. |
| Recovery unstable | Keep the incident open and extend observation. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
incident=INC-77; symptom=429-spike; release=unchanged; status=investigating
```

Expected handoff:

```text
class=capacity; mitigation=queue-cap; impact=stable; evidence=preserved
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Cohere status](https://status.cohere.com)
- [Going live](https://docs.cohere.com/docs/going-live)
