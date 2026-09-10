---
name: miro-webhooks-events
description: "Analyze and execute this workflow: replace retired Miro REST webhooks with explicit freshness requirements, bounded reconciliation, or in-board Web SDK events. Use when designing Miro change detection. Trigger with \"Miro webhooks\"."
argument-hint: "[event-use-case] [freshness-slo]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- events
- web-sdk
- reconciliation
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Eventing Gap and Supported Alternatives

## Overview

Prevent new systems from depending on Miro's discontinued experimental webhook infrastructure. Select an alternative that honestly represents durability and freshness; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Event use case, consumers, and freshness/loss tolerance
- Current REST and Web SDK capability inventory
- Authorized boards, rate budget, and reconciliation state store

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Miro discontinued experimental REST webhooks and `/v2-experimental/webhooks/board_subscriptions`.
- There is no current production Miro REST callback/signature contract documented as its replacement.
- Web SDK UI events such as `items:create` and `items:delete` run in active board app contexts; they are not durable server-to-server delivery.
- `experimental:items:update` remains experimental, and `items:create` does not fire for copy-paste or duplication.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Inventory every retired subscription call, callback handler, signature assumption, queue, and downstream consumer.
2. Define required freshness, completeness, replay, ordering, and active-board assumptions.
3. Choose bounded REST reconciliation for durable server state or supported Web SDK UI events for active in-board behavior.
4. For polling, store normalized checkpoints, traverse cursors safely, budget credits, and run periodic full reconciliation.
5. For Web SDK events, register and unregister stable handlers, tolerate duplicates/misses, and label session-only semantics.
6. Remove retired endpoints and secrets; test detection gaps and publish the residual freshness/loss contract.

## Approval Boundaries

Do not reactivate retired endpoints, invent a signature header, market session events as durable delivery, or increase polling load without owner approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return retired dependency inventory, chosen alternative, freshness/loss guarantee, rate budget, checkpoint design, tests, and migration plan. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Retired endpoint is still called | Disable that path and move the consumer to reconciliation or an approved alternative. |
| Consumer requires lossless real time | Report that current documented capabilities do not satisfy it. |
| Web SDK event misses duplication | Reconcile rather than claiming completeness. |
| Polling nears credit limit | Slow the schedule, narrow reads, or renegotiate freshness. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
retired-subscriptions=3; replacement=cursor-reconcile; interval=5m; full-scan=24h; credit-headroom=35%; lossless=no
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Webhooks removal](https://developers.miro.com/changelog/removed-experimental-webhooks-support)
- [Web SDK UI events](https://developers.miro.com/docs/websdk-reference-ui)
