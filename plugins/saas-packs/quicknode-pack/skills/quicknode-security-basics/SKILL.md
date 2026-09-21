---
name: quicknode-security-basics
description: 'Harden QuickNode endpoints with server-side token handling, separate credentials, least-privilege account roles, and plan-appropriate security filters. Use when reviewing exposure, isolating applications, or responding to a leaked endpoint. Trigger with: "secure QuickNode", "harden a QuickNode endpoint", "rotate a leaked QuickNode token".'
allowed-tools: Read, Grep, Write, Edit, Bash(qn:*)
version: 2.0.0
argument-hint: '[endpoint-and-threat-model]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - security
  - authentication
  - hardening
compatibility: 'JWT, referrer allowlists, domain masking, and advanced rate controls can be plan-specific'
---

# QuickNode Endpoint Hardening

## Overview

Protect endpoint tokens as credentials, isolate consumers with multiple tokens, and layer only controls that match the client threat model. A browser referrer rule is not a substitute for keeping privileged RPC or account keys on a server.

## Prerequisites

- Endpoint inventory with owners, applications, and environments
- Current plan and available endpoint-security controls
- A threat model covering browser, server, CI, and operator access

## Instructions

### Step 1: Find exposure

Use Read and Grep for `quiknode.pro`, `x-token`, `x-api-key`, JWT configuration, logs, examples, and client bundles. Stop and rotate any live credential committed to Git or shipped to an untrusted client.

### Step 2: Separate identities

Create distinct endpoint tokens for applications and environments. Keep Admin API/SDK API keys separate from chain RPC tokens. Apply least-privilege team and account roles.

### Step 3: Choose layered controls

Use token authentication for every endpoint. Add JWT for short-lived server authorization when supported, referrer allowlists for browser-origin reduction, and IP or method limits for known traffic patterns. Document plan dependencies.

### Step 4: Keep privileged calls server-side

Use Write or Edit to route transaction submission, archive/debug methods, and account-control calls through a trusted backend. Do not embed endpoint or API tokens in public JavaScript.

### Step 5: Inspect configuration

Use Bash(qn:*) to read endpoint security state with an approved authenticated operator identity. Compare actual tokens, filters, limits, domains, and team access to the declared policy without printing secret values.

### Step 6: Exercise response

Prove that an unauthorized origin, token, method, or IP is rejected as designed. Revoke one test token and confirm other isolated consumers continue. Record recovery time and escalation owner.

## Tool Discipline

Use Read and Grep for exposure discovery, Write/Edit for server-side boundaries and policy, and Bash(qn:*) for read-only security inspection. Credential creation, revocation, and production filter changes require an explicit checkpoint.

## Output

- Endpoint threat model and credential map
- Actual-versus-declared security control comparison
- Negative authorization tests
- Rotation and incident-response procedure

## Examples

A public dApp calls a backend that holds the endpoint token. Production and staging use separate tokens, and a method limit prevents the public route from invoking debug methods.

## Error Handling

| Failure | Response |
| --- | --- |
| Token exposed | Revoke, replace, sanitize history and logs, then investigate use |
| Referrer rule blocks valid traffic | Roll back the specific rule; do not expose the token |
| `-32611` rejection | Compare method and filter policy before retrying |
| Security feature unavailable | Record the plan gap and enforce the boundary in the application |

## Resources

- [Security evidence and source notes](references/official-docs.md)
- [Multi-token authentication](https://www.quicknode.com/guides/quicknode-products/endpoint-security/how-to-set-up-multi-token-authentication-on-quicknode)
- [Method rate limits](https://www.quicknode.com/guides/quicknode-products/endpoint-security/how-to-setup-method-rate-limits)
