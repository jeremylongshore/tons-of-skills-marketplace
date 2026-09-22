---
name: vastai-local-dev-loop
description: >-
  Build a fast local development loop that promotes a CPU-tested change to one disposable Vast.ai GPU canary and always tears it down. Use when iterating on images, startup scripts, or training code. Trigger with: "test locally then on Vast.ai", "build a GPU canary loop", "shorten Vast.ai iteration".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[project-image-and-gpu-canary-policy]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - development
  - canary
  - containers
compatibility: 'Requires local container tooling, the Vast.ai CLI, a registry, a scoped API key, and a disposable GPU budget.'
---

# Vast.ai Local-to-GPU Canary Loop

## Overview

Keep slow marketplace operations out of the inner loop. Validate code and the container locally, publish an immutable image, then use a single policy-constrained GPU rental only for the behavior that cannot be proven without CUDA.

## Prerequisites

- Local unit and CPU-mode test commands with expected outputs
- Immutable image registry and a reproducible startup contract
- Canary GPU, price, reliability, timeout, and cleanup policy

## Instructions

### Step 1: Define the local contract

Use Read and Grep to identify entrypoints, required files, ports, and environment names. Write an explicit smoke command that works without cloud credentials.

### Step 2: Run local gates

Execute unit tests, build the image, start it in CPU mode where supported, and validate its health or process exit contract.

### Step 3: Publish immutable bytes

Push a digest or commit-addressed image. Reject mutable `latest` as canary evidence because the remote host may pull different bytes.

### Step 4: Rent the smallest canary

Search verified offers within the budget, create one instance with the immutable image, and record the contract ID before polling.

### Step 5: Compare GPU behavior

Run the same smoke assertion plus a CUDA-specific check. Capture structured output and the image digest, not interactive screenshots.

### Step 6: Tear down on every path

Copy only the required evidence, destroy the instance, and confirm removal even when the canary fails.

## Authentication

Inject the scoped Vast.ai key only into the local control process. Put workload secrets in an approved runtime secret mechanism and never bake them into the image or startup script.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Local test/build receipt and immutable image identity
- GPU canary offer, instance, state, and assertion evidence
- Confirmed teardown plus a classified local/remote delta

Return commit, image digest, offer and instance IDs, local/GPU outcomes, elapsed time, estimated cost, and cleanup status.

## Examples

A model-server change passes CPU request-shape tests, is pushed by digest, then runs one CUDA inference on a verified low-cost GPU before the disposable contract is destroyed.

## Error Handling

| Failure | Response |
| --- | --- |
| Local smoke fails | Do not rent a GPU; fix the deterministic local failure first. |
| Remote bytes differ | Destroy the canary and republish an immutable digest. |
| GPU assertion fails only remotely | Collect driver, CUDA, image, and command evidence before teardown. |
| Teardown is uncertain | Treat the instance as actively billable and escalate with its ID. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Docker environment](https://docs.vast.ai/guides/instances/docker-environment)
- [Create instances with the API](https://docs.vast.ai/api-reference/creating-instances-with-api)
- [Official Vast.ai CLI](https://github.com/vast-ai/vast-cli)
