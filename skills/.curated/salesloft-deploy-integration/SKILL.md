---
name: salesloft-deploy-integration
description: >-
  Roll out a Salesloft-backed service through secret injection, contract checks, read-only smoke evidence, bounded canaries, monitoring, and rollback. Use when releasing integration code to a runtime. Trigger with "deploy Salesloft integration", "Salesloft rollout", or "Salesloft release plan".
argument-hint: "[repository-path] [environment] [release-sha]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- deployment
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Integration Rollout

## Overview

This skill deploys application code that calls Salesloft without assuming a particular cloud vendor. It separates process health, Salesloft connectivity, and CRM mutation correctness.

## Prerequisites

- Immutable release SHA and target runtime
- Named Salesloft team, environment, release owner, and rollback owner
- Passing offline contract and security tests
- Approved secret references, callback URL, and canary plan

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect deployment manifests, health checks, secret references, and rollback controls. Use `WebFetch` only for official Salesloft contracts. Use `Write` or `Edit` after the deployment target is confirmed.

## Current Contract

- Inject Bearer credentials through the runtime secret system and bind them to one team.
- Process health is not proof of API auth or correct CRM mutation.
- A webhook receiver must preserve raw request bytes before parsing and verify SHA-1 HMAC.
- Team-wide rate consumption from other integrations can affect the rollout.
- Webhook subscription creation requires a valid OAuth token or API key and event-specific scopes.

## Authentication

Deploy only an approved flow and least-privilege scope set. Prove credential-to-team mapping with a read-only identity request before enabling workers or webhooks.

## Instructions

1. Pin SHA, image or artifact digest, target, team alias, and secret references.
2. Run deployment-config and offline contract checks before applying changes.
3. Deploy with workers and Salesloft writes disabled.
4. Prove health, TLS, and one bounded read-only Salesloft request.
5. Verify webhook raw-body handling and callback-token configuration without a real side effect.
6. Enable a tiny approved canary and reconcile every mutation.
7. Expand only while error, endpoint-cost, remaining-budget, queue, and reconciliation signals stay healthy.

## Approval Boundaries

Do not create subscriptions, alter callback URLs, enable production writes, or broaden traffic without target-specific approval. Roll back when identity, signature, or reconciliation evidence fails.

## Output

Return SHA/digest, target, team proof, config checks, smoke result, canary evidence, monitoring snapshot, rollout state, and rollback receipt.

## Error Handling

| Condition | Response |
|---|---|
| Wrong team identity | Disable workers and replace the secret mapping. |
| Webhook signature fails | Reject delivery and halt subscription cutover. |
| Rate headroom collapses | Pause expansion and inspect team-wide consumers. |
| Canary mismatch | Stop, reconcile, and roll back before retrying. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
sha=a1b2c3d; health=pass; auth-read=pass; canary=2/2 reconciled; rollout=10%
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Webhook introduction](https://developers.salesloft.com/docs/platform/webhooks/introduction/)
- [Rate limits](https://developers.salesloft.com/docs/platform/api-basics/rate-limits/)
