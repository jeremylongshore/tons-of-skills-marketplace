---
name: cohere-enterprise-rbac
description: >-
  Map Cohere Team Owner and User roles to application authorization, key ownership, tenant isolation, and audit controls. Use when governing multi-team Cohere access. Trigger with "Cohere RBAC", "Cohere team roles", or "Cohere enterprise keys".
argument-hint: "[team] [environment] [role-review]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- access-control
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Enterprise Access Control

## Overview

Use Cohere's documented Team roles for platform administration while enforcing fine-grained workload authorization in the application and secret manager.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Cohere Teams document Owner and User roles; Owners have additional membership, production-key, billing, and production-form powers.
- Team users can still have broad key and usage capabilities, so provider roles alone are not application RBAC.
- Separate human administration from runtime service identities and environment-specific credentials.
- Enforce tenant, model, endpoint, tool, and budget policy before provider calls.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Inventory Cohere teams, members, roles, keys, environments, service identities, and billing owners.
2. Map Owner and User capabilities to least-privilege job functions and separation-of-duties requirements.
3. Move runtime keys into approved secret stores and bind retrieval to named workloads.
4. Implement application authorization for tenant data, allowed models, endpoints, tools, and spend.
5. Review membership, keys, usage, invoices, and access evidence on a fixed cadence.
6. Test member removal, key rotation, service revocation, tenant denial, and emergency access.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Orphaned owner | Assign an accountable owner before changing production access. |
| Shared human key | Replace it with workload-owned environment credentials. |
| Role too broad | Compensate with secret-manager and application policy or escalate. |
| Former member | Remove access and rotate credentials they could retrieve. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
team=platform-ai; environments=staging,prod; tenants=multi; review=quarterly
```

Expected handoff:

```text
roles=mapped; keys=workload-owned; app-rbac=enforced; review=evidenced
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Teams and roles](https://docs.cohere.com/reference/teams-and-roles)
- [API keys](https://dashboard.cohere.com/api-keys)
