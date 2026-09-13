---
name: procore-prod-checklist
description: >-
  Gate a Procore integration for production with evidence for security, permissions, lifecycle, support, sandbox testing, health, rate handling, webhooks, and rollback. Use when preparing for customer launch or Marketplace submission. Trigger with: "review Procore production readiness", "check Procore launch", "prepare Procore Marketplace approval".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-version-and-launch-scope]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - production-readiness
  - marketplace
compatibility: 'Requires a release candidate, Procore app version, sandbox evidence, operational owners, and production approval authority.'
---

# Procore Production Readiness Gate

## Overview

Convert launch claims into verifiable evidence. This gate covers the integration and its Procore app contract; it does not declare Marketplace approval or provider certification merely because local checks pass.

## Prerequisites

- Immutable release candidate and matching app version
- Data classification, permission map, environment matrix, and endpoint inventory
- Support, security, operations, rollback, and customer communication owners

## Instructions

### Step 1: Verify application contract

Confirm semantic version, release notes, components, callbacks, permissions, permitted-project behavior, installation instructions, and production credentials.

### Step 2: Verify functional paths

Exercise token lifecycle, required reads, expected denials, approved mutations, pagination, files, webhooks, deduplication, reconciliation, and cleanup in the intended sandbox.

### Step 3: Verify reliability

Prove handling for 401, 403, hidden 404, 422, 429, 503, timeout, ambiguous write, duplicate event, discarded event window, and provider outage.

### Step 4: Verify security and privacy

Review secret storage and rotation, tenant routing, least privilege, log redaction, secure-file handling, data retention, deletion, and incident escalation.

### Step 5: Verify operations

Establish Integration Health and API activity review, rate and backlog alerts, support intake, status-page dependency, runbooks, and on-call ownership.

### Step 6: Decide explicitly

Record PASS, CONDITIONAL, or FAIL per gate with evidence. Require launch approval and preserve rollback triggers; do not convert missing evidence into a pass.

## Authentication

Readiness tests use the selected OAuth 2.0 grant, environment-specific credentials, and intended user or DMSA permission boundary. Evidence excludes all tokens, client secrets, and webhook destination credentials.

## Tool Discipline

Use Read and Grep to inspect release artifacts, tests, manifests, and evidence. Use Write or Edit only for the approved checklist, remediation, test, or redacted receipt; passing this workflow does not authorize provider-side promotion.

## Output

- Evidence matrix for application, function, reliability, security, and operations
- Explicit gaps, owners, rollback triggers, and approval
- Launch or no-launch decision with provider-certification boundary

Return exact release identifiers, gate verdicts, evidence references, approvers, and unresolved risks.

## Examples

A release passes happy paths but lacks proof for discarded webhook recovery. The gate remains conditional until a bounded outage test shows reconciliation closes the gap; it does not award itself Procore Marketplace approval.

## Error Handling

| Failure | Response |
| --- | --- |
| Evidence references a mutable build | Fail the gate and rebuild from an immutable release. |
| Required permission is unexplained | Reduce or justify it with endpoint and test evidence. |
| Failure path is untested | Keep the gate open and run a bounded sandbox test. |
| Rollback cannot restore compatibility | Stop launch until a viable rollback or forward-fix boundary exists. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Marketplace Approval Checklist](https://developers.procore.com/documentation/marketplace-checklist)
- [Verification and production access](https://developers.procore.com/documentation/verification-and-production-access)
- [Integration Health](https://developers.procore.com/documentation/integration-health)
