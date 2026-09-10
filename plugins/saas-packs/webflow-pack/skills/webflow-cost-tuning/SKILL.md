---
name: webflow-cost-tuning
description: >-
  Reduce avoidable Webflow integration cost and plan pressure using measured API, storage, traffic, and deployment usage. Use when right-sizing a plan or replacing wasteful polling and origin reads. Trigger with "Webflow cost", "right-size Webflow", or "reduce Webflow usage".
argument-hint: "[project-path] [site-id] [workload]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- cost
- capacity
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Plan and Usage Tuning

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Pricing and plan entitlements change; never embed cached dollar figures or promise savings without current billing evidence.
- Site plan affects general Data API request limits, while endpoint and product entitlements can impose separate constraints.
- Cached Content Delivery reads effectively avoid API rate limits, but cache misses and bypasses still reach origin.
- Webhooks can replace polling for documented events; they do not eliminate reconciliation or every read workload.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Collect the current plan, invoices or usage exports the user provides, sites, traffic, API headers, deploy frequency, and workload schedule.
2. Separate fixed subscription choices from measured drivers such as origin calls, polling, asset traffic, build frequency, and external infrastructure.
3. Rank optimizations by evidence: remove unused calls, cache eligible live reads, subscribe to events, batch supported writes, and reduce duplicate deployments.
4. Check current official pricing and plan pages at decision time; label all forecasts with date, assumptions, and excluded charges.
5. Model baseline, expected range, implementation effort, reliability tradeoffs, and a rollback for each change.
6. Run one bounded experiment and compare measured usage and service quality before recommending a plan change.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| No billing evidence | Provide a measurement plan rather than a savings claim. |
| Optimization harms freshness | Restore the prior path and renegotiate the freshness budget. |
| Feature unavailable on plan | Present the current entitlement source and a supported alternative. |

## Examples

Measure cold and cached CMS reads for one week, replace eligible polling with webhooks, quantify origin-call reduction, then consult current plan pricing before proposing any downgrade.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
