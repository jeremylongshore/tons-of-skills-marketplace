---
name: miro-hello-world
description: "Design and implement a bounded, read-only Miro connectivity probe that proves authorization context before writes are enabled. Use when smoke-testing a new Miro integration. Trigger with \"test Miro connection\"."
argument-hint: "[environment] [team-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- quickstart
- connectivity
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Read-Only Connection Probe

## Overview

Run the smallest useful REST probe and produce a redacted receipt. A successful HTTP response is insufficient unless tenant and scope context also match; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- An approved OAuth installation with `boards:read`
- Expected team and user context
- A test board or permission to list board metadata

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary. These declared tools do not call authenticated Miro APIs or deployment CLIs; implement client, configuration, and test changes, then return exact operator commands or an approval-gated handoff for live execution.

## Current Contract

- `GET https://api.miro.com/v2/boards` requires `boards:read`.
- Filtering by `team_id` or `project_id` is indexed immediately; other search filters can lag by several seconds.
- Board-list responses are paginated and must not be treated as a complete inventory from one page.
- Response bodies can contain confidential names, descriptions, owners, and links.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Inspect the integration configuration without reading credential values.
2. Confirm token context and expected team before querying board resources.
3. Request one bounded board page filtered to the approved team when available.
4. Record status, latency, rate-limit headers, page size, and only redacted board identifiers.
5. Verify the response shape and pagination cursor handling against the official reference.
6. Keep writes disabled and return the minimal evidence needed to authorize the next stage.

## Approval Boundaries

Do not create a sample board or item as part of a connectivity probe unless the user explicitly authorizes that mutation and identifies the test board. Pause when the responsible owner or exact target is uncertain.

## Output

Return environment, context match, scope sufficiency, HTTP status, latency, rate-limit headroom, page/cursor facts, and go/no-go. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| 401 | Refresh once if eligible, then stop and repair authorization. |
| 403 or 404 | Check scope, membership, board visibility, and tenant context without guessing. |
| 429 | Honor reset headers and stop the probe. |
| Unexpected response shape | Capture a redacted schema diff and hold writes. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
environment=dev; context=matched; status=200; boards-returned=1; cursor=present; remaining-credits=99500; writes=off
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Get boards](https://developers.miro.com/reference/get-boards)
- [Permission scopes](https://developers.miro.com/reference/scopes)
