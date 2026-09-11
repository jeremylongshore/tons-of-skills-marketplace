---
name: salesforce-install-auth
description: 'Select and document a supported Salesforce authorization path using an External Client App or an approved existing Connected App. Use when onboarding or repairing API access. Trigger with "configure Salesforce authentication".'
argument-hint: "[org-alias] [integration-purpose]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, authentication, oauth, external-client-app]
model: inherit
effort: high
compatibility: Designed for Claude Code; identity and client-app changes require Salesforce org owner and security approval
---
# Salesforce API Authorization and Client-App Onboarding

## Overview

Choose the app and OAuth model, establish least privilege, and prove read-only access without defaulting to legacy username-password automation.

## Prerequisites

- Target org, edition, domain, environment, integration purpose, and data classes
- Identity, security, Salesforce administration, application, and support owners
- Current org policy and first-party OAuth documentation

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce REST API supports OAuth through External Client Apps or Connected Apps. Creating Connected Apps is restricted as of Spring '26; existing Connected Apps can continue, while Salesforce recommends External Client Apps for new integrations.

## Authentication

Select an OAuth flow from current Salesforce documentation for the workload and client type. Never copy browser sessions, use a human password in automation, log tokens, or assume that one flow, scope set, or login host fits every org.

## Instructions

1. Record the org, My Domain, edition, environment, workload, required resources, and accountable owners.
2. Determine whether the org requires an External Client App or has an approved existing Connected App.
3. Map the selected OAuth flow, scopes, policies, principal, certificate or secret custody, expiry, rotation, and revocation.
4. Inspect the repository for password flows, unpinned login hosts, broad scopes, plaintext keys, and mixed-org aliases.
5. Present app creation, policy, permission-set assignment, pre-authorization, and credential issuance for explicit approval.
6. After provisioning, discover supported API versions and run the smallest documented read-only identity or resource check.
7. Store only secret references and a redacted receipt; test revocation and recovery in a non-production org.

## Approval Boundaries

Do not create or alter a client app, grant scopes, assign permissions, issue credentials, or test production writes without the named org and security owners.

## Output

Return the app-type decision, OAuth contract, access matrix, secret references, read-only verification, rotation and revocation owners, and unresolved policy questions.

## Error Handling

| Condition | Response |
|---|---|
| New Connected App creation is unavailable | Use the org-approved External Client App path or obtain Salesforce Support guidance; do not bypass the restriction. |
| Authorization succeeds but a resource is denied | Compare scopes, permission sets, CRUD, field access, sharing, edition, and API entitlement independently. |
| Current OAuth contract is unknown | Stop before provisioning and obtain current org-specific documentation. |

## Example

A redacted completion receipt might look like this:

```text
org=sandbox; app=external-client-app; flow=org-approved; scopes=least-privilege; probe=read-only-pass; secrets=referenced
```

## Resources

- [Salesforce REST authorization](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)
- [Salesforce REST API introduction](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.

