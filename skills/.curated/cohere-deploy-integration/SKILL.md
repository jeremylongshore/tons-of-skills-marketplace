---
name: cohere-deploy-integration
description: >-
  Deploy a Cohere-powered service with server-side secrets, streaming-safe infrastructure, health checks, canarying, and rollback. Use when shipping Cohere workloads. Trigger with "deploy Cohere", "Cohere production deploy", or "Cohere streaming service".
argument-hint: "[repository-path] [platform] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- deployment
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Deployment Integration

## Overview

Release the application around Cohere without embedding the key in clients, turning health checks into billable generation, or hiding provider failure.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Call Cohere from a trusted server runtime; never expose the provider key to browsers or mobile clients.
- Use a local process health check and a separate protected provider-readiness probe.
- Streaming paths require proxy buffering, idle timeout, cancellation, and client-disconnect tests.
- Model selection and fallback must be explicit deployment configuration reviewed against current availability.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Inspect the target platform's secret, egress, timeout, streaming, autoscaling, and rollback behavior.
2. Inject `CO_API_KEY` from the platform secret manager and restrict access to the service identity.
3. Set explicit model IDs, request bounds, client timeouts, concurrency, and circuit-breaker thresholds.
4. Deploy to a non-production environment and test cancellation, throttling, timeout, and provider outage behavior.
5. Canary production traffic while watching quality, error, latency, queue, and spend signals.
6. Promote or roll back using recorded thresholds and preserve the deployment evidence.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Key in client bundle | Stop release, remove it, and rotate the exposed key. |
| Buffered stream | Fix proxy/runtime streaming settings before promotion. |
| Cold-start timeout | Measure and tune platform startup separately from provider latency. |
| Provider outage | Trip the circuit and use the approved degradation path. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
platform=cloud-run; stream=true; canary=5%; provider-probe=protected
```

Expected handoff:

```text
secrets=server-only; stream=pass; canary=healthy; rollback=verified
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Going live](https://docs.cohere.com/docs/going-live)
- [Cloud compatibility](https://docs.cohere.com/docs/cohere-works-everywhere/)
