---
name: canva-data-handling
description: 'Analyze and govern Canva credentials, user metadata, designs, assets, comments, and temporary result URLs across their lifecycle. Use when defining collection, storage, access, retention, deletion, or privacy controls. Trigger with: "classify Canva data", "Canva retention", "delete Canva integration data".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[data-classification-and-retention-policy]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - data
  - operations
compatibility: 'Requires an approved organizational privacy/security policy and resource-owner authorization; this skill is not legal advice.'
---

# Canva Data Lifecycle Control

## Overview

Create an application-specific lifecycle map for every Canva data class. Minimize stored content, keep credentials segregated, and make deletion/revocation evidence reproducible without logging protected values.

## Prerequisites

- Current data-flow and storage inventory
- Approved classification, retention, deletion, and legal-hold policy
- Tenant and resource ownership model plus incident contacts

## Instructions

### Step 1: Inventory data classes

Use Read and Grep to locate client secrets, access and refresh tokens, OAuth state/verifier, user/profile metadata, design references/content, assets, comments, job results, and logs.

### Step 2: Define collection purpose

For each class, record purpose, explicit scope, source endpoint, owner, destination, processors, and whether collection can be avoided.

### Step 3: Protect credentials

Store client secrets and user tokens in protected backend systems, separate access from refresh tokens, restrict operators, and exclude them from logs and backups where policy requires.

### Step 4: Control content and URLs

Encrypt approved stored content, authorize every read, avoid durable storage of signed URLs, and derive expiry from current response evidence rather than a fixed assumption.

### Step 5: Implement lifecycle

Use Write or Edit to apply policy-controlled expiration, consent revocation, account deletion, resource deletion, legal hold, and processor cleanup.

### Step 6: Prove completion

Record counts, policy version, timestamps, opaque references, failed deletions, and follow-up owner without retaining deleted content in the receipt.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A user disconnects the integration. The service revokes or discards tokens, expires cached metadata and result references, schedules approved content deletion, and records a content-free receipt.

## Error Handling

| Failure | Response |
| --- | --- |
| Owner cannot be resolved | Quarantine access and stop processing |
| Deletion conflicts with legal hold | Preserve only the authorized hold and record its authority |
| Token appears in telemetry | Contain, revoke, and remediate the logging path |
| Processor deletion fails | Record the exception and escalate to the policy owner |

## Resources

- [First-party source notes](references/official-docs.md)
- [Connect security](https://www.canva.dev/docs/connect/guidelines/security/)
- [Canva privacy policy](https://www.canva.com/policies/privacy-policy/)
