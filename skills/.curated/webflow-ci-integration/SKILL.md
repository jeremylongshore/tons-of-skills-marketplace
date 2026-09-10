---
name: webflow-ci-integration
description: >-
  Build fail-closed CI for Webflow Data API or Cloud changes with pinned tools and explicit identities. Use when adding automated tests, non-interactive CLI work, or gated deployment. Trigger with "Webflow CI", "Webflow GitHub Actions", or "automate Webflow deploy".
argument-hint: "[project-path] [workflow-file] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- ci-cd
- automation
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow CI and Agent Automation

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Webflow CLI non-interactive work must pass every required ID explicitly and should add `--no-input`; missing values fail instead of opening a usable prompt.
- Current `apps` management commands are on the CLI `next` channel. CI must pin an exact pre-release version rather than installing the moving tag.
- `--json` changes successful output, while errors remain human-readable stderr; gate primarily on exit status.
- Destructive app commands require `--yes` in non-interactive mode, and supported write-management commands provide `--dry-run` for previews.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Inventory existing workflows, branch protections, environment approvals, package locks, `webflow.json`, and the intended Webflow surface.
2. Pin Node and the exact SDK or CLI version. Pass app, environment, site, workspace, mount, and deployment mode explicitly.
3. Separate pull-request checks from protected-environment mutations. PR jobs should typecheck, test fixtures, and run read-only probes only.
4. For management writes, run the documented dry-run, archive the plan, and bind execution to an approved environment.
5. For Cloud deploys, wait for the deployment terminal status and run a route-specific smoke test before downstream notification.
6. Test missing secrets, wrong IDs, 429s, failed deployments, and rollback selection; preserve receipts without secret values.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Missing required ID | Fail the job and name the approved secret or manifest key; never select an arbitrary resource. |
| Moving CLI changed | Restore the pinned version and assess release notes before updating. |
| Deployment not terminal | Use the documented wait operation and timeout; do not report success from enqueue alone. |

## Examples

A protected production workflow pins the exact CLI `next` build, passes site/app/environment IDs from environment secrets, runs read-only tests first, deploys only after approval, waits for success, and smoke-tests the mount.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
