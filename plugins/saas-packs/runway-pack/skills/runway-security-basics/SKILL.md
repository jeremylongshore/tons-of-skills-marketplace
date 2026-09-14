---
name: runway-security-basics
description: >-
  Harden Runway keys, organization access, prompts, media, generated outputs, and support evidence. Use when threat-modeling an integration. Trigger with: "secure Runway API", "Runway key rotation", "Runway media privacy".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[service-and-data-class]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - security
  - secrets
  - moderation
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Runway Credential, Media, and Moderation Controls

## Overview

Runway integrations handle organization-scoped credentials and potentially sensitive media. Security must cover key lifecycle, server-only egress, input rights, temporary URL capabilities, moderation outcomes, output access, evidence minimization, and incident response.

## Prerequisites

- Data classification and media-rights policy
- Runway organization role and key inventory
- Secret manager, private object storage, audit logging, and incident owners

## Instructions

### Step 1: Inventory identities and keys

List organization members, roles, keys, consumers, environments, creation dates, and rotation owners. Removing a member does not disable their organization-scoped keys, so revocation is a separate control.

### Step 2: Enforce server-only access

Keep `RUNWAYML_API_SECRET` in a secret manager and restrict egress to Runway hosts. Prevent browser exposure, repository commits, shell history, build arguments, logs, traces, and support archives.

### Step 3: Govern input content

Verify rights, tenant authorization, data minimization, acceptable-use policy, file type and size, and public-URL exposure. Treat prompts and source media as sensitive application data.

### Step 4: Handle moderation honestly

Expect moderation as a failed task and inspect `failureCode`. Do not automatically retry safety failures or expose unsafe diagnostics; repeated moderated requests can threaten account availability.

### Step 5: Control media capabilities

Treat public input URLs, `runway://` URIs, and signed output URLs as temporary access capabilities. Copy approved output to owned private storage, scan and validate it, and issue internal authorized links.

### Step 6: Prove rotation and response

Rotate keys through a canary, explicitly disable old credentials, scan for leaks, and maintain a playbook for revocation, artifact restriction, customer notification, and evidence deletion.

## Authentication

Bearer secrets authenticate the organization, not an end user. Authorization in the product must therefore occur before the server uses Runway; API authentication does not replace tenant, actor, media-rights, or budget checks.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Key, role, consumer, and data-flow inventory
- Threat model and prioritized credential/media/moderation controls
- Rotation test and incident-response evidence

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A developer leaves the organization. The admin removes membership, separately identifies and disables every key used by that service, deploys a replacement secret, proves one read-only canary, and scans logs and artifacts for the old prefix.

## Error Handling

| Failure | Response |
| --- | --- |
| Secret scanner finds a Runway key | Revoke it immediately, restrict the artifact, determine exposure, rotate consumers, and document the incident. |
| Customer media is on a public URL | Stop submission until access and rights meet policy; use a controlled upload path where appropriate. |
| Safety failure is retried automatically | Disable that retry class and review prompt, media, and moderation policy. |

## Validation

Test client-side bundle inspection, secret scanning, least-privilege deployment access, old-key failure after rotation, media authorization, output URL redaction, safety-failure handling, and evidence expiry.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
