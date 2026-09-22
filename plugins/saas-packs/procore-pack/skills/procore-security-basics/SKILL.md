---
name: procore-security-basics
description: >-
  Threat-model a Procore integration across OAuth credentials, company routing, DMSA permissions, webhooks, files, logs, and revocation. Use when reviewing a new app, hardening production, or responding to credential exposure. Trigger with: "secure a Procore integration", "review Procore API security", "rotate Procore credentials".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[application-and-data-classification]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - security
  - threat-modeling
compatibility: 'Requires application architecture, data classification, permission inventory, and access to the Procore app configuration.'
---

# Procore Integration Security Boundary

## Overview

Protect construction data by constraining identity, company and project scope, transport, stored artifacts, and operator actions. Procore authorization is permission-based; neither a valid token nor a successful request proves least privilege.

## Prerequisites

- Data-flow diagram, asset classification, trust boundaries, and named security owner
- OAuth grant, credential locations, DMSA manifest, and permitted-project inventory
- Webhook destinations, file flows, log sinks, support path, and revocation procedure

## Instructions

### Step 1: Inventory secrets and principals

Locate client secrets, access and refresh tokens, webhook destination secrets, cookies, and signed URLs. Ensure each secret has an owner, approved store, rotation path, and narrow audience.

### Step 2: Prove least privilege

Map every endpoint to its required Procore tool permission and project scope. For DMSAs, compare the manifest with installed permitted projects and remove unexplained access.

### Step 3: Bind company routing

Carry company context explicitly and validate `Procore-Company-Id` where required. Prevent a multi-company worker or event handler from reusing stale tenant context.

### Step 4: Protect data paths

Use supported TLS, authenticate secure-file downloads as documented, sanitize logs and traces, and keep payload retention proportional to the business requirement.

### Step 5: Harden mutations

Separate preview from execution, require approval for consequential changes, validate project ownership, and reconcile provider state after writes.

### Step 6: Exercise response

Test revocation, credential rotation, app disconnection, webhook-secret rotation, and audit retrieval. Record recovery time without exposing the secrets under test.

## Authentication

Procore API access uses OAuth 2.0 Bearer tokens from Authorization Code or DMSA Client Credentials. Store client secrets server-side, rotate credentials regularly, and revoke authorization when access is no longer valid.

## Tool Discipline

Use Read and Grep to inspect architecture, manifests, configuration, and evidence. Use Write or Edit only for the approved threat model, security change, test, or redacted receipt; provider permission changes require administrator approval.

## Output

- Threat model and endpoint-to-permission map
- Secret, routing, file, webhook, and mutation controls
- Rotation, revocation, and negative-access test evidence

Return risks by severity, bounded remediation, owner, due condition, and verification status.

## Examples

A multi-company connector passes company context with every job and tests that a permitted DMSA cannot read an unselected project. Logs retain normalized routes and status codes while excluding tokens, project names, payloads, and signed file URLs.

## Error Handling

| Failure | Response |
| --- | --- |
| Credential exposed | Revoke or rotate immediately, invalidate caches, and scrub derived artifacts. |
| Excess project access | Stop affected processing and reduce DMSA or user scope before resuming. |
| Company context is ambiguous | Fail closed rather than dispatching against a default tenant. |
| Secure file URL is logged | Remove and expire the artifact, then repair logging and retrieval boundaries. |

## Resources

- [First-party source notes](references/official-docs.md)
- [API security overview](https://developers.procore.com/documentation/api-security-overview)
- [Developer Managed Service Accounts](https://developers.procore.com/documentation/developer-managed-service-accounts)
- [Secure file access](https://developers.procore.com/documentation/secure-file-access-tips)
