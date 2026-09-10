---
name: together-deploy-integration
description: >-
  Deploy and roll back Together AI integrations across serverless inference or v2 Dedicated Model Inference with secret injection, health probes, traffic control, and cost shutdown. Use when releasing Together-backed services or dedicated models. Trigger with "deploy Together", "Together dedicated endpoint", or "Together rollout".
argument-hint: "[repository-path] [serverless|dedicated-v2] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- deployment
model: inherit
effort: high
compatibility: Designed for Claude Code; deployment requires platform access and Together AI project authorization
---
# Together AI Deployment Integration

## Overview

This skill separates application release from paid Together capacity changes and defines a reversible deployment for serverless or current v2 dedicated inference.

## Prerequisites

- A tested application artifact and model-quality evidence
- Environment-scoped secret references and network egress policy
- Current model availability plus serverless or dedicated capacity decision
- Health, canary, rollback, cost, and teardown owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect manifests, secret wiring, health checks, and rollback automation. Use `WebFetch` for current Together model and DMI lifecycle contracts. Use `Write` or `Edit` only for approved deployment files after the target platform is confirmed.

## Current Contract

- Serverless needs no GPU provisioning and uses the shared inference API with a current model ID.
- New dedicated deployments use Together's v2 endpoint/deployment model and beta management surfaces.
- Legacy v1 endpoint creation is retired; do not publish `client.endpoints.create(model=..., hardware=...)` as the new path.
- Dedicated replicas bill while running. Scale to zero or delete after an approved rollback or experiment.

## Authentication

Inject a project-scoped `TOGETHER_API_KEY` from the deployment platform's secret manager. Dedicated management also requires authorized project context; never expose management identifiers or Bearer headers unnecessarily.

## Instructions

1. Classify the workload as serverless or dedicated from latency, throughput, model, and utilization evidence.
2. Pin the application artifact, SDK major, configuration schema, model policy, and secret references.
3. For dedicated v2, resolve model/config resources, create the deployment, and poll to ready before routing traffic.
4. Run a non-sensitive health probe that validates provider reachability and response shape.
5. Shift a bounded canary while monitoring error rate, latency, usage, quality, and cost.
6. Promote or roll back explicitly; scale obsolete dedicated replicas to zero and verify billing disposition.

## Approval Boundaries

Do not provision paid hardware, change traffic weights, rotate production keys, or promote a model without the named owners and an executable rollback.

## Output

Return deployment mode, artifact/model/config identities, secret reference, readiness and canary evidence, traffic state, cost state, rollback result, and teardown owner.

## Error Handling

| Condition | Response |
|---|---|
| Legacy v1 create returns `403` | Stop and migrate to the current v2 DMI flow. |
| Deployment ready but routing fails | Verify traffic split and endpoint inference name. |
| Canary regresses | Route back and preserve redacted evidence. |
| Teardown unverified | Keep the change open; dedicated replicas may still bill. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
mode=dedicated-v2; deployment=ready; canary=5%; rollback=verified; obsolete-replicas=zero
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Dedicated Model Inference](https://docs.together.ai/docs/dedicated-endpoints/overview)
- [Migrate from v1](https://docs.together.ai/docs/dedicated-endpoints/migrate-from-v1)
- [Official dedicated skill](https://github.com/togethercomputer/skills/tree/main/skills/together-dedicated-model-inference)
