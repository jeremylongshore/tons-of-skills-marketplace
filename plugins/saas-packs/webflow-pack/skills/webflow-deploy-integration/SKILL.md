---
name: webflow-deploy-integration
description: >-
  Plan and execute a Webflow Cloud deployment with explicit app identity, mount, environment, verification, and rollback. Use when shipping a Cloud app or repairing its deployment lane. Trigger with "deploy Webflow Cloud", "Webflow app deploy", or "rollback Webflow deployment".
argument-hint: "[project-path] [site-attached|project-app] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- deployment
- cloud
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Cloud Deployment

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Webflow Cloud supports site-attached apps and standalone project apps; the first deployment inputs differ.
- Current app-management commands use the CLI `apps` namespace on the `next` channel, while stable CLI retains documented Cloud commands and deprecated aliases.
- Webflow recommends GitHub-linked deployment for the simple continuous-deployment path; linking the repository is a one-time dashboard operation.
- A deployment enqueue is not success. Wait for a terminal deployment status and verify the actual mounted route.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Inspect framework, build output, `webflow.json`, app/environment IDs, mount path, domain, and existing deployment history.
2. Choose site-attached or project-app mode and record all IDs. Discover IDs read-only; never infer them from names alone.
3. Pin the CLI channel/version and validate Node compatibility. Build and test locally using the project's own scripts.
4. Prepare the exact deploy command with explicit `--no-input`, target IDs, mount, environment, and any documented mount-path option.
5. Show rollback as a specific prior successful deployment or prior artifact, then obtain production approval.
6. Deploy, wait for terminal success, check domains and the mounted route, and retain the deployment ID and verification receipt.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Ambiguous app/environment | Stop and require an explicit ID or verified manifest value. |
| Build succeeds, deploy fails | Collect build/runtime logs for that deployment ID and leave the previous deployment active. |
| Smoke test fails | Trigger the approved rollback or redeploy the named prior successful deployment. |

## Examples

For a site-attached Astro app, verify the site and app IDs, pin the CLI version, build locally, approve `/app` on production, deploy non-interactively, wait for success, and test the exact public route.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
