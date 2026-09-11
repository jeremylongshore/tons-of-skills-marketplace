---
name: salesforce-local-dev-loop
description: 'Build a repeatable Salesforce DX development loop using source format, synthetic tests, and an authorized scratch org or sandbox. Use when changing metadata or integration code. Trigger with "build a Salesforce dev loop".'
argument-hint: "[project-path] [org-alias]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, salesforce-dx, scratch-org, testing]
model: inherit
effort: high
compatibility: Designed for Claude Code; org creation, metadata deployment, and test-data loading require Dev Hub and administrator authorization
---
# Salesforce DX Local Development Loop

## Overview

Create a source-driven loop that separates static and synthetic checks from explicitly authorized org validation and leaves no unmanaged test data.

## Prerequisites

- A Salesforce DX project or an approved migration plan to source format
- An authorized Dev Hub and scratch-org definition, or a dedicated development sandbox
- Synthetic fixtures, test owner, cleanup policy, and current Salesforce CLI contract

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce DX supports source-driven development and scratch orgs configured through project definitions; org availability, features, limits, duration, namespaces, and sandbox alternatives depend on the customer environment.

## Authentication

Use a named CLI alias backed by the approved OAuth path. Never commit authorization files, access tokens, private keys, usernames, org IDs, or generated user passwords.

## Instructions

1. Inspect project configuration, package directories, metadata ownership, API versions, hooks, and current CLI pin.
2. Choose a scratch org or development sandbox based on feature fidelity, data need, namespace, and lifecycle constraints.
3. Create synthetic fixtures and local contract tests that require no live org or secret.
4. Run formatting, static analysis, unit tests, schema checks, and metadata dependency checks locally.
5. With approval, create or authenticate the development org and deploy only the bounded source set.
6. Run Apex, Flow, Lightning, and integration tests applicable to the change; capture aggregate results and IDs only.
7. Delete synthetic data, close or expire temporary orgs, revoke temporary access, and record reproducible commands.

## Approval Boundaries

Do not create orgs, enable features, deploy metadata, load data, or change remote configuration without Dev Hub, admin, and component-owner approval.

## Output

Return the environment decision, pinned toolchain, source and fixture map, local and org test results, cleanup receipt, and remaining fidelity gaps.

## Error Handling

| Condition | Response |
|---|---|
| Scratch-org feature does not match production | Use an approved sandbox or revise the definition; do not weaken production metadata. |
| Deployment reports missing dependencies | Add the dependency explicitly or reduce the source set before retrying. |
| Test data cannot be proven synthetic | Stop and replace it before local export or CI use. |

## Example

A redacted completion receipt might look like this:

```text
project=sfdx; target=scratch-org; fixtures=synthetic; static=pass; deploy=validated; apex=pass; cleanup=complete
```

## Resources

- [Salesforce DX development model](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_develop.htm)
- [Scratch org definition file](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_scratch_orgs_def_file.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
