---
name: quicknode-local-dev-loop
description: 'Create a deterministic local QuickNode development loop with transport fixtures, base-URL injection, redacted recordings, and an opt-in read-only sandbox check. Use when developing SDK, RPC, Stream, or Webhook integrations without consuming live credits on every test. Trigger with: "develop against QuickNode locally", "mock QuickNode", "test a QuickNode adapter offline".'
allowed-tools: Read, Grep, Write, Edit, Bash(npm:*)
version: 2.0.0
argument-hint: '[adapter-and-test-command]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - local-development
  - testing
  - fixtures
compatibility: 'SDK base URL overrides are for local, staging, and approved sandbox boundaries'
---

# QuickNode Deterministic Local Loop

## Overview

Develop against an injectable transport by default. Local tests should model QuickNode protocol contracts without a live token, then use one explicit sandbox read to catch integration drift.

## Prerequisites

- Existing QuickNode or JSON-RPC adapter
- Repository test runner and fixture convention
- Optional non-production, read-only credential in a local secret manager

## Instructions

### Step 1: Locate the boundary

Use Read and Grep to find direct endpoint calls, SDK constructors, global environment reads, retries, timers, and response parsing. Choose one adapter seam for injection.

### Step 2: Define fixture contracts

Use Write or Edit to add success, HTTP error, JSON-RPC error, timeout, rate limit, malformed response, and pagination fixtures. Preserve request IDs and nested causes.

### Step 3: Inject transport and time

Pass the transport, base URL, clock, and sleeper into the adapter. Use documented SDK base URL overrides only for a local stub or approved staging endpoint.

### Step 4: Sanitize recordings

If a real response becomes a fixture, retain only necessary fields and replace endpoint URLs, tokens, API keys, addresses, and business payloads. Add a leak assertion to the fixture test.

### Step 5: Run fast tests

Use Bash(npm:*) to run the repository's pinned unit and contract commands. Keep network disabled in the default lane and make accidental outbound access fail.

### Step 6: Opt into one live read

Gate a sandbox read behind an explicit variable or command. Verify chain identity and shape, cap timeout and calls, and skip cleanly when the opt-in credential is absent locally.

## Tool Discipline

Use Read/Grep for adapter discovery, Write/Edit for injection and fixtures, and Bash(npm:*) for repository-defined tests. Do not use production endpoints, funded signers, or live writes.

## Output

- Injectable QuickNode transport boundary
- Sanitized deterministic fixtures
- Fast offline test command
- Explicit sandbox-read contract

## Examples

An SDK adapter receives a stub base URL and fake clock. Retry tests advance virtual time, while a separate opt-in command performs one authenticated chain-ID read.

## Error Handling

| Failure | Response |
| --- | --- |
| Unit test reaches the network | Block outbound access and fix the adapter seam |
| Fixture contains a token | Remove it, rotate if real, and add a regression assertion |
| Retry test sleeps in real time | Inject clock and sleeper |
| Sandbox differs from production | Document the gap and cover it in protected CI |

## Resources

- [Local-loop evidence and source notes](references/official-docs.md)
- [SDK configuration](https://www.quicknode.com/docs/sdk/quick-start)
- [QuickNode API overview](https://www.quicknode.com/docs/build-with-ai/quicknode-apis)
