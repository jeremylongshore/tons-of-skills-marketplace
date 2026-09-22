---
name: vastai-deploy-integration
description: >-
  Deploy an immutable service or batch worker to a Vast.ai instance with template, health, artifact, rollback, and cleanup controls. Use when shipping an instance-based workload rather than Serverless. Trigger with: "deploy to a Vast.ai instance", "release a Vast.ai template", "roll back a Vast.ai deployment".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[release-image-template-and-health-contract]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - deployment
  - templates
  - instances
compatibility: 'Requires an immutable image, Vast.ai template or creation manifest, scoped deployment key, health contract, and rollback artifact.'
---

# Immutable Vast.ai Instance Deployment

## Overview

Make the deployment reproducible outside the console. Bind release bytes to an immutable image and versioned template hash, launch a canary under policy, validate service and GPU health, then promote or destroy.

## Prerequisites

- Release commit, image digest, template hash, ports, environment names, and startup contract
- Offer policy, health checks, artifact/checkpoint destinations, and maximum rollout time
- Last-known-good image/template plus rollback and teardown owners

## Instructions

### Step 1: Freeze the deployment manifest

Record all non-secret template settings, image digest, on-start behavior, exposed ports, disk, label, and required GPU/host constraints.

### Step 2: Validate outside production

Build and scan the image, run local contract tests, and launch a disposable canary from the exact template hash.

### Step 3: Verify readiness

Bound state polling, resolve current endpoints, check process and GPU health, and execute a representative request or batch assertion.

### Step 4: Promote deliberately

Create or update the production instance only after canary acceptance. Persist resource IDs and externalize important data before traffic or work begins.

### Step 5: Observe the release

Track state, logs, request/job outcome, cost, disk, and checkpoint health through the acceptance window.

### Step 6: Roll back or close

On regression, route work to the last-known-good template or recreate from it; copy evidence and destroy rejected or superseded instances.

## Authentication

Give deployment automation only search, template, and instance permissions it needs. Keep registry, model, and storage secrets in approved runtime variables and out of template descriptions and logs.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Versioned deployment manifest and immutable identities
- Canary and production health/acceptance evidence
- Promotion, rollback, and superseded-resource cleanup receipt

Return release, image/template identities, offer and instance IDs, health result, acceptance window, decision, and cleanup status.

## Examples

A model API is launched from a pinned template hash and image digest, passes GPU and request canaries, then replaces the previous instance; the rejected candidate is destroyed and the old template remains recorded for rollback.

## Error Handling

| Failure | Response |
| --- | --- |
| Template resolves different bytes | Stop and pin a new immutable hash before provisioning. |
| Health passes but workload assertion fails | Reject the release and retain the last-known-good service. |
| Rollback data is only on local disk | Copy it externally before destructive recovery if the incident permits. |
| Superseded instance remains | Treat it as a cost leak and complete or escalate teardown. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Creating templates](https://docs.vast.ai/guides/templates/creating-templates)
- [Managing templates](https://docs.vast.ai/guides/templates/managing-templates)
- [Manage instances](https://docs.vast.ai/guides/instances/manage-instances)
