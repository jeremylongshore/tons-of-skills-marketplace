---
name: vastai-upgrade-migration
description: >-
  Upgrade or roll back the Vast.ai CLI, Python SDK import surface, and workload template without speculative API-version changes. Use when changing a client pin, SDK import, or production template. Trigger with: "upgrade Vast.ai CLI", "migrate from vastai_sdk", "roll a Vast.ai template update".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[current-version-target-version-and-workloads]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - upgrade
  - compatibility
  - rollback
compatibility: 'Requires current and target client versions, a test environment, immutable templates, and retained rollback artifacts.'
---

# Reversible Vast.ai Client and Template Upgrade

## Overview

Treat the provider client and workload template as separate compatibility boundaries. Pin and test the managed CLI or PyPI package, preserve the `vastai_sdk` compatibility shim during migration, and canary template changes before a rolling update.

## Prerequisites

- Current CLI/SDK version, install channel, import usage, commands, templates, and dependent automation
- Target version and release evidence plus contract tests for critical commands and response adapters
- Rollback client version, prior template hash, and an acceptance deadline

## Instructions

### Step 1: Freeze the current contract

Record versions, install location, key precedence, imports, command help, structured outputs, and immutable template/model identities.

### Step 2: Upgrade in isolation

For the managed CLI, use its version-aware update mechanism and retain the prior version. For Python, pin the target `vastai` package in a disposable environment.

### Step 3: Test client compatibility

Run auth, offer search, instance read, response normalization, and expected-denial tests without creating paid resources unless the plan requires a canary.

### Step 4: Migrate SDK imports deliberately

Move from `vastai_sdk` to `vastai` while the documented compatibility shim remains; test high-level and sync/async client boundaries actually used.

### Step 5: Canary workload changes

Create a separate endpoint or disposable instance from the target template, prove output and recovery, then trigger a controlled rolling update if Serverless.

### Step 6: Accept or revert

Compare contract and SLO evidence. Restore the prior client pin or template reference on failure and verify the rollback path.

## Authentication

Confirm the upgraded client still reads the intended XDG or environment credential and preserves least privilege. Never test upgrades with an unscoped production key by default.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Before/after client and template contract inventory
- Compatibility, canary, SLO, and expected-denial results
- Acceptance or rollback receipt with retained prior versions

Return install channel, old/new versions, import boundary, old/new template hashes, tests, decision, and rollback verification.

## Examples

A service moves from the `vastai_sdk` shim to `vastai` in staging, pins the package, validates its response adapter, canaries a new template, then performs a monitored Serverless rolling update with the prior hash retained.

## Error Handling

| Failure | Response |
| --- | --- |
| Structured output changes | Fail at the adapter contract and keep the previous pin. |
| Credential source changes | Stop and restore the intended key precedence before any mutation. |
| Canary output or recovery regresses | Reject the template and retain production on the old hash. |
| Rollback artifact is unavailable | Issue NO-GO until the prior client and template are recoverable. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Official CLI README](https://github.com/vast-ai/vast-cli)
- [Official SDK skill](https://github.com/vast-ai/vast-cli/blob/master/vastai_sdk/SKILL.md)
- [Zero-downtime worker update](https://docs.vast.ai/guides/serverless/zero-downtime-worker-update)
