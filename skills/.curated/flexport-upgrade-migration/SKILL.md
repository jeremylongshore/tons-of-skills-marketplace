---
name: flexport-upgrade-migration
description: >-
  Upgrade a Flexport REST integration using account version settings and request overrides while tolerating compatible additions. Use when changing the Flexport-Version header, testing a new schema, or responding to added fields and event types. Trigger with: "upgrade Flexport API", "change Flexport version", "handle Flexport schema change".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[current-version-and-target-version]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - upgrade
  - versioning
compatibility: 'Requires access to current Flexport version documentation, account version context, contract tests, and a rollback owner.'
---

# Flexport Version-Tolerant Upgrade

## Overview

Flexport supports account-default version selection plus per-request `Flexport-Version` overrides. Backward-compatible additions can include attributes, resources, optional parameters, enum values, and event types, so readers and routers must be additive-tolerant.

## Prerequisites

- Current account default and every application override
- Endpoint/event inventory with sanitized fixtures
- Target-version diff, owner approvals, canary, and rollback

## Instructions

### Step 1: Discover effective versions

Record the account default and explicit header behavior for every client; do not assume a hardcoded v2 path determines the contract.

### Step 2: Classify changes

Separate breaking target-version differences from compatible additions that may appear without an account-version switch.

### Step 3: Harden readers

Ignore or preserve unknown optional fields, route unknown enum/event values safely, and fail only when a required invariant is absent.

### Step 4: Test with overrides

Exercise approved read-only calls using the target `Flexport-Version` header while production remains on its current default.

### Step 5: Canary one cohort

Deploy tolerant code first, switch a bounded read cohort, compare business outcomes, then enable mutations only after reconciliation passes.

### Step 6: Change default last

Coordinate account-default changes after all clients are ready, retain explicit rollback overrides, and verify events plus in-flight operations.

## Authentication

REST calls authenticate with a cached OAuth 2.0 client-credentials Bearer token using audience `https://api.flexport.com`, or an explicitly accepted broad API key. Use distinct credentials per workload and never log credentials or tokens. MCP calls use the authenticated connection to `https://mcp.flexport.com/mcp` and remain subject to each tool's documented account permissions.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Flexport-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

Return a machine-reviewable receipt in this shape; adapt the operation values, but never place credentials or provider payloads in it:

```yaml
surface: rest-v3
operation: shipment-read
decision: approved
outcome: verified
evidence:
  release_sha: recorded-out-of-band
  provider_reference: redacted
rollback_owner: logistics-platform
```

## Examples

A parser learns to preserve unknown shipment attributes and quarantine unknown event types. The team tests reads with `Flexport-Version: 3`, canaries them, then changes the account default only after every client passes.

## Error Handling

| Failure | Response |
| --- | --- |
| Effective version unknown | Stop and inspect account settings plus outbound headers. |
| Unknown additive enum crashes routing | Quarantine safely and make parsing tolerant. |
| Read results diverge | Pause migration and reconcile semantic, expansion, and pagination differences. |
| Rollback header untested | Do not change the account default. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Versioning](https://apidocs.flexport.com/v3/tag/Versioning/)
- [Flexport v3 API reference](https://apidocs.flexport.com/v3/)
- [Milestones](https://apidocs.flexport.com/v3/tag/Milestones/)
