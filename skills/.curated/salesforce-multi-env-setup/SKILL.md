---
name: salesforce-multi-env-setup
description: 'Build Salesforce development, scratch-org, sandbox, staging, and production environments with explicit promotion and drift controls. Use when designing org topology. Trigger with "set up Salesforce environments".'
argument-hint: "[project] [org-topology]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, environments, scratch-org, sandbox]
model: inherit
effort: high
compatibility: Designed for Claude Code; org creation, refresh, feature enablement, data seeding, and promotion require Dev Hub and Salesforce administrator approval
---
# Salesforce Multi-Environment and Org Topology

## Overview

Map each environment to a purpose, fidelity level, data policy, authorization boundary, lifecycle, and promotion contract.

## Prerequisites

- Business release model, Salesforce DX project, package strategy, org inventory, and environment owners
- Dev Hub, scratch-org, sandbox, staging, and production capabilities actually available to the customer
- Data seeding, masking, refresh, drift, namespace, dependency, promotion, rollback, and support requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Scratch orgs are disposable source-driven environments configured from project definitions; sandboxes provide different production fidelity and lifecycle characteristics. Available types, features, refreshes, data, and limits depend on the customer org.

## Authentication

Give each environment separate aliases, apps or policies, principals, permissions, and secret references. Never copy production tokens or unmasked production data into development or CI.

## Instructions

1. Inventory every org and environment with purpose, edition, features, packages, namespace, data class, owner, lifecycle, and authority.
2. Choose scratch org, developer sandbox, partial or full sandbox, or other approved environment from fidelity and data requirements.
3. Define source, metadata, package, settings, seed, masking, and post-refresh automation contracts.
4. Create environment-specific app, principal, permission, limit, event, endpoint, and secret-reference matrices.
5. Automate deterministic creation or refresh where supported, then verify org identity before any deployment or data load.
6. Promote immutable source and artifacts through validation gates; never promote mutable org state as the source of truth.
7. Detect configuration and metadata drift, reconcile approved exceptions, test rollback, and retire environments and credentials on schedule.

## Approval Boundaries

Do not create, refresh, clone, seed, mask, deploy, or retire an org without Dev Hub, admin, security, privacy, data, and release approval.

## Output

Return the org topology, fidelity and data matrix, lifecycle, configuration contract, authorization map, promotion gates, drift report, and retirement owners.

## Error Handling

| Condition | Response |
|---|---|
| Environment lacks a production feature | Move the test to an approved higher-fidelity org and document residual risk. |
| Production data appears in an unauthorized org | Stop access, invoke the data incident process, and prove deletion or containment. |
| Org alias resolves to an unexpected identity | Block all deployment and mutation until binding is corrected. |

## Example

A redacted completion receipt might look like this:

```text
project=core-crm; dev=scratch; integration=developer-sandbox; uat=partial; prod=production; drift=0; secrets=separate
```

## Resources

- [Salesforce DX development model](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_develop.htm)
- [Salesforce sandbox environments](https://help.salesforce.com/s/articleView?id=sf.data_sandbox_environments.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
