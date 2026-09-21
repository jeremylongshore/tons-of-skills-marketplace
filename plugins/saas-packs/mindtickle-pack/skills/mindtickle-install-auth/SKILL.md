---
name: mindtickle-install-auth
description: 'Select and document the correct Mindtickle access path for a tenant, including browser SSO, user provisioning, managed connectors, or customer-issued API credentials. Use when onboarding or repairing an integration. Trigger with "configure Mindtickle access".'
argument-hint: "[tenant] [integration-purpose]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, authentication, sso, scim]
model: inherit
effort: medium
compatibility: Designed for Claude Code; tenant access, identity configuration, connector enablement, and credential issuance require customer and Mindtickle authorization
---
# Mindtickle Tenant Access and Integration Onboarding

## Overview

Choose the supported access model, establish ownership, and verify the smallest safe capability without inventing a universal endpoint or credential format.

## Prerequisites

- The customer's tenant URL, subscription package, site owner, and integration purpose
- An identity, security, and data owner for the affected users and records
- Customer-authorized tenant documentation or a Mindtickle Technical Solutions contact

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local configuration, `WebFetch` to re-check official public and tenant-authorized contracts, and `Write` or `Edit` only for secretless configuration and redacted evidence.

## Current Contract

Mindtickle documents tenant-specific web URLs, role-based administration, managed integrations, REST-based Content/User/Reporting APIs, and standards including SCIM, SAML, and OpenID. Exact API hosts, routes, schemas, credentials, and entitlements are tenant-controlled and must be obtained from authorized documentation.

## Authentication

Separate interactive SSO, automated provisioning, managed connector authorization, and API credentials. Do not treat an SSO session as API authorization, guess headers, reuse administrator cookies, or place secrets in files, logs, prompts, or receipts.

## Instructions

1. Record the tenant, package, data classes, systems of record, intended reads and writes, and accountable owners.
2. Classify the path as browser SSO, SCIM/user sync, a catalogued managed integration, or a customer-issued API contract.
3. Re-fetch the applicable public product description and the customer's current tenant documentation.
4. Build an access matrix covering principal, roles, scopes, environments, expiration, rotation, revocation, and break-glass ownership.
5. Inspect the repository for guessed hosts, hard-coded secrets, browser-session reuse, and mixed tenant configuration.
6. Present every tenant setting, consent, connector enablement, and credential request for explicit approval.
7. After authorized provisioning, perform the smallest documented read-only check and retain only redacted status, principal class, tenant, and request identifiers.

## Approval Boundaries

Do not invite users, change SSO or provisioning, enable a connector, issue credentials, broaden access, or test production writes without the relevant owner.

## Output

Return the selected access path, entitlement evidence, access matrix, secretless configuration, verification receipt, rotation/revocation owner, and unresolved vendor questions.

## Error Handling

| Condition | Response |
|---|---|
| Tenant documentation is unavailable | Stop at the decision record and request it from the site owner or Mindtickle. |
| SSO succeeds but an integration fails | Diagnose the integration credential independently; do not reuse the browser session. |
| Capability is not in the package | Record the entitlement gap and route it to the commercial or site owner. |

## Example

```text
tenant=customer-specific; path=managed-connector; principal=service-owned; entitlement=confirmed; smoke=read-only-pass; secrets=redacted
```

## Resources

- [Mindtickle integrations](https://www.mindtickle.com/platform/integrations/)
- [Subscription services](https://www.mindtickle.com/legal/description-of-subscription-services/)
- [Mindtickle Trust](https://www.mindtickle.com/trust/)

## Next Steps

Test credential rotation or connector reauthorization in a non-production tenant and assign a review date.
