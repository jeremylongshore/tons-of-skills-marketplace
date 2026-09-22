---
name: attio-deploy-integration
description: >-
  Plan and execute a staged deployment for an external Attio REST integration with secret injection, contract tests, read-only smoke evidence, canary writes, and rollback. Use when releasing Attio-backed services. Trigger with "deploy Attio integration", "Attio rollout", or "Attio release plan".
argument-hint: "[repository-path] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- deployment
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Integration Rollout

## Overview

This skill releases application code that calls Attio's REST API. It uses progressive evidence so a bad schema mapping, scope, or retry policy is caught before broad CRM mutation.

## Prerequisites

- A versioned application artifact and tested configuration
- Environment-specific Attio workspace and secret references
- A disposable canary record or approved read-only smoke path
- Defined rollback owner, trigger, and previous artifact

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect deployment manifests, secret names, health checks, migrations, and rollback commands. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` after the rollout target and approval boundary are confirmed.

## Current Contract

- Inject tokens from the deployment platform; never bake them into images or manifests.
- Validate object and list schemas in the target workspace before enabling writes.
- Keep read and write traffic controls separate because Attio publishes different limit tiers.
- A successful process health check is not proof that CRM mutations are correct.

## Authentication

Use the target environment's least-privilege single-workspace token or tenant-specific OAuth token. Confirm workspace identity and required endpoint scopes before canary traffic.

## Instructions

1. Compare artifact, configuration, secret references, workspace alias, and endpoint set with the approved release record.
2. Run offline contract and redaction tests on the exact artifact.
3. Deploy with Attio writes disabled and perform a bounded read-only smoke request.
4. Confirm current object/list attributes and pagination behavior in the target workspace.
5. Enable one idempotent or reversible canary write, then read it back.
6. Expand traffic gradually while watching 4xx, 429, 5xx, latency, duplicate writes, and queue age.
7. Roll back on a declared trigger and verify both application and CRM state.

## Approval Boundaries

Production writes, token rotation, schema changes, and cleanup of canary data require exact target display and owner approval. Do not roll forward through unexplained validation or authorization failures.

## Output

Return artifact identity, environment checks, read smoke, canary evidence, traffic stage, observed metrics, rollback status, and residual risks.

## Error Handling

| Condition | Response |
|---|---|
| Workspace identity is uncertain | Stop before enabling traffic. |
| Schema differs from staging | Disable writes and reconcile mappings. |
| 429 rate increases | Hold or reduce traffic and honor `Retry-After`. |
| Canary is not reversible | Do not use it; choose a safer proof. |

## Examples

Input:

```text
artifact=release-sha; environment=production; writes=initially-disabled
```

Expected handoff:

```text
read-smoke=pass; canary=verified; expansion=approved; rollback=ready
```

This result binds the rollout decision to the tested artifact and rollback path.

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication](https://docs.attio.com/rest-api/guides/authentication)
- [Rate limiting](https://docs.attio.com/rest-api/guides/rate-limiting)
- [REST API overview](https://docs.attio.com/rest-api/overview)
