---
name: miro-local-dev-loop
description: "Build repository-side scaffolding for a repeatable Miro development loop with isolated apps, fixture boards, contract tests, cleanup, and explicit operator commands. Use when developing Miro integrations locally. Trigger with \"start Miro dev loop\"."
argument-hint: "[feature] [test-board-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- development
- testing
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Local Development Loop

## Overview

Shorten feedback cycles without turning a real collaboration board into a test fixture. Separate configuration, deterministic fixtures, and destructive cleanup; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- A non-production Miro app and Developer team
- A dedicated test board with an accountable owner
- Local configuration names, fixture schema, and cleanup policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary. These declared tools do not call authenticated Miro APIs or deployment CLIs; implement client, configuration, and test changes, then return exact operator commands or an approval-gated handoff for live execution.

## Current Contract

- Web SDK code runs only while its Miro app context is loaded on a board.
- REST OAuth and Web SDK authorization are separate; hybrid apps must configure both flows.
- Board operations are asynchronous and can take time to synchronize.
- REST test traffic consumes the same per-user/per-application credit budget as other callers.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Map the feature to REST, Web SDK, or a deliberate hybrid before writing code.
2. Load configuration by environment and assert that production app, team, and board IDs are absent.
3. Create deterministic fixture items with a run marker on the dedicated test board.
4. Run unit tests with schema-faithful fixtures, then one bounded live contract test.
5. Compare the observed response and rate headers with the recorded contract.
6. Delete only run-marked fixtures after verifying board ID, item IDs, and ownership; retain a redacted receipt.

## Approval Boundaries

Do not expose a local callback publicly, install an app to another team, or delete unmarked board content without explicit approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return environment guards, fixture IDs as hashes, test results, observed contract drift, cleanup count, and leftovers. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Production identifier detected | Abort before making any request. |
| Fixture create partially fails | Stop, inventory confirmed creations, and clean only those IDs. |
| Asynchronous state is not visible | Retry a bounded read with jitter; do not duplicate the write. |
| Cleanup ownership is uncertain | Leave the item and flag it for a board owner. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
app=dev; board=test-only; fixtures-created=3; contract-tests=8/8; fixtures-removed=3; production-ids=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [REST OAuth from Web SDK](https://developers.miro.com/docs/enable-api-authentication-from-sdk-authorization)
- [Web SDK board reference](https://developers.miro.com/docs/websdk-reference-board)
