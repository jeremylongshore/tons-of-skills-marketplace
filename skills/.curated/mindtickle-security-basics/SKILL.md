---
name: mindtickle-security-basics
description: 'Threat-model and harden a Mindtickle tenant and its identity, connector, API, content, and reporting integrations. Use when conducting security review or control remediation. Trigger with "secure Mindtickle integration".'
argument-hint: "[scope] [evidence-period]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, security, privacy, threat-modeling]
model: inherit
effort: high
compatibility: Designed for Claude Code; tenant, identity, data, credential, and security-control changes require their respective owners
---
# Mindtickle Security and Privacy Control Review

## Overview

Translate shared responsibility into testable controls for identities, tenant boundaries, employee data, content, integrations, evidence, and incident response.

## Prerequisites

- A scoped architecture, data inventory, identity model, contract registry, and accountable owners
- Current customer policy, threat model, retention schedule, and incident process
- Authorized access to Mindtickle trust artifacts and tenant-specific security documentation

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect configuration and evidence, `WebFetch` for current official security material, and `Write` or `Edit` for the threat model, control matrix, and sanitized findings.

## Current Contract

Mindtickle describes role-based access, customer responsibility for SSO, roles, provisioning, and data lifecycle, plus independent compliance and security assessments. Certifications inform assurance but do not replace customer control validation.

## Authentication

Separate users, administrators, provisioning identities, managed connectors, API principals, and support access. Require least privilege, phishing-resistant identity controls where available, rotation, revocation, access review, and no shared credentials.

## Instructions

1. Inventory tenants, environments, principals, roles, integrations, data classes, content audiences, exports, caches, logs, and support paths.
2. Map threats across account takeover, overprivilege, tenant misrouting, lifecycle drift, data leakage, malicious content, replay, schema injection, and compromised dependencies.
3. Verify SSO enforcement, identity-provider MFA, provisioning ownership, disabled-user handling, administrator separation, and periodic access review.
4. Test tenant binding, input and output validation, secret handling, egress restrictions, encryption, logging redaction, and evidence integrity.
5. Review data minimization, retention, deletion, exports, residency commitments, learner transparency, and restricted assessment or coaching data.
6. Validate connector and adapter scopes, contract provenance, dependency controls, incident contacts, support disclosure, and credential compromise response.
7. Rank findings by exploitable path and business impact; assign owner, remediation, verification, and due date.
8. Re-test changed controls and preserve redacted evidence rather than closing on configuration screenshots alone.

## Approval Boundaries

Do not weaken SSO, grant roles, rotate production credentials, access learner records, change retention, or conduct intrusive testing without explicit authorization.

## Output

Return the asset and data inventory, trust boundaries, threat model, control evidence, findings, owners, remediation dates, residual risks, and re-test results.

## Error Handling

| Condition | Response |
|---|---|
| A secret appears in evidence | Restrict access, remove it, rotate as required, and regenerate the artifact. |
| Tenant-specific assurance is unavailable | Record the gap and request it through the authorized trust or commercial channel. |
| A critical control fails | Stop affected integration activity and invoke the incident process. |

## Example

```text
scope=reporting-adapter; principals=3-owned; tenant-binding=pass; pii-logs=none; findings=1-high,2-medium; retest=scheduled
```

## Resources

- [Mindtickle Trust](https://www.mindtickle.com/trust/)
- [Mindtickle compliance](https://www.mindtickle.com/trust/compliance/)
- [Mindtickle Support Services](https://www.mindtickle.com/legal/support-services/)

## Next Steps

Track remediation to evidence-backed closure and schedule the next access and contract review.
