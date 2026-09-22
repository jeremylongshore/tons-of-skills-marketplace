---
name: quicknode-core-workflow-a
description: 'Design a safe EVM transaction-submission path over QuickNode with simulation, fee and nonce policy, signer isolation, broadcast identity, and confirmation rules. Use when moving a read-only integration into transaction writes. Trigger with: "send transactions through QuickNode", "build an EVM write path", "harden QuickNode transaction submission".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[chain-network-and-write-operation]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - ethereum
  - transactions
  - reliability
compatibility: 'EVM method availability, fee fields, and finality rules vary by chain and network'
---

# QuickNode EVM Transaction Safety

## Overview

Build a write path that treats signing, submission, and confirmation as separate state transitions. QuickNode transports the signed transaction; the application remains responsible for intent, signer custody, nonce coordination, chain identity, and reorganization policy.

## Prerequisites

- A verified QuickNode endpoint and expected EVM chain ID
- A testnet signer held outside source code
- Contract ABI, write intent, value ceiling, and confirmation policy

## Instructions

### Step 1: Inspect the existing path

Use Read and Grep to find signers, private-key variables, nonce overrides, fee logic, retries, and receipt assumptions. Stop if secrets or signed raw transactions are logged.

### Step 2: Define transaction intent

Use Write or Edit to express destination, calldata, value, chain ID, and caller policy as validated inputs. Reject unexpected networks and unbounded value before reaching the signer.

### Step 3: Simulate and estimate

Run the equivalent read call and gas estimate at an explicit block tag when supported. Treat a revert as an application or chain-state result, not a transient provider failure.

### Step 4: Coordinate nonce and fees

Assign one nonce owner per signer. Read pending nonce state, define replacement rules, and use chain-appropriate fee fields. Do not blindly overwrite a nonce or double fees on each timeout.

### Step 5: Sign and broadcast once

Keep signing in a wallet, HSM, or approved remote signer. Persist the signed transaction hash before submission. On an ambiguous timeout, query by hash before broadcasting again.

### Step 6: Confirm by policy

Track inclusion, receipt status, block hash, and the required chain-specific confirmation depth. Reconcile dropped or reorganized receipts and expose a durable business-operation idempotency key.

## Tool Discipline

Use Read and Grep for transaction-path discovery and Write/Edit for validation, state-machine, and tests. This skill never asks the agent to hold a private key or execute a funded transaction.

## Output

- Validated transaction-intent schema
- Signer, nonce, fee, and broadcast ownership contract
- Ambiguous-submission reconciliation path
- Chain-specific confirmation and reorg policy

## Examples

A payment request is recorded before signing. If broadcast times out, the worker searches for the known transaction hash and never manufactures a second payment from the same business request.

## Error Handling

| Failure | Response |
| --- | --- |
| Simulation reverts | Decode against ABI and state; do not retry automatically |
| Nonce too low | Reconcile pending and mined transactions for the signer |
| Broadcast timeout | Query the persisted hash before deciding whether to resubmit |
| Receipt disappears | Return to pending and apply the documented reorg policy |

## Resources

- [Transaction-safety evidence and source notes](references/official-docs.md)
- [Ethereum API overview](https://www.quicknode.com/docs/ethereum/api-overview)
- [QuickNode Ethereum methods](https://www.quicknode.com/docs/ethereum)
