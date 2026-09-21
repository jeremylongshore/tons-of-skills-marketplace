---
name: castai-install-auth
description: 'Choose and configure the correct CAST AI authentication boundary for castctl, REST API, Terraform, or enterprise child-organization access. Use when connecting a cluster, provisioning an automation identity, or repairing region and organization mismatches. Trigger with: "authenticate CAST AI", "set up a CAST AI API key", "configure CAST AI access".'
allowed-tools: Read, Grep, Write, Edit, Bash(castctl:*), Bash(curl:*)
version: 2.0.0
argument-hint: '[client-and-organization-scope]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - authentication
  - security
compatibility: 'Requires CAST AI console access to create scoped keys; regional endpoints are US, EU, or India as documented'
---

# CAST AI Authentication Boundary

## Overview

Keep human castctl login, service API keys, enterprise organization targeting, and cluster installation secrets separate. Choose the narrowest identity for one client, region, organization, and lifecycle.

## Prerequisites

- The intended client: castctl, REST, Terraform, CI, or another approved integration
- CAST AI organization, role binding, and environment region
- An approved secret manager, rotation owner, and expiration or review date

## Instructions

### Step 1: Classify the actor

Use Read and Grep to find existing CAST AI environment variables, provider configuration, CI secrets, Helm values, and runbooks. Distinguish a human interactive session from non-interactive automation; do not reuse one credential across both.

### Step 2: Select the authentication path

For human cluster connection, use Bash(castctl:\*) with browser login; castctl stores its own local token and organization selection. For REST or Terraform automation, create an API access key whose inherited role bindings match the required operations.

### Step 3: Pin region and organization

Use the documented US, EU, or India API base that matches the CAST AI environment. Send API keys only in the `X-API-Key` header. For an enterprise key targeting a child organization, also provide `X-CastAI-Organization-Id`; never infer that identifier from a cluster name.

### Step 4: Store without exposure

Use Write or Edit to add secret references, not values, to configuration. Keep keys out of Git, command history, URLs, Terraform outputs, plan artifacts, Helm-rendered output, logs, and support bundles.

### Step 5: Verify minimally

Use Bash(curl:\*) only against a documented read endpoint selected from the current CAST AI API specification. Limit output to status and a non-sensitive identifier, set a timeout, and test the expected 401 or 403 path with no credential.

### Step 6: Record lifecycle

Document owner, client, role basis, organization, region, storage location, creation time, review date, rotation procedure, and revocation condition. Because a created key cannot be viewed again, loss requires replacement rather than recovery.

## Tool Discipline

Use Read and Grep for credential-reference discovery. Use Write and Edit only for secret references and lifecycle documentation. Use Bash(castctl:_) for documented interactive auth and Bash(curl:_) for a bounded read-only verification; never print headers or key values.

## Output

- Actor/client authentication decision
- Region and organization boundary
- Secret-reference configuration
- Minimal verification and rotation record

## Examples

A developer uses castctl browser login for a reviewed sandbox connection. A CI job uses a separate organization-scoped read-only API key against the EU endpoint and cannot target sibling organizations.

## Error Handling

| Failure                          | Response                                                           |
| -------------------------------- | ------------------------------------------------------------------ |
| A key appears in history or logs | Revoke it, remove exposure, and create a replacement               |
| API returns 401                  | Verify key validity and regional base without widening permissions |
| API returns 403                  | Review role bindings and organization targeting                    |
| Enterprise call hits wrong child | Stop and correct the explicit organization header                  |

## Resources

- [Authentication evidence and source notes](references/official-docs.md)
- [API access](https://docs.cast.ai/docs/api-access)
- [Connect with castctl](https://docs.cast.ai/docs/connect-with-castctl)
- [CAST AI API specification](https://api.cast.ai/spec/)
