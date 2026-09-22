---
name: salesforce-debug-bundle
description: 'Build a privacy-safe Salesforce support bundle with request, limits, metadata, job, event, and change evidence. Use when escalating an integration defect. Trigger with "build a Salesforce debug bundle".'
argument-hint: "[incident-id] [output-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, support, diagnostics, redaction]
model: inherit
effort: high
compatibility: Designed for Claude Code; debug logs, event records, and org metadata require explicit support and data-owner authorization
---
# Privacy-Safe Salesforce Support Evidence Bundle

## Overview

Collect the smallest reproducible evidence set while excluding credentials, raw business records, personal data, and unrelated org configuration.

## Prerequisites

- Incident identifier, time window, environment, affected operation, and support destination
- Approved evidence classes, redaction policy, retention period, and transfer channel
- Read-only access to the specific limits, metadata, job, event, or log evidence required

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce diagnostic surfaces vary by product, edition, permission, and entitlement. Limits can be read through the versioned REST resource, while debug logs, Event Monitoring, async jobs, and event metrics require separate access and interpretation.

## Authentication

Use a dedicated read-only diagnostic principal where possible. Never include access or refresh tokens, session IDs, cookies, authorization headers, client secrets, private keys, usernames, org IDs unless approved, or raw record payloads.

## Instructions

1. Create a manifest naming incident, time window, environment class, components, evidence owners, retention, and recipient.
2. Collect application version, dependency lock, API version, redacted request ID, status, timing, retry history, and recent deployment IDs.
3. Add only relevant limits, object metadata fingerprints, async job summaries, event channel metrics, and log excerpts.
4. Replace record IDs, user IDs, org IDs, domains, field values, queries, and payloads with stable redaction tokens where required.
5. Scan the bundle for credentials, authorization material, personal data, customer names, and unrelated records.
6. Generate hashes and a manifest, then have the incident and data owners review the exact archive.
7. Transfer through the approved support channel, record receipt, expiry, and deletion responsibility.

## Approval Boundaries

Do not enable broad tracing, extend log retention, retrieve EventLogFile content, export records, or send an archive without support, security, and data-owner approval.

## Output

Return the redacted manifest, evidence inventory, collection gaps, hashes, reviewer approvals, transfer receipt, retention deadline, and deletion owner.

## Error Handling

| Condition | Response |
|---|---|
| Required evidence is not entitled or permitted | Record the gap and ask Salesforce Support for an approved alternative. |
| Secret or personal data is detected | Block transfer, remove the material, rotate exposed credentials if necessary, and rescan. |
| Bundle cannot reproduce the timeline | Do not add broad data; refine the time window and correlation identifiers. |

## Example

A redacted completion receipt might look like this:

```text
incident=SF-204; window=30m; files=7; records=0; secrets=0; pii=tokenized; hash=recorded; expiry=14d
```

## Resources

- [Limits REST resource](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-limits.html)
- [EventLogFile object](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_eventlogfile.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
