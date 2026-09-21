---
name: clari-security-basics
description: >-
  Secure Clari identities, credentials, exported revenue data, Copilot content, and ingestion mutations. Use when threat-modeling or reviewing least privilege and data handling. Trigger with: "secure Clari", "threat-model Clari", "review Clari access".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surface-data-classes-and-destination]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - security
  - least-privilege
  - data-governance
compatibility: 'Requires security ownership, a data-classification policy, approved secret storage, and an inventory of Clari surfaces and destinations.'
---

# Secure Clari Data Integration Boundary

## Overview

Protect both control-plane credentials and the business data they unlock. Clari exports can contain hierarchy, identity, forecast, quota, CRM, activity, and conversation data, while ingestion and Copilot CRM endpoints can mutate provider state.

## Prerequisites

- Integration data-flow diagram and endpoint inventory
- Named secret, privacy, retention, and incident owners
- Destination encryption, access-control, audit, and deletion capabilities

## Instructions

### Step 1: Classify every flow

Identify credentials, user and participant identifiers, revenue values, activity metadata, transcripts, recordings, and CRM objects by sensitivity.

### Step 2: Minimize authority

Use dedicated identities, separate Revenue, ingestion, and Copilot secrets, narrow hierarchy or workspace access, and deny mutation endpoints unless required.

### Step 3: Protect credentials

Store only references in configuration, redact all documented auth headers, rotate on schedule, and test revocation without exposing values.

### Step 4: Protect data in motion and at rest

Require HTTPS, encryption, restricted landing zones, field-level minimization, retention limits, and governed deletion.

### Step 5: Constrain mutations

Gate ingestion and Copilot create, update, or delete actions behind validation, reconciliation, explicit operator approval, and rollback planning.

### Step 6: Exercise response

Test credential exposure, overbroad access, incorrect export publication, and unauthorized mutation scenarios; retain redacted evidence.

## Authentication

Revenue `apikey`, ingestion `partnerkey`, and Copilot key/password credentials are distinct high-impact secrets. Never log them, accept them in free-form prompts, or reuse one surface’s credential in another client.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Threat model and data-classification matrix
- Least-privilege credential and endpoint policy
- Rotation, revocation, deletion, and incident drill receipts

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A pipeline grants a forecast integration user access only to the required hierarchy, stores raw exports in a restricted landing zone, publishes minimized aggregates, and denies ingestion and Copilot CRM mutation endpoints.

## Error Handling

| Failure | Response |
| --- | --- |
| Secret appears in a log or fixture | Revoke or rotate it immediately, contain the artifact, and document affected access. |
| Identity sees unexpected hierarchy data | Stop exports, reduce provider access, and review already-landed data before resuming. |
| Unauthorized mutation occurs | Disable the writer, preserve audit evidence, reconcile provider state, and execute the approved rollback. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
