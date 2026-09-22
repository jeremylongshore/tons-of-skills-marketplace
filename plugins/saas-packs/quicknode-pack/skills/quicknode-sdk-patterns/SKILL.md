---
name: quicknode-sdk-patterns
description: 'Adopt the current unified QuickNode SDK with explicit product clients, timeouts, environment configuration, and platform checks. Use when coordinating Admin API, RPC, Streams, Webhooks, KV Store, or SQL Explorer from one service. Trigger with: "use the QuickNode SDK", "build a QuickNode client", "standardize QuickNode API access".'
allowed-tools: Read, Grep, Write, Edit, Bash(npm:*)
version: 2.0.0
argument-hint: '[language-and-product-clients]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - sdk
  - typescript
  - architecture
compatibility: 'Unified SDK supports documented native targets; Node.js package supports TypeScript, CommonJS, ES modules, and Bun'
---

# QuickNode Unified SDK Pattern

## Overview

Use one configured `QuicknodeSdk` instance and its named product clients. Do not confuse this control-plane SDK with a chain-specific ethers or viem provider, and do not retain old `Core`-only examples as the architecture for new multi-product services.

## Prerequisites

- Required product clients and account role
- A secret reference for `QN_SDK__API_KEY`
- A deployment target supported by the SDK native binaries

## Instructions

### Step 1: Audit existing clients

Use Read and Grep to find `@quicknode/sdk`, `Core`, direct `api.quicknode.com` calls, timeouts, retries, and duplicate API-key configuration. Classify chain RPC providers separately from QuickNode product clients.

### Step 2: Confirm platform support

Check the current SDK platform matrix before installing. Browser and unsupported native targets require a server-side boundary or direct documented APIs; do not assume a package that installs on one developer machine will load in every runtime.

### Step 3: Install deliberately

Use Bash(npm:*) to add a reviewed, pinned `@quicknode/sdk` version and capture the lockfile change. Do not use an unbounded latest version in production automation.

### Step 4: Build one client boundary

Use Write or Edit to construct `QuicknodeSdk.fromEnv()` once, inject it into application modules, and set a finite HTTP timeout. Keep base URL overrides limited to local tests or approved staging proxies.

```typescript
import { QuicknodeSdk } from '@quicknode/sdk';

export const quicknode = QuicknodeSdk.fromEnv();
```

### Step 5: Select explicit product clients

Route account resources through `admin`, Tooling Access RPC through `rpc`, data pipelines through `streams`, template subscriptions through `webhooks`, cursor state through `kvstore`, and indexed queries through `sql`. Keep chain-specific endpoint RPC behind its own adapter.

### Step 6: Test the boundary

Mock the SDK at the adapter edge. Add one authorized read-only integration test in a protected environment, validate typed error handling, and reject logs containing API keys or full endpoint URLs.

## Tool Discipline

Use Read and Grep for migration discovery, Bash(npm:*) only for package operations, and Write/Edit for the adapter and tests. Never execute destructive Admin, Stream, or Webhook methods without an explicit operator checkpoint.

## Output

- Product-client ownership map
- One reusable configured SDK boundary
- Platform and version compatibility receipt
- Unit and protected integration tests

## Examples

A release auditor uses `quicknode.admin` for endpoint inventory and `quicknode.streams` for paused-stream checks. Application chain reads remain in a separate RPC adapter with a distinct endpoint token.

## Error Handling

| Failure | Response |
| --- | --- |
| Native module fails to load | Recheck the published platform matrix and deployment target |
| SDK returns 401 | Verify `QN_SDK__API_KEY` and account role |
| Wrong product base URL | Remove accidental production override and retest |
| Old `Core` API conflicts | Isolate legacy chain calls and migrate behind an adapter |

## Resources

- [SDK evidence and source notes](references/official-docs.md)
- [Unified SDK](https://www.quicknode.com/docs/sdk)
- [SDK quickstart](https://www.quicknode.com/docs/sdk/quick-start)
