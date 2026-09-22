---
name: webflow-sdk-patterns
description: >-
  Apply maintainable patterns around an official Webflow SDK without inventing method contracts. Use when centralizing clients, pagination, retries, tenancy, or typed boundaries. Trigger with "Webflow SDK pattern", "wrap Webflow client", or "paginate Webflow".
argument-hint: "[project-path] [javascript|python]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- sdk
- architecture
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow SDK Patterns

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Webflow publishes official JavaScript and Python SDKs generated from the current API contract.
- Official SDKs include exponential backoff for rate-limit responses, but applications still need bounded work queues and business-level retry policy.
- The Content Delivery API can be selected with its documented base URL for cached live-item reads; it is not a general replacement for Data API writes.
- SDK return shapes and method names must come from the installed package types or current official reference, not remembered examples.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Locate every Webflow client construction and direct API call; group them by token, site, environment, and read/write intent.
2. Create one configuration boundary that validates the token variable name, API base URL, and expected site ID without logging values.
3. Wrap pagination as an iterator with explicit page and item limits. Preserve cursors or offsets exactly as returned.
4. Centralize error normalization around HTTP status, Webflow `code`, `message`, `details`, and retry headers.
5. Use a shared limiter for callers that share an API key. Let the official SDK backoff operate inside a bounded job policy.
6. Add contract tests against fixtures and one read-only integration smoke before migrating callers.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Generated method differs | Trust installed SDK types and the current reference; update the adapter, not every caller. |
| 429 loop | Honor `Retry-After`, cap attempts, and coordinate callers sharing the same key. |
| Cross-tenant result | Stop and require a verified site-ID allowlist before any write path. |

## Examples

Replace scattered client construction with a site-keyed factory, a bounded collection-item iterator, normalized errors, and tests that prove one tenant cannot request another tenant's site.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
