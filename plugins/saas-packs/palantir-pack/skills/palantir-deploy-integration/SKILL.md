---
name: palantir-deploy-integration
description: >-
  Choose and execute a Foundry-native deployment path for OSDK applications, products, or container workloads. Use when publishing a Developer Console app, DevOps product, or Compute Module. Trigger with "deploy to Foundry" or "Palantir Compute Module".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[application-product-or-module]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, deployment, compute-modules]
---
# Palantir Application and Compute Deployment

## Overview

Select the deployment primitive from the workload instead of defaulting to an external cloud runtime. Use Developer Console and Marketplace for OSDK applications, DevOps products for release-managed resources, or Compute Modules for compatible container workloads inside Foundry.

## Prerequisites

- Identify the workload, owners, target environment, runtime needs, data access, availability objective, and rollback requirement.
- Determine whether it is an OSDK website/application, a packaged Foundry product, a container-backed function, or a container-backed pipeline.
- Read `references/official-docs.md` and the target enrollment's in-platform Compute Module or DevOps instructions.
- Prepare a versioned artifact and non-production target.

## Current Contract

- Compute Modules run interactive container images in Foundry and support container-backed functions, pipelines, and custom integrations.
- Compute Module images must meet documented platform, user, tag/digest, and port requirements.
- Developer Console applications can be packaged through Marketplace with OAuth client metadata and resource restrictions.
- DevOps/Marketplace installation can remap supported environment parameters, while Ontology API-name handling still requires deliberate design.

## Authentication

Use Developer Console OAuth for application access and Foundry's approved artifact/deployment authentication for publishing. Keep client secrets and bearer tokens in approved secret surfaces; do not bake them into images, code repositories, product parameters, or website assets.

## Instructions

1. Classify the workload and select Developer Console/Marketplace, a DevOps product, or a Compute Module with a written rationale.

2. Inventory dependencies, OAuth grants, resource restrictions, parameters, markings, artifact repository, and target-space ownership.

3. Build and test a versioned artifact; for containers, verify non-root numeric user, `linux/amd64`, allowed ports, and a non-`latest` tag or digest.

4. Install or configure in a non-production environment and run functional, security, scaling, and failure-path checks.

5. Promote the exact artifact through the approved release path, verify health and logs, and retain the prior version for rollback.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Application, platform, security, and data owners approve the deployment and its access. Production installation, module start/scale changes, OAuth changes, and release-channel changes are live mutations requiring explicit approval.

## Output

A deployment decision, dependency and parameter map, immutable artifact identity, access model, environment test results, promotion receipt, health evidence, and rollback target.

## Error Handling

| Condition | Response |
|---|---|
| The container violates image requirements | Reject the artifact and rebuild it; do not request a platform exception as the first response. |
| Parameters resolve to source-environment values | Stop installation and correct supported remapping or explicit environment parameters. |
| The module starts but cannot access data | Check OAuth/resource restrictions and Foundry permissions without embedding new credentials. |
| Post-promotion health degrades | Roll back to the recorded artifact or product version and preserve logs and metrics. |

## Examples

### Example 1

Package an OSDK website and Developer Console application as a DevOps product, install it in a test space, verify remapped OAuth/Foundry parameters, then promote the same product version.

### Example 2

Deploy a container-backed function as a Compute Module using a non-root `linux/amd64` image pinned by version, query it in the test panel, inspect logs, and validate scale behavior.

## Validation

- The chosen primitive matches the workload and current Foundry support.
- The deployed artifact identity exactly matches the reviewed version.
- Secrets are absent from code, image layers, and product parameters.
- Environment-specific URLs, OAuth values, Ontology references, markings, and dependencies resolve correctly.
- The rollback restores the prior healthy version within the stated objective.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
