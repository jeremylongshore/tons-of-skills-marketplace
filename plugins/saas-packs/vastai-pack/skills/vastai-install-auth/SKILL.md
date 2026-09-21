---
name: vastai-install-auth
description: >-
  Install the supported Vast.ai CLI and establish a least-privilege authentication boundary without leaking or persisting the wrong key. Use when bootstrapping a workstation, CI runner, or automation account. Trigger with: "install Vast.ai", "configure VAST_API_KEY", "create a scoped Vast.ai key".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workstation-or-ci-and-required-operations]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - authentication
  - cli
  - least-privilege
compatibility: 'Requires a Vast.ai account, an approved secret store, and Linux, macOS, WSL, or Python 3.9+.'
---

# Vast.ai CLI Authentication Boundary

## Overview

Install from the provider-supported channel, choose file-backed versus environment-backed authentication by runtime, and prove that the key can perform only the intended operations. The current CLI migrates legacy key files into the XDG configuration location.

## Prerequisites

- Named workload owner and classified workstation, CI, container, or service runtime
- Permission inventory covering search, instance, user, billing, machine, and team operations
- Approved secret store plus a rotation and revocation owner

## Instructions

### Step 1: Select the install channel

Use the managed installer on Linux, macOS, or WSL when an isolated runtime is desired. Use the `vastai` PyPI package for Windows or Python SDK work; record the installed version.

### Step 2: Place the credential

For an interactive workstation, let `vastai set api-key` write `~/.config/vastai/vast_api_key` or the corresponding XDG configuration path. For CI or containers, inject `VAST_API_KEY`; the environment value takes precedence and avoids a key file.

### Step 3: Create least privilege

Build a permission file containing only the categories and endpoint constraints the workload needs, then create a named scoped key. Do not use a full-access console key for shared automation.

### Step 4: Verify positive and negative paths

Run `vastai show user --raw`, one required operation, and one operation expected to be denied. Preserve only status, key ID, and permission evidence.

### Step 5: Plan rotation

Create and verify the replacement before deleting the old key. Revoke immediately if a key, command trace, or artifact may have exposed its value.

## Authentication

Every API request requires a key. Treat `VAST_API_KEY`, the XDG key file, and the legacy `~/.vast_api_key` location as secrets; never print key values or copy them into receipts.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Install channel and exact CLI/SDK version
- Scoped permission manifest with positive and expected-denial results
- Redacted rotation, revocation, and rollback receipt

Return runtime, install channel, key ID, granted categories, verification outcomes, and credential owner.

## Examples

A CI deployer receives `misc`, `user_read`, `instance_read`, and `instance_write` without billing or team access; its key is injected as a masked environment secret and deleted after replacement validation.

## Error Handling

| Failure | Response |
| --- | --- |
| `vastai show user` returns 401 | Stop retries; verify key source, precedence, revocation state, and account context. |
| Required command returns 403 | Add only the missing documented category or endpoint constraint, then rerun the negative test. |
| CLI reads an unexpected legacy key | Inspect XDG precedence and migrate or revoke the stale credential. |
| Credential may be exposed | Revoke it, scrub artifacts, rotate dependent jobs, and document the incident. |

## Resources

- [First-party source notes](references/official-docs.md)
- [CLI authentication](https://docs.vast.ai/cli/authentication)
- [CLI permissions](https://docs.vast.ai/cli/permissions)
- [Official Vast.ai CLI](https://github.com/vast-ai/vast-cli)
