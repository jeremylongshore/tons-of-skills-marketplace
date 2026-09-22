---
name: quicknode-ci-integration
description: 'Build a fork-safe QuickNode CI contract lane with mocked default tests and a protected read-only integration check. Use when preventing chain, network, method, SDK, or secret drift before deployment. Trigger with: "test QuickNode in CI", "add a QuickNode contract test", "secure QuickNode GitHub Actions".'
allowed-tools: Read, Grep, Write, Edit, Bash(npm:*)
version: 2.0.0
argument-hint: '[test-command-and-protected-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - ci
  - testing
  - security
compatibility: 'Live checks require a protected CI environment and a read-only QuickNode credential'
---

# QuickNode CI Contract Lane

## Overview

Keep pull-request tests deterministic and credential-free. Run a minimal live QuickNode read only after trust has been established, with environment protection and no secrets exposed to forked code.

## Prerequisites

- Existing test framework and CI provider
- QuickNode adapter boundary with injectable transport
- Protected environment containing a read-only endpoint or API key

## Instructions

### Step 1: Inventory the pipeline

Use Read and Grep to find workflow triggers, fork behavior, secret references, generated code, endpoint fixtures, and commands that can sign or submit transactions.

### Step 2: Define offline contracts

Use Write or Edit to test JSON-RPC request IDs, chain-ID validation, result-versus-error parsing, timeout behavior, rate-limit classification, and redaction with fixtures. Mock at the transport boundary.

### Step 3: Add a protected live read

Permit one documented, low-cost read method in a trusted environment. Assert chain identity and response shape rather than a volatile block value. Never load a funded signer or production write credential.

### Step 4: Close the fork boundary

Do not expose QuickNode secrets to untrusted pull requests or execute fork-controlled code in a privileged `pull_request_target` context. Require environment approval or a trusted post-merge lane.

### Step 5: Pin toolchain inputs

Use Bash(npm:*) to run the existing pinned test command. Commit lockfile changes with SDK upgrades, pin third-party workflow actions by immutable revision under repository policy, and reject install scripts not already reviewed.

### Step 6: Produce a gate receipt

Record exact commit, command, offline results, live method, chain ID, latency, and redaction check. Make the live lane fail closed when its credential is expected but absent.

## Tool Discipline

Use Read and Grep for CI discovery, Write/Edit for fixtures and workflow changes, and Bash(npm:*) only for repository-defined package and test commands. Do not invoke live RPC from an untrusted event.

## Output

- Credential-free default contract suite
- Protected read-only integration lane
- Fork and secret-exposure controls
- Exact-head CI receipt

## Examples

A public fork runs parser and retry fixtures only. A protected main-branch job reads `eth_chainId`, verifies the expected network, and stores no endpoint URL in logs.

## Error Handling

| Failure | Response |
| --- | --- |
| Fork can access secrets | Disable the lane and correct the event boundary |
| Live block assertion flakes | Assert response contract and chain identity instead |
| Credential silently absent | Fail the protected lane with a configuration error |
| Test can submit transactions | Replace the credential and constrain the adapter |

## Resources

- [CI evidence and source notes](references/official-docs.md)
- [QuickNode APIs](https://www.quicknode.com/docs/build-with-ai/quicknode-apis)
- [SDK quickstart](https://www.quicknode.com/docs/sdk/quick-start)
