---
name: workhuman-common-errors
description: 'Triage Workhuman identity, eligibility, approval, spend, integration, reporting, and redemption failures using tenant evidence. Use when diagnosing operations. Trigger with "diagnose a Workhuman error".'
argument-hint: "[symptom] [tenant-or-integration]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, troubleshooting, recognition, integrations]
model: inherit
effort: high
compatibility: Designed for Claude Code; remediation that changes identity, worker, recognition, award, spend, or connector state requires owner approval
---
# Workhuman Failure Triage

## Overview

Classify failures by evidence and authoritative system before changing configuration or retrying potentially consequential recognition and award operations.

## Prerequisites

- Failure time, tenant, actor or principal class, operation, environment, and safe correlation identifier
- Current tenant contract, program rules, field authority map, and recent change history
- Owners for identity, HCM, recognition, payroll, security, and vendor support

## Tool Discipline

Use `Read`, `Glob`, and `Grep` for sanitized logs and configuration, `WebFetch` for current first-party context, and `Write` or `Edit` only for redacted timelines, hypotheses, fixtures, and approved repairs.

## Current Contract

Workhuman spans customer identity, workforce data, recognition policy, award approval and spend, Store redemption, reporting, and managed integrations. A visible symptom can originate in another authority; public pages do not define a universal HTTP error map.

## Authentication

Confirm which principal failed and whether its authorization applies to the tenant, environment, data direction, and operation. Never test by borrowing a more privileged user session.

## Instructions

1. Freeze the timeline, impact, last known success, recent changes, and whether any write may have partially applied.
2. Sanitize evidence while preserving status, safe error class, correlation identifier, timestamps, and contract version.
3. Classify the failure as identity, entitlement, worker authority, eligibility, approval, spend, financial handling, schema, capacity, delivery, reporting, redemption, or vendor service.
4. Compare actual behavior with the current authorized contract and customer program configuration.
5. Reproduce with a synthetic fixture in the smallest non-production scope; do not replay an ambiguous write.
6. Test one hypothesis at a time and name the system and owner authorized to resolve it.
7. Present the repair, affected records, risk, verification, rollback, and approval boundary.
8. After approval, apply the narrow repair and reconcile both expected and actual state.

## Approval Boundaries

Do not change SSO, privileges, workers, recognition policy, awards, balances, payroll mappings, integrations, or production records during diagnosis.

## Output

Return the sanitized timeline, classification, contract evidence, reproduction result, root cause or ranked hypotheses, repair preview, approver, and reconciliation receipt.

## Error Handling

| Condition | Response |
|---|---|
| Write outcome is ambiguous | Quarantine retries and reconcile with the authoritative system first. |
| Evidence conflicts with the contract | Preserve both and escalate as contract or service drift. |
| Personal data is present in logs | Restrict and redact the bundle before sharing or retaining it. |

## Example

A redacted completion receipt might look like this:

```text
symptom=award-not-in-payroll; class=integration-mapping; source=workhuman; target=workday; records=3-held; repair=previewed; owner=payroll
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)

## Next Steps

Convert confirmed incidents into regression fixtures and review whether monitoring or ownership must change.
