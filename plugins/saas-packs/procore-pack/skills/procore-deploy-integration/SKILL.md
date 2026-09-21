---
name: procore-deploy-integration
description: >-
  Promote a Procore app version through sandbox verification, permission-diff review, semantic versioning, release notes, production promotion, and post-deploy proof. Use when shipping a connector or embedded app change. Trigger with: "deploy a Procore integration", "promote a Procore app version", "release Procore manifest".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-version-and-release-scope]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - deployment
  - release
compatibility: 'Requires Procore Developer Portal app ownership, an installable app version, and authorized sandbox and production administrators.'
---

# Procore App Version Promotion

## Overview

Promote the Procore app contract and the integration deployment as one reviewed release. Permission changes, installation steps, OAuth credentials, endpoint compatibility, and customer communication must align with the same semantic version.

## Prerequisites

- Immutable integration release and matching Procore app version
- Permission and component diff, release notes, migration plan, and rollback owner
- Sandbox installation, test company, production approver, and observation window

## Instructions

### Step 1: Freeze the release

Record source release identifier, app manifest version, endpoint inventory, configuration schema, and generated artifacts. Refuse moving tags or unreviewed builds.

### Step 2: Review contract changes

Classify semantic version impact and inspect added permissions, components, callback URLs, post-install steps, and customer-facing behavior.

### Step 3: Verify in sandbox

Install the version using the correct environment key, exercise authentication, required reads, expected denials, mutations in disposable data, webhooks, and cleanup.

### Step 4: Approve promotion

Present evidence, permission diff, release notes, known limitations, support plan, and rollback. Require the authorized operator to promote the reviewed version.

### Step 5: Deploy and canary

Deploy the matching integration release to a bounded tenant set, verify token acquisition and read-only access, then enable controlled business processing.

### Step 6: Observe and settle

Monitor API activity, Integration Health, errors, rate budget, webhook deliveries, and backlog. Roll back the application release or integration according to the predeclared boundary.

## Authentication

Deployment verification uses OAuth 2.0 credentials for each environment and never copies sandbox tokens into production. Production credential issuance and rotation stay within the Developer Portal and approved secret store.

## Tool Discipline

Use Read and Grep to inspect release artifacts, manifests, diffs, and evidence. Use Write or Edit only for the approved release record, configuration, test, or receipt; the actual Procore promotion requires an authorized portal operator.

## Output

- Immutable release and app-version evidence
- Permission diff, sandbox proof, promotion approval, and canary results
- Observation, rollback, and customer-impact receipt

Return exact versions, approvers, test results, rollout scope, health signals, and final disposition.

## Examples

A manifest adds a new project-tool permission, so the release is classified accordingly and tested against both allowed and denied projects. The production canary does not begin until the portal version and deployed integration share the reviewed release.

## Error Handling

| Failure | Response |
| --- | --- |
| Manifest and deployment differ | Stop rollout and rebuild from the immutable reviewed release. |
| Permission diff is unexplained | Reject promotion until each new capability has an owner and test. |
| Sandbox proof fails | Repair and create a new reviewed version rather than editing evidence. |
| Canary health degrades | Halt expansion and execute the declared rollback boundary. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Promote a version to production](https://developers.procore.com/documentation/building-apps-promote-manifest)
- [App versioning and update notification](https://developers.procore.com/documentation/building-apps-versioning)
- [Integration Health](https://developers.procore.com/documentation/integration-health)
