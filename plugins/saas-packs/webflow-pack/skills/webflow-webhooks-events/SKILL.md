---
name: webflow-webhooks-events
description: >-
  Register and operate Webflow webhooks with current event names, signature verification, replay defense, and idempotency. Use when receiving site, CMS, form, ecommerce, page, or comment events. Trigger with "Webflow webhook", "verify Webflow signature", or "Webflow events".
argument-hint: "[project-path] [site-id] [trigger-type]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- webhooks
- events
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Webhooks and Events

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- API-created webhook requests include `x-webflow-timestamp` and `x-webflow-signature`; dashboard-created webhooks lack the headers needed for signature validation.
- The signature is SHA-256 HMAC over the documented timestamp/body representation. Webflow recommends its SDK verifier because the implementation may evolve.
- Qualifying site-token webhooks receive their own secret; OAuth-created webhooks use the OAuth app client secret.
- Webflow retries a failed delivery up to three additional times. Redirects, non-200 responses, TLS problems, and timeouts count as failures.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Choose an official trigger type and determine its required scope from the create-webhook endpoint and event reference.
2. Make the HTTPS handler preserve the request representation required by the SDK verifier and reject missing headers.
3. Verify signature and timestamp before parsing sensitive data; reject requests older than the documented five-minute window.
4. Derive an idempotency key from stable event and payload identifiers, then enqueue work and return HTTP 200 quickly.
5. Redact form and ecommerce data in logs and set retention for payloads and deduplication keys.
6. Show the destination, trigger, site ID, auth mode, and rollback before registration; after approval, verify the stored webhook and a controlled test delivery.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Signature headers absent | Confirm whether the webhook was created in the dashboard; recreate through API if verification is required. |
| Repeated delivery | Return the prior success for the idempotency key without repeating downstream mutation. |
| Handler redirects or times out | Expose a direct HTTPS route, acknowledge quickly, and move processing to a queue. |

## Examples

Create a `collection_item_published` webhook through the API, verify with the official SDK and the correct signing key, reject timestamps older than five minutes, deduplicate the event, enqueue processing, and return 200.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
