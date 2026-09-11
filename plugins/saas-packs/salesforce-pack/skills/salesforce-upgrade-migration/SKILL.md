---
name: salesforce-upgrade-migration
description: 'Migrate Salesforce API, seasonal release, CLI, client-library, metadata, and integration contracts under compatibility and rollback controls. Use when planning platform upgrades. Trigger with "plan a Salesforce upgrade".'
argument-hint: "[repository] [target-release]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, upgrade, api-lifecycle, compatibility]
model: inherit
effort: high
compatibility: Designed for Claude Code; API version, dependency, metadata, and production changes require code and Salesforce platform owner approval
---
# Salesforce API and Toolchain Upgrade Control

## Overview

Replace fixed-version guesswork with a complete inventory, compatibility matrix, staged validation, explicit ownership, and reversible consumer migration.

## Prerequisites

- Repository and org inventory with API versions, libraries, CLI, metadata, events, packages, and consumers
- Current Salesforce API EOL policy, seasonal release notes, dependency releases, and customer support constraints
- Test environments, representative fixtures, compatibility owner, migration window, and rollback point

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce supports REST API versions for a documented lifecycle and retires older versions after notice. As of this review, versions 21.0 through 30.0 are unavailable, while the current support table must be re-fetched before every migration.

## Authentication

Use existing approved app and principal contracts for compatibility tests. Do not add a password fallback, copy production tokens into test, or broaden access to compensate for an upgrade defect.

## Instructions

1. Inventory every explicit and library-default API version, CLI and library version, endpoint, schema snapshot, event client, and metadata consumer.
2. Re-fetch the API EOL table, release notes, client-library releases, CLI contract, and org upgrade schedule.
3. Classify each dependency as supported, deprecated, retired, preview, beta, or customer-specific and name an owner.
4. Build fixtures for response, error, pagination, metadata, event schema, limits, and partial-failure compatibility.
5. Upgrade one boundary at a time in a branch and validate static, unit, contract, sandbox, and deployment checks.
6. Canary representative reads and approved non-production writes, then migrate consumers in reversible cohorts.
7. Reconcile results, remove old versions only after all consumers and rollback windows close, and schedule the next review.

## Approval Boundaries

Do not change API versions, dependencies, org settings, metadata, event consumers, or production traffic without code, platform, security, and business-owner approval.

## Output

Return the version inventory, authority evidence, compatibility matrix, changed contracts, test results, cohort plan, rollback point, and retirement date.

## Error Handling

| Condition | Response |
|---|---|
| Requested API version is retired | Stop requests and migrate through a supported version after contract testing; do not retry the retired URI. |
| Library default differs from configured version | Pin and test the effective version at the raw request boundary. |
| Seasonal release changes org behavior | Hold rollout, reproduce in the preview or sandbox path, and update the compatibility decision. |

## Example

A redacted completion receipt might look like this:

```text
apis=14; retired=2; target=discovered-supported; fixtures=12; sandbox=pass; cohorts=3; rollback=tagged
```

## Resources

- [REST API end-of-life policy](https://developer.salesforce.com/docs/platform/api-rest/guide/api-rest-eol.html)
- [Salesforce release notes](https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
