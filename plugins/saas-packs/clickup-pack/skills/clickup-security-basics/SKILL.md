---
name: clickup-security-basics
description: >-
  Harden ClickUp credentials, OAuth callbacks, Workspace boundaries, webhooks, logging, and incident response with least-privilege controls. Use when threat-modeling or reviewing a ClickUp integration. Trigger with "secure ClickUp", "ClickUp security review", or "ClickUp token rotation".
argument-hint: "[repository-or-service] [assessment|remediation]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- security
model: inherit
effort: high
compatibility: Designed for Claude Code; credential and access changes require authorized security and Workspace owners
---
# ClickUp Integration Security

## Overview

Protect long-lived credentials and sensitive work content across outbound API calls, inbound webhooks, queues, logs, and operator tooling.

## Prerequisites

- A data-flow and trust-boundary diagram plus credential/Workspace inventory
- Named security, service, data, and ClickUp Workspace owners
- Synthetic fixtures and an incident/rotation runbook

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Personal tokens do not expire; OAuth tokens currently do not expire but that behavior is subject to change.
- OAuth Authorization Code callbacks require exact redirects, state validation, and server-side client-secret handling.
- Webhook requests use per-webhook secrets and raw-body HMAC-SHA256 in `X-Signature`; ClickUp has no fixed webhook source IP.
- API authorization reflects the user and authorized Workspaces, so the app must enforce its own tenant policy.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Inventory credentials, callbacks, Workspaces, scopes/capabilities, webhooks, queues, stores, logs, and operator access.
2. Remove client-side or repository secrets; inject environment-specific references at runtime.
3. Enforce OAuth state, exact redirect handling, Workspace allow-lists, and deny-by-default write policies.
4. Verify webhook signatures with constant-time comparison before JSON processing; apply replay/idempotency controls.
5. Redact content and secrets from errors, traces, bundles, analytics, and CI artifacts.
6. Exercise leak, revocation, cross-tenant, forged/replayed webhook, partial-write, and incident recovery scenarios.

## Approval Boundaries

Do not rotate shared credentials, reauthorize Workspaces, change ACLs, or inspect private content without accountable owner approval.

## Output

Return threats, controls, credential/tenant map, webhook findings, data exposures, tested incident paths, residual risk, and owners.

## Error Handling

| Condition | Response |
|---|---|
| Credential found in source or logs | Revoke/regenerate, scrub accessible artifacts, and open an incident. |
| Webhook signature is absent/invalid | Reject before parsing or enqueueing. |
| Workspace guard is missing | Disable writes until tenant enforcement exists. |
| Security owner is absent | Do not approve production use. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
secrets-in-source=0; oauth-state=pass; workspace-guard=pass; webhook-hmac=pass; replay-test=pass; residual=2
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Webhook signature](https://developer.clickup.com/docs/webhooksignature)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
