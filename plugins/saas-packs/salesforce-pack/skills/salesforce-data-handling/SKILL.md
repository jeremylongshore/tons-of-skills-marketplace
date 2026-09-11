---
name: salesforce-data-handling
description: 'Review Salesforce data classification, minimum access, extraction, transformation, retention, subject requests, deletion, legal hold, and evidence. Use when operating privacy-sensitive workflows. Trigger with "review Salesforce data handling".'
argument-hint: "[org-alias] [dataset-or-object]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, privacy, data-governance, retention]
model: inherit
effort: high
compatibility: Designed for Claude Code; personal-data access, export, retention, correction, and deletion require privacy, legal, security, and data-owner approval
---
# Salesforce Data Handling and Privacy Operations

## Overview

Translate policy and legal obligations into object- and field-level controls without treating one Salesforce feature or object as automatic compliance.

## Prerequisites

- Dataset, objects, fields, data subjects, purposes, jurisdictions, systems of record, recipients, and owners
- Current object metadata, CRUD and field access, sharing, encryption, retention, audit, export, and deletion capabilities
- Privacy policy, legal basis, subject-request process, legal holds, incident process, and evidence requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce provides data, security, privacy, encryption, and metadata capabilities that vary by product and entitlement. The Individual object can support privacy use cases where enabled, but its presence alone does not prove GDPR, CCPA, retention, or subject-request compliance.

## Authentication

Use minimum object, field, record, and export access for the approved purpose. Separate administrators, privacy operators, integration principals, and support access; never place tokens or raw personal data in fixtures, logs, or receipts.

## Instructions

1. Map objects and fields to data classes, purposes, legal bases, subjects, sources of truth, recipients, residency, retention, and owners.
2. Discover current metadata, permissions, sharing, encryption, audit, Individual-object or alternative mapping, and downstream copies.
3. Minimize selected fields and rows, parameterize queries, redact logs, encrypt transport and storage, and restrict exports.
4. Define correction, access, portability, restriction, deletion, anonymization, and legal-hold actions across every authoritative and copied system.
5. Use stable case identifiers and approval gates; never assume deleting one Salesforce record satisfies a multi-system request.
6. Test the workflow with synthetic subjects, inaccessible fields, holds, duplicates, relationships, events, backups, and failures.
7. Execute approved cases, reconcile every system and exception, retain minimum evidence, and delete temporary exports on schedule.

## Approval Boundaries

Do not export, disclose, correct, merge, anonymize, delete, unencrypt, shorten retention, or override a legal hold without accountable approval.

## Output

Return the data map, control and permission evidence, minimum query or export contract, case plan, approvals, system results, exceptions, reconciliation, and expiry.

## Error Handling

| Condition | Response |
|---|---|
| Legal hold conflicts with deletion | Stop deletion and route the case to legal with the held systems identified. |
| Field or copy ownership is unknown | Treat completion as unproven until an owner and disposition are established. |
| Temporary export exceeds approved scope | Quarantine and securely delete it, assess exposure, and regenerate the minimum dataset. |

## Example

A redacted completion receipt might look like this:

```text
case=DSR-88; systems=4; fields=approved-minimum; hold=none; actions=completed; exceptions=0; exports=deleted
```

## Resources

- [Salesforce data protection and privacy](https://help.salesforce.com/s/articleView?id=sf.data_protection_and_privacy.htm)
- [Individual object reference](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_individual.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
