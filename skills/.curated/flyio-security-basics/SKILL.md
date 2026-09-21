---
name: flyio-security-basics
description: >-
  Harden Fly.io tokens, deploy authority, App secrets, private networking, images, and operational evidence with least privilege. Use when establishing or reviewing platform security. Trigger with: "secure Fly app", "audit Fly tokens", "harden Fly private network".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[organization-app-and-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - security
  - least-privilege
  - secrets
compatibility: 'Requires named security and application owners, a Fly.io organization and app inventory, approved identity policy, and access to redacted configuration evidence.'
---

# Fly.io Identity, Secrets, and Network Baseline

## Overview

Protect the control plane, deployed code, runtime secrets, images, network paths, and support evidence as one system. Scoped tokens reduce control-plane authority, but deploy access remains highly sensitive because new code can read secrets injected into Machines.

## Prerequisites

- Human and workload identity inventory with owners and expiry policy
- Apps, process groups, images, domains, certificates, private peers, and data flows
- Incident, rotation, vulnerability, and access-review procedures

## Instructions

### Step 1: Separate identity classes

Distinguish interactive operators, app deploy automation, organization automation, read-only monitoring, SSH, Machine-exec, WireGuard, database, and external-service identities.

### Step 2: Apply least privilege and expiry

Use app deploy tokens for one app, read-only organization tokens for observation, and short-lived command or SSH tokens for bounded access. Review and revoke by token ID.

### Step 3: Protect runtime secrets

Store app values through Fly secrets, inspect only names and digests, stage changes when appropriate, and prevent deployed code, logs, crashes, and support bundles from exfiltrating values.

### Step 4: Control code and images

Require reviewed immutable images, dependency and vulnerability gates, provenance, protected production environments, release approval, and rollback. Treat image registry and build credentials separately.

### Step 5: Protect network paths

Map public services, certificates, 6PN, Flycast, WireGuard peers, outbound destinations, and application authentication. Private reachability does not imply trusted requests.

### Step 6: Prove operations

Exercise token rotation, emergency revocation, secret update, deploy rollback, access review, log redaction, and incident escalation with timestamped receipts.

## Authentication

Current guidance deprecates routine use of the all-powerful `fly auth token` output. Store scoped tokens in an approved secret manager and expose them only to the intended process. Never place tokens, secret values, WireGuard keys, or database URLs in source or evidence.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Identity and authority matrix with scope, owner, expiry, and review date
- Secret, image, network, logging, and evidence control assessment
- Prioritized remediation and tested rotation, revocation, rollback, and incident receipts

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A production app has one expiring app deploy token, a separate read-only monitoring token, short-lived Machine-exec access for migrations, protected image promotion, named WireGuard peers, and a quarterly drill that revokes and replaces each automation credential.

## Error Handling

| Failure | Response |
| --- | --- |
| Unknown or ownerless token | Revoke after dependency review or assign owner and expiry immediately; do not leave indefinite authority. |
| Secret appears in logs or evidence | Contain access, rotate the secret, sanitize retained artifacts, and investigate deployed code and pipeline output. |
| Private service lacks app authentication | Add workload authentication and authorization; 6PN reachability is not an identity decision. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Access tokens](https://fly.io/docs/security/tokens/)
- [App secrets](https://fly.io/docs/apps/secrets/)
- [Private networking](https://fly.io/docs/networking/private-networking/)
- [Health checks](https://fly.io/docs/reference/health-checks/)
