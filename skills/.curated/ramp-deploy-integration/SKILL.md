---
name: ramp-deploy-integration
description: >-
  Deploy a Ramp API integration with environment isolation, secret controls, schema gates, reconciliation, and a reversible production rollout. Use when promoting a service, worker, webhook receiver, or accounting connector. Trigger with "deploy Ramp integration" or "Ramp rollout".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, deployment, rollout, reliability]
---
# Ramp Integration Deployment and Rollout

## Overview

Promote the exact tested artifact, not an unreviewed configuration. Resolve environment and credential provenance before startup, begin with bounded reads, and gate all writes behind explicit business approval and reconciliation.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Sandbox and production are separate Ramp environments with different hosts, credentials, tokens, and data.
- OAuth tokens are bound to scopes and environment; a passing sandbox test does not authorize production.
- Webhook consumers must be externally reachable and idempotent, while accounting writers need durable downstream receipts.
- The OpenAPI schema and current guide exports are the contract inputs for release validation.

## Instructions

1. Freeze the candidate artifact, dependency lock, OpenAPI checksum, configuration schema, data migration, scopes, event subscriptions, and rollback artifact.

2. Validate secrets are references to the target environment's approved store; reject demo hosts in production and production hosts in sandbox.

3. Deploy dark with outbound writes disabled, prove health, token acquisition, sanitized tracing, queue durability, and one minimum-scope read.

4. Canary one entity, event type, or bounded accounting cohort; reconcile object counts, amounts, duplicates, lag, and errors before expansion.

5. Enable approved writes gradually, monitor rollback thresholds, then preserve artifact digest, config digest, approvers, canary evidence, and final reconciliation.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Service and security owners approve artifact, configuration, and secrets. Finance/data owners approve entities and writes; the incident owner has authority to halt or roll back.

## Output

A signed deployment record with artifact and config digests, environment proof, scope/event inventory, canary and reconciliation evidence, rollback thresholds, and owners.

## Error Handling

| Condition | Response |
|---|---|
| The artifact requests an unexpected scope | Block startup and return to application/security review. |
| Canary reconciliation diverges | Disable writes, preserve checkpoints, repair or reverse the bounded cohort, and do not expand. |
| Rollback cannot read the new data shape | Keep writes disabled until backward compatibility or a tested data rollback exists. |

## Examples

### Example 1

Deploy a webhook consumer dark, replay sandbox fixtures, then canary only `transactions.ready_to_sync` for one entity.

### Example 2

Promote an ERP worker with production writes disabled until its read-only inventory exactly reconciles.

## Validation

- The deployed digest equals the reviewed and tested digest.
- Host, credentials, entity, scopes, and event subscriptions prove the intended environment.
- Canary records reconcile and duplicate delivery does not duplicate business effects.
- Rollback is executable and has a named decision owner.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
