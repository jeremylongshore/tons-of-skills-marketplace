---
name: canva-core-workflow-b
description: 'Operate Canva assets, brand-template autofill, and folders with explicit rights and asynchronous reconciliation. Use when performing uploads, dataset validation, autofill jobs, or folder changes. Trigger with: "upload Canva asset", "autofill brand template", "manage Canva folder".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[asset-template-or-folder-operation]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - assets
  - operations
compatibility: 'Requires operation-specific scopes, resource rights, current feature availability, and an approved asset/data classification.'
---

# Canva Asset, Autofill, and Folder Workflow

## Overview

Treat asset upload, dataset discovery, autofill, and folder mutation as separate authorization domains. Re-read schemas and reconcile asynchronous jobs rather than assuming old fields or completion.

## Prerequisites

- Authorized owner, tenant, operation, and destination
- Explicit asset, design, brand-template, or folder scopes
- Approved file rights, data classification, and cleanup policy

## Instructions

### Step 1: Choose one operation

Identify upload, asset metadata change, template dataset read, autofill, or folder mutation. Do not bundle unrelated writes into one approval.

### Step 2: Validate rights and input

Confirm resource ownership, file type/size against the current endpoint, malware policy, template availability, and every requested explicit scope.

### Step 3: Submit upload safely

For binary or URL upload, record the operation and job ID, avoid logging source URLs or content, and poll the corresponding existing job.

### Step 4: Refresh the dataset

Read the current template or design dataset immediately before autofill. Reject unknown required fields and disclose that nonexistent field names may be skipped.

### Step 5: Run autofill deliberately

Confirm current entitlement and preview status, validate each data value, submit once, and reconcile the job before exposing the resulting design.

### Step 6: Apply folder mutation

Validate source/destination authorization and expected current state, make one bounded change, then read back metadata and record rollback.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

An approved campaign asset is uploaded, a current brand-template dataset is fetched, authorized fields are autofilled, and the resulting design is moved only after each job and ownership check succeeds.

## Error Handling

| Failure | Response |
| --- | --- |
| Dataset changed | Stop and revalidate input mapping |
| Upload job failed | Correct the documented cause before resubmitting |
| Autofill unavailable | Do not suggest a plan upgrade; report current capability evidence |
| Folder state diverged | Stop further moves and reconcile ownership |

## Resources

- [First-party source notes](references/official-docs.md)
- [Asset APIs](https://www.canva.dev/docs/connect/api-reference/assets/)
- [Autofill guide](https://www.canva.dev/docs/connect/autofill-guide/)
