---
name: vastai-ci-integration
description: >-
  Run a credential-safe disposable Vast.ai GPU CI job with a scoped key, immutable image, cost ceiling, terminal-state deadline, and guaranteed destruction. Use when GPU-only acceptance must run in CI. Trigger with: "run GPU tests in CI", "add Vast.ai to GitHub Actions", "make Vast.ai CI clean up".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[ci-provider-test-command-and-gpu-policy]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - ci
  - gpu-testing
  - cleanup
compatibility: 'Requires a CI secret store, current Vast.ai CLI, immutable test image, registered SSH key, and a disposable test budget.'
---

# Disposable Vast.ai GPU CI

## Overview

Use ordinary CPU CI for deterministic tests and reserve Vast.ai for a small GPU acceptance slice. The cloud step must publish its resource ID immediately and make cleanup independent of test success.

## Prerequisites

- GPU-only acceptance command and expected machine-readable result
- Scoped CI key, dedicated SSH public key, immutable image digest, and masked logs
- Offer constraints, maximum price, readiness deadline, job timeout, and cleanup escalation

## Instructions

### Step 1: Gate before provisioning

Run lint, unit, CPU, and image tests first. Skip the GPU job when those fail or when the change does not require hardware acceptance.

### Step 2: Create a scoped run manifest

Record commit, image digest, test command, GPU policy, maximum spend, external artifact target, and unique CI run label.

### Step 3: Provision one resource

Search compliant verified offers and create exactly one instance. Write the returned instance ID to CI state before any polling or test step.

### Step 4: Wait and test

Use structured status, bounded polling, terminal failure branches, and a non-interactive GPU test. Keep command output and logs free of secrets.

### Step 5: Publish evidence

Copy the test result, relevant redacted logs, image identity, timings, and cost estimate to durable CI artifacts.

### Step 6: Destroy unconditionally

Run destruction in the CI finalizer for success, failure, cancellation, and timeout; confirm removal and alert on cleanup failure.

## Authentication

Inject `VAST_API_KEY` from the CI secret store into the control step only. Use a scoped key without billing-write or team-write and prevent forked or untrusted PRs from receiving it.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- CI run and immutable workload manifest
- Provisioning, state, GPU assertion, timing, and cost artifacts
- Unconditional cleanup result and escalation receipt

Return CI run, commit, image digest, offer/instance IDs, test result, elapsed time, estimate, and confirmed destruction.

## Examples

A protected-branch workflow runs CPU tests first, rents one verified GPU under a fixed ceiling, executes a five-minute CUDA acceptance test, uploads JSON evidence, and destroys the instance in `always()` cleanup.

## Error Handling

| Failure | Response |
| --- | --- |
| Secret-bearing event is untrusted | Skip the GPU job; never expose repository secrets to fork code. |
| Create result lacks an instance ID | Reconcile by run label before retrying to prevent duplicate rentals. |
| Job is cancelled | The independent cleanup job destroys the persisted instance ID. |
| Destroy cannot be confirmed | Fail the workflow and alert the billing owner with the resource ID. |

## Resources

- [First-party source notes](references/official-docs.md)
- [CLI authentication for CI](https://docs.vast.ai/cli/authentication#environment-variable-cicd)
- [CLI hello world](https://docs.vast.ai/cli/hello-world)
- [Official CLI skill](https://github.com/vast-ai/vast-cli/blob/master/vastai/SKILL.md)
