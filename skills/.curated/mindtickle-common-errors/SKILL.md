---
name: mindtickle-common-errors
description: 'Triage Mindtickle access, provisioning, content, assignment, reporting, and managed-integration failures using evidence and ownership boundaries. Use when an incident or rollout fails. Trigger with "triage Mindtickle failure".'
argument-hint: "[incident-id] [symptom]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, troubleshooting, incident-response, support]
model: inherit
effort: medium
compatibility: Designed for Claude Code; production changes and vendor escalation require incident-owner approval
---
# Evidence-First Mindtickle Failure Triage

## Overview

Classify a failure by boundary, protect learner data, and produce the smallest reversible diagnosis before changing tenant state.

## Prerequisites

- An incident owner, affected tenant, time window, population, and business impact
- The last known-good state and recent changes across identity, content, data, and integrations
- Approved access to redacted application and tenant evidence

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local logs and configuration, `WebFetch` for current official and authorized tenant guidance, and `Write` or `Edit` for a sanitized timeline and support packet.

## Current Contract

Failures can cross customer identity providers, user sync, tenant roles, subscribed modules, managed connectors, customer adapters, and Mindtickle service boundaries. HTTP status alone does not prove root cause, and public material does not define universal error payloads.

## Authentication

Use the least-privilege diagnostic principal. Redact tokens, cookies, personal data, assessment results, content URLs, and confidential tenant artifacts before sharing evidence.

## Instructions

1. Freeze the symptom, first occurrence, blast radius, expected behavior, request or job identifiers, and recent changes.
2. Determine whether the failure is interactive access, provisioning, entitlement, content, assignment, reporting, connector, adapter, or platform availability.
3. Compare one failing case with one known-good case while changing only one variable at a time.
4. Validate tenant, principal, role, environment, contract digest, input identity, timestamps, and source-system state.
5. Check official service and support information, then distinguish customer-controlled remediation from vendor escalation.
6. Propose the smallest reversible repair with preview, approver, rollback, and post-change verification.
7. Reconcile the full affected set after repair; do not close on one successful sample.

## Approval Boundaries

Do not reset identity settings, re-provision populations, republish content, edit scores, replay writes, or disable controls during diagnosis without the responsible owner.

## Output

Return the timeline, impact, boundary classification, evidence table, ruled-out causes, proposed repair, approval requirement, verification, and support escalation packet.

## Error Handling

| Condition | Response |
|---|---|
| Evidence contains sensitive data | Stop distribution, redact it, and rotate any exposed credential. |
| Ownership boundary is unclear | Pause changes and assign customer and vendor owners in the incident record. |
| Platform incident is suspected | Preserve corroborating timestamps and use the contracted support channel and severity. |

## Example

```text
incident=INC-1042; impact=27-users; boundary=user-sync; change=attribute-map-v4; repair=rollback-proposed; vendor-ticket=not-yet-needed
```

## Resources

- [Mindtickle Support Services](https://www.mindtickle.com/legal/support-services/)
- [Mindtickle Service Level Agreement](https://www.mindtickle.com/legal/service-level-agreement/)

## Next Steps

Attach the sanitized evidence to the incident and convert the root cause into a regression fixture.
