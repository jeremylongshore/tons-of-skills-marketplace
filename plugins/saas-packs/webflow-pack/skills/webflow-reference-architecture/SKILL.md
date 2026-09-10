---
name: webflow-reference-architecture
description: >-
  Design a Webflow integration architecture with explicit Data API, Content Delivery, webhook, identity, queue, and publication boundaries. Use when starting a service or untangling a coupled integration. Trigger with "Webflow architecture", "design Webflow integration", or "Webflow service layout".
argument-hint: "[project-path] [single-site|multi-tenant]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- architecture
- integration
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Integration Reference Architecture

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Data API is the fresh read/write control plane; Content Delivery is a cached live-content read surface.
- Webhooks provide event signals but require authentication, idempotency, retries, and periodic reconciliation.
- Token type and site identity are architectural boundaries. A multi-tenant app should not share a broad internal token.
- CMS staging and publication are different states and should have separate application operations and approval policy.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Inventory actors, sites, locales, data classifications, freshness needs, write paths, event paths, and operational owners.
2. Draw trust boundaries for OAuth or site tokens, secret storage, Webflow APIs, queues, databases, logs, and public delivery.
3. Define adapters for Data API, Content Delivery, and webhook verification so SDK-generated contracts do not leak through the domain layer.
4. Separate read models, staged-write workflows, publication commands, and destructive operations.
5. Specify idempotency, reconciliation, rate budgets, cache policy, observability, and recovery for each data flow.
6. Validate the design with one happy path, one auth failure, one rate-limit event, one duplicate webhook, and one uncertain write.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Site identity implicit | Add an allowlisted site/tenant mapping before implementation. |
| Publish coupled to save | Split preparation and live publication into separately authorized commands. |
| Webhook is sole truth | Add reconciliation against the authoritative Webflow resource. |

## Examples

A multi-tenant CMS service stores one OAuth grant per tenant, uses Data API for staged writes, Content Delivery for eligible live reads, verifies and deduplicates webhooks, and gates publication separately.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
