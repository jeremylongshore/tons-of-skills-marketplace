---
name: workhuman-install-auth
description: 'Select and document the supported Workhuman access path for a customer tenant, including SSO, managed integrations, or customer-issued API credentials. Use when onboarding or repairing an integration. Trigger with "configure Workhuman access".'
argument-hint: "[tenant] [integration-purpose]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, authentication, sso, integration]
model: inherit
effort: medium
compatibility: Designed for Claude Code; tenant access, identity changes, managed integrations, and credential issuance require customer and Workhuman authorization
---
# Workhuman Tenant Access and Integration Onboarding

## Overview

Choose the supported access model, establish ownership, and prove the smallest safe capability without guessing a host, route, grant, or credential format.

## Prerequisites

- The customer tenant, subscribed products, program owner, and integration purpose
- Identity, security, data, and support owners for the affected workforce records
- Current customer-authorized Workhuman documentation or an assigned Workhuman implementation contact

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local configuration, `WebFetch` to re-check first-party public and authorized tenant contracts, and `Write` or `Edit` only for secretless configuration and redacted evidence.

## Current Contract

Workhuman publicly documents SSO, controlled privileges, an open API, and managed integrations such as Microsoft Teams and Workday. Its public pages do not define one universal API host, OAuth flow, scope set, or verification route; obtain those details from the customer's current contract.

## Authentication

Separate interactive SSO, managed-connector authorization, and API credentials. Do not reuse browser sessions, infer `client_credentials`, copy administrator cookies, or put secrets in files, commands, prompts, logs, or receipts.

## Instructions

1. Record tenant, products, data classes, intended reads and writes, environments, and accountable owners.
2. Classify the path as interactive SSO, a Workhuman-managed integration, or a customer-issued API contract.
3. Re-fetch the applicable first-party product page and the customer's current implementation documentation.
4. Build an access matrix covering principal, roles or scopes, expiry, rotation, revocation, and break-glass ownership.
5. Search the repository for guessed hosts, undocumented routes, hard-coded secrets, and mixed-tenant configuration.
6. Present every tenant setting, connector enablement, consent, and credential request for explicit approval.
7. After authorized provisioning, run the smallest documented read-only check and retain only redacted status and correlation evidence.

## Approval Boundaries

Do not change SSO, assign privileges, enable an integration, issue credentials, or test production writes without the relevant customer and vendor owners.

## Output

Return the selected access path, contract evidence, access matrix, secretless configuration, verification receipt, rotation and revocation owners, and unresolved vendor questions.

## Error Handling

| Condition | Response |
|---|---|
| Customer API documentation is unavailable | Stop at the decision record and request it from the program owner or Workhuman. |
| SSO succeeds but an integration fails | Diagnose the connector or API principal independently; do not reuse the browser session. |
| Capability is not subscribed | Record the entitlement gap and route it to the commercial or program owner. |

## Example

A redacted completion receipt might look like this:

```text
tenant=customer-specific; path=managed-workday; principal=vendor-managed; contract=current; smoke=read-only-pass; secrets=redacted
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)

## Next Steps

Test reauthorization or credential rotation in a non-production context and assign a contract review date.
