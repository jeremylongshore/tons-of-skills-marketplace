---
name: fireflies-install-auth
description: >-
  Establish a least-privilege Fireflies API identity, protect its bearer key, and prove the authenticated GraphQL boundary without exposing meeting data. Use when bootstrapping or repairing an integration. Trigger with "configure Fireflies API", "Fireflies auth failed", or "rotate Fireflies key".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <environment>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, authentication, security]
model: inherit
effort: medium
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies API Identity and Access Setup

## Overview

Create an auditable identity boundary before any transcript query or mutation. A successful request proves only that the key is accepted; it does not grant permission to enumerate or export meeting content.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Fireflies uses POST requests to https://api.fireflies.ai/graphql with Content-Type application/json and Authorization: Bearer <API key>. Obtain the key from the Fireflies Integrations page, keep it server-side, and use the smallest identity query needed to confirm the principal and team context.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Identify the owning Fireflies user or team, intended environment, and exact read or mutation capabilities.
2. Create or retrieve the API key through the Fireflies dashboard; never ask a user to paste it into chat.
3. Store the key in the approved secret manager and inject it as FIREFLIES_API_KEY only at runtime.
4. Send a minimal user query from a controlled server-side client and inspect both HTTP status and the GraphQL errors array.
5. Record the authenticated user ID, team context, key owner, storage location, and rotation owner without recording the key.
6. Test an invalid-key path and confirm logs redact Authorization and response data.
7. Document rotation and revocation steps before enabling production access.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before creating, rotating, revoking, or broadening a production key, changing its owning account, or querying any real meeting record.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- auth_failed: verify the Bearer scheme, secret injection, and key lifecycle without printing the token.
- HTTP success with GraphQL errors: treat the operation as failed and record safe error metadata.
- Unexpected team visibility: stop and review the key owner's role before continuing.

## Examples

- "Prove staging auth" returns only the principal and a redacted request receipt.
- "Use this key in browser code" is rejected because bearer keys must remain server-side.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
