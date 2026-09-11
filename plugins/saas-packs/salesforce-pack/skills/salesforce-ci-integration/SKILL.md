---
name: salesforce-ci-integration
description: 'Build fork-safe Salesforce CI with secretless static and fixture gates, protected non-production validation, and separately approved production promotion. Use when automating delivery. Trigger with "add Salesforce CI".'
argument-hint: "[repository] [project-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, ci, github-actions, deployment-validation]
model: inherit
effort: high
compatibility: Designed for Claude Code; live org authentication and deployment require protected runners, environments, and customer authorization
---
# Fork-Safe Salesforce Continuous Integration

## Overview

Separate deterministic untrusted-code checks from credentialed org validation so pull requests cannot access Salesforce secrets or mutate a customer org.

## Prerequisites

- Repository, Salesforce DX project, package layout, branch policy, and immutable dependency lock
- Synthetic metadata and API fixtures plus an authorized validation org
- CI, Salesforce admin, security, release, and code owners with environment protection rules

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce CLI can validate and deploy source against authorized orgs, but exact commands, test levels, authentication, and metadata behavior vary with the pinned CLI and project. Fork pull requests must be treated as untrusted.

## Authentication

Keep org authorization, certificates, secrets, and aliases out of fork-origin jobs, logs, caches, and artifacts. Resolve protected credentials only after trusted code, environment approval, and exact-head verification.

## Instructions

1. Pin runtime, package manager, Salesforce CLI, plugins, lockfiles, action SHAs, and generated-artifact checks.
2. Create a secretless lane for formatting, linting, static analysis, unit tests, schema tests, fixture contracts, and source validation.
3. Model auth expiry, permission denial, API-version drift, metadata conflict, partial deployment, limits, and rollback in fixtures.
4. Restrict credentialed jobs to protected branches or environments with no fork secrets, minimal permissions, concurrency, and timeouts.
5. Against an approved non-production org, verify identity, validate the bounded deployment, run required tests, and capture IDs.
6. Require human approval and immutable artifact promotion before any production validation or deployment job.
7. Reconcile deployed metadata and application health, publish a redacted receipt, and revoke temporary credentials.

## Approval Boundaries

Do not expose secrets to pull requests, authenticate unreviewed code, auto-deploy to production, or lower required test levels or branch protection.

## Output

Return the trust-boundary diagram, pinned CI configuration, secretless and protected gate results, org identity proof, validation IDs, promotion approval, and rollback evidence.

## Error Handling

| Condition | Response |
|---|---|
| Fork job requests a Salesforce secret | Fail closed and keep the live-org lane skipped. |
| Validation org differs from the expected org | Stop immediately, revoke the session, and correct environment binding. |
| Protected validation is flaky | Fix determinism or quarantine the lane explicitly; do not silently make it optional. |

## Example

A redacted completion receipt might look like this:

```text
head=immutable; fork-lane=secretless-pass; protected-org=matched; validate=pass; tests=pass; production=manual
```

## Resources

- [Salesforce DX development model](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_develop.htm)
- [REST OAuth authorization](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
