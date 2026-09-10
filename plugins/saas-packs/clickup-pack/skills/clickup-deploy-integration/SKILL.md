---
name: clickup-deploy-integration
description: >-
  Deploy and roll back a server-side ClickUp API and webhook service with secret injection, workspace guards, health probes, and durable queues. Use when releasing a ClickUp integration. Trigger with "deploy ClickUp", "ClickUp production release", or "ClickUp webhook service".
argument-hint: "[service-path] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- deployment
model: inherit
effort: high
compatibility: Designed for Claude Code; deployment requires platform access and environment-specific ClickUp credentials
---
# Deploy a ClickUp Integration

## Overview

Release the integration as a reversible server-side boundary that keeps credentials out of clients and acknowledges webhooks quickly.

## Prerequisites

- A tested server-side adapter, environment inventory, and rollback artifact
- Environment-scoped secret references and authorized Workspace allow-lists
- HTTPS webhook ingress, raw-body signature verification, durable queueing, and observability

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- ClickUp tokens belong on the server; browser CORS errors are not solved by exposing a token.
- Webhook verification uses the raw request body, the webhook secret, HMAC-SHA256, and `X-Signature`.
- Webhook handlers should acknowledge within ClickUp's seven-second health boundary and process asynchronously.
- v2 and v3 base paths remain explicit per operation.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Inventory deploy target, endpoint/version matrix, callback URLs, secret references, and Workspace allow-lists.
2. Build and test offline contracts, raw-body signature handling, queue idempotency, and redaction.
3. Deploy dark with outbound writes disabled and webhook registration unchanged.
4. Run bounded identity, Workspace, health, and synthetic signed-event probes.
5. Canary trusted traffic, watch rate/error/webhook-health metrics, and verify durable side effects.
6. Promote or roll back; then reconcile secrets, callbacks, queues, and deployment evidence.

## Approval Boundaries

Require explicit approval before production traffic, webhook registration changes, task mutations, ACL changes, or irreversible infrastructure teardown.

## Output

Return artifact digest, environment, version matrix, secret references, probe/canary result, webhook health, promotion decision, and rollback target.

## Error Handling

| Condition | Response |
|---|---|
| Signature verification fails | Reject the request and inspect raw-body handling; do not weaken verification. |
| Health probe exposes content | Stop and replace it with metadata-only evidence. |
| Canary crosses Workspace boundary | Disable writes and roll back immediately. |
| Rollback cannot restore callback routing | Keep traffic dark and escalate. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
env=production; artifact=sha256:...; writes=disabled; signed-probe=pass; canary=pass; rollback=ready
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Webhook signature](https://developer.clickup.com/docs/webhooksignature)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
