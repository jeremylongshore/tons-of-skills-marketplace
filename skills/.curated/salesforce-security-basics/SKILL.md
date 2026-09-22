---
name: salesforce-security-basics
description: 'Secure a Salesforce integration across OAuth, principals, permissions, sharing, fields, secrets, encryption, logging, and revocation. Use when reviewing threats or hardening controls. Trigger with "secure Salesforce integration".'
argument-hint: "[org-alias] [integration]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, security, least-privilege, data-protection]
model: inherit
effort: high
compatibility: Designed for Claude Code; security, identity, permission, sharing, and encryption changes require customer security and Salesforce administrator approval
---
# Salesforce Integration Security Baseline

## Overview

Build a shared-responsibility control set that connects the external application, Salesforce org, principal, data, event, and operational boundaries.

## Prerequisites

- System context, data classes, org topology, app type, principal, APIs, events, and support paths
- Current customer security policy, Salesforce security documentation, and threat model
- Identity, security, Salesforce administration, privacy, data, application, and incident owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce access combines OAuth client policy, user or integration-principal permissions, object CRUD, field-level access, record sharing, org settings, and optional security products. Controls and entitlements must be verified in the target org.

## Authentication

Prefer an External Client App for new REST integrations where the org contract requires it, or govern an approved existing Connected App. Use workload-appropriate OAuth, minimum scopes, protected secret custody, rotation, revocation, and no human-password automation.

## Instructions

1. Map trust boundaries, principals, orgs, APIs, events, data classes, mutations, logs, vendors, and failure paths.
2. Verify app type, OAuth flow, scopes, policies, certificate or secret custody, token lifetime, rotation, and revocation.
3. Review permission sets or groups, profile baseline, CRUD, field access, sharing, elevated access, and separation of duties.
4. Inspect queries, payloads, caches, queues, logs, exports, support bundles, backups, and retention for minimum-data handling.
5. Assess SOQL injection, mass assignment, replay, duplicate mutation, confused-deputy, mixed-org, and secret-exposure threats.
6. Test denied paths, expired and revoked credentials, inaccessible fields, sharing restrictions, redaction, and break-glass audit.
7. Track every gap with severity, owner, deadline, compensating control, verification evidence, and review cadence.

## Approval Boundaries

Do not change app policy, scopes, permissions, sharing, encryption, retention, or monitoring without security, admin, privacy, and data-owner approval.

## Output

Return the threat model, access matrix, control evidence, denied-path tests, gaps, compensating controls, rotation and revocation proof, and owners.

## Error Handling

| Condition | Response |
|---|---|
| Administrator access masks a denied path | Repeat with the actual integration principal before accepting the control. |
| Security product or event is not entitled | Record the boundary and choose a documented compensating control. |
| Credential exposure is suspected | Revoke and rotate through the incident process before further testing. |

## Example

A redacted completion receipt might look like this:

```text
integration=orders; app=external-client-app; scopes=minimum; crud-fls=verified; sharing=verified; denied-tests=pass; gaps=2-owned
```

## Resources

- [REST OAuth authorization](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)
- [Salesforce Security Implementation Guide](https://developer.salesforce.com/docs/atlas.en-us.securityImplGuide.meta/securityImplGuide/)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
