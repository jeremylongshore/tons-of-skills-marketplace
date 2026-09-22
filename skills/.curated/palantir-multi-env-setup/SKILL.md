---
name: palantir-multi-env-setup
description: >-
  Configure development, test, and production Foundry environments using spaces, DevOps products, Marketplace installations, and explicit parameters. Use when release-managing workflows across environments. Trigger with "Foundry environments" or "Palantir dev test prod".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[devops-store-and-product]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, environments, devops]
---
# Palantir DevOps Environment Separation

## Overview

Represent long-lived environments with Foundry spaces and promote versioned products through DevOps and Marketplace. Use Global Branching for isolated changes within an environment, not as a substitute for every long-lived environment boundary.

## Prerequisites

- Identify the enrollment, DevOps store, source products, target spaces, owners, dependencies, security policies, external systems, and approval chain.
- Inventory environment-specific sources, sinks, URLs, OAuth clients, markings, organizations, schedules, and release windows.
- Read `references/official-docs.md` and inspect the current product dependency and parameter contracts.
- Establish the development source product and at least one non-production installation.

## Current Contract

- Spaces provide environment separation for development, test, and production workflows.
- DevOps products package resources and their dependencies; downstream products should resolve inputs from the corresponding target environment.
- Marketplace installations can use release channels, locks, maintenance windows, and parameter inputs.
- Supported Developer Console application parameters can be remapped during installation, but Ontology API-name behavior and source-code parameters need explicit review.

## Authentication

Give each environment an appropriately restricted OAuth application or mapped Developer Console application according to the supported product contract. Do not copy production client secrets into development or embed environment credentials in packaged source.

## Instructions

1. Define each environment as a space with owners, security policy, external integration boundary, approval workflow, and recovery objective.

2. Package the workflow into bounded DevOps products with explicit inputs, outputs, dependencies, and parameter contracts.

3. Install upstream products before downstream dependents in test, resolving every input from the matching environment.

4. Verify parameter remapping, OAuth/restrictions, Ontology references, markings, schedules, and external endpoints.

5. Promote an immutable product version through the approved release channel and test downgrade or prior-version rollback.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Space owners approve environment membership; product owners approve versions and dependencies; security/data owners approve environment-specific controls; production owners approve installation, channel, lock, and maintenance-window changes.

## Output

An environment matrix, product/dependency graph, parameter and secret map, installation order, release-channel policy, test results, promotion receipt, drift report, and rollback version.

## Error Handling

| Condition | Response |
|---|---|
| A dependency resolves across environments | Stop installation and bind it to the corresponding target-space product or resource. |
| A packaged application retains source parameters | Correct supported remapping or parameterization before promotion. |
| Security differs unintentionally | Block the release and reconcile roles, mandatory controls, restrictions, and external integrations. |
| Rollback dependencies are unavailable | Keep the current version locked and restore the dependency chain before proceeding. |

## Examples

### Example 1

Create Development, Test, and Production spaces, package an upstream data product and downstream application product, and verify same-environment dependency binding before promotion.

### Example 2

Install a Developer Console application through Marketplace, confirm Foundry URL and OAuth parameters map to test, verify Ontology API-name handling, then promote the same product version.

## Validation

- Every product dependency resolves inside the intended environment.
- Environment-specific credentials and external endpoints are isolated.
- Parameter remapping and Ontology identifiers are verified from the installed product.
- Release approvals, channels, locks, and maintenance windows match policy.
- A prior product version and its dependencies can be restored.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
