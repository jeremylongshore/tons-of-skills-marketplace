---
name: miro-upgrade-migration
description: "Plan and implement a Miro integration upgrade through contract inventory, pinned dependencies, shadow-read design, reversible rollout, and an approval-gated live handoff. Use when changing API or SDK versions. Trigger with \"upgrade Miro integration\"."
argument-hint: "[current-version] [target-version]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- upgrade
- migration
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Dependency and API Upgrade

## Overview

Treat upgrades as contract changes, not package-only edits. Separate REST major-version migration from client-library and Web SDK lifecycle changes; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Current and target dependency/API inventory
- Official changelog, lifecycle, and endpoint references
- Representative fixtures, sandbox board, and rollback artifact

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary. These declared tools do not call authenticated Miro APIs or deployment CLIs; implement client, configuration, and test changes, then return exact operator commands or an approval-gated handoff for live execution.

## Current Contract

- Miro maintains one recommended production REST major version; current resource work uses v2.
- OAuth `/v1/oauth` was not included in the REST v1-to-v2 resource migration.
- v2 replaced polymorphic widgets with item-type endpoints and changed several relationship and pagination models.
- Experimental endpoints can change or be removed and cannot silently graduate into a production dependency.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Inventory SDK, raw endpoints, OAuth, scopes, response schemas, pagination, item types, and experimental use.
2. Diff current code against official lifecycle, migration, reference, and pinned package contracts.
3. Build compatibility fixtures and translate one operation at a time behind the adapter boundary.
4. Run shadow reads and normalized comparisons on a sandbox board before enabling writes.
5. Canary the target with error, latency, credit, and semantic-drift thresholds.
6. Promote only after reconciliation; retain the prior artifact/config and exercise rollback.

## Approval Boundaries

Do not change a production API path, scopes, token mode, or enable a formerly experimental capability without service-owner approval and fresh evidence. Pause when the responsible owner or exact target is uncertain.

## Output

Return contract diff, dependency changes, compatibility results, shadow/canary metrics, cutover decision, rollback evidence, and leftovers. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Official docs and SDK disagree | Prefer the observed official endpoint contract and pin/escalate the client discrepancy. |
| Shadow reads diverge | Stop promotion and classify schema versus data drift. |
| Experimental path remains | Isolate or remove it before production approval. |
| Rollback changes data | Use a forward repair plan and obtain explicit approval. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
rest=v2; oauth=v1-unchanged; sdk=old->pinned; shadow=250/250-equal; canary-errors=0; rollback=passed
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [REST comparison](https://developers.miro.com/docs/rest-api-comparison-guide)
- [Lifecycle policy](https://developers.miro.com/docs/lifecycle-policy)
