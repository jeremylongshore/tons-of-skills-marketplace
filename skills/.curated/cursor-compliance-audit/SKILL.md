---
name: cursor-compliance-audit
description: 'Compliance and security auditing for Cursor IDE usage: SOC 2, GDPR,
  HIPAA assessment, evidence

  collection, and remediation. Triggers on "cursor compliance", "cursor audit", "cursor
  security review",

  "cursor soc2", "cursor gdpr", "cursor data governance".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- security
- compliance
- audit
compatibility: Designed for Claude Code
---
# Cursor Compliance Audit

## Overview

Assess a Cursor deployment against approved privacy, identity, source-code, and audit controls. This is an evidence-backed configuration review, not legal certification.

## Prerequisites

- A named system owner, applicable controls, and authority to inspect tenant settings.
- Read-only admin evidence, current access roster, and redaction rules for audit artifacts.
- Legal/compliance review for regulated data, customer commitments, or PHI/PCI scope.

## Instructions

1. Define the tenant, repositories, data classes, and control period in scope.
2. Compare privacy, retention, identity, access review, and `.cursorignore` settings to the approved baseline.
3. Record findings with evidence, owner, severity, due date, and verification method.
4. Escalate suspected sensitive-code exposure before broad configuration changes.

Compliance and security auditing framework for Cursor IDE usage. Covers SOC 2, GDPR, and HIPAA assessment with audit checklists, evidence collection, and remediation guidance.

## Cursor Security Posture

### Certifications and Attestations

| Certification | Status | Notes |
|--------------|--------|-------|
| SOC 2 Type II | Certified | Annual audit, report available on request |
| Penetration testing | Annual | Results shared under NDA (Enterprise) |
| Encryption at rest | AES-256 | All stored data |
| Encryption in transit | TLS 1.2+ | All API communications |
| Zero data retention | Available | Via Privacy Mode |
| GDPR compliance | Yes | EU data processing supported |
| HIPAA BAA | Not available (as of early 2026) | See HIPAA section |

### Data Processing Architecture

```
Developer Machine
    │
    ├─► Cursor Client ──► Cursor API (US/EU) ──► Model Provider
    │   (local)           (routing + auth)        (OpenAI/Anthropic)
    │                           │
    │                           └─► Zero retention agreement
    │
    ├─► Codebase Index ──► Embedding API ──► Turbopuffer (vectors)
    │                      (no plaintext stored)
    │
    └─► Local Settings (API keys, preferences)
        (never transmitted)
```

## Audit Checklist: SOC 2

### CC6.1 — Logical Access Controls

```
[ ] SSO (SAML/OIDC) configured and enforced
[ ] MFA enabled at Identity Provider level
[ ] RBAC roles assigned: Owner, Admin, Member
[ ] Inactive users deprovisioned (SCIM or manual)
[ ] Access review completed (quarterly)

Evidence:
  - SSO configuration screenshot from admin dashboard
  - IdP MFA policy documentation
  - User list export from Cursor admin
  - SCIM sync logs (if applicable)
```

### CC6.6 — System Boundaries

```
[ ] Privacy Mode enforced at team level
[ ] .cursorignore configured for sensitive files
[ ] Data classification aligned with .cursorignore patterns
[ ] Model provider data retention agreements documented
[ ] BYOK configuration documented (if applicable)

Evidence:
  - Privacy Mode enforcement screenshot
  - .cursorignore file contents (committed to git)
  - Cursor data use policy acceptance
  - API key provider agreements
```

### CC6.7 — Data Transmission Security

```
[ ] All Cursor API calls use TLS 1.2+
[ ] Corporate proxy configured with valid certificates
[ ] No self-signed certificates or TLS bypasses
[ ] Network firewall rules documented

Evidence:
  - Network architecture diagram showing Cursor data flows
  - Firewall rules for cursor.com domains
  - Proxy configuration settings
```

### CC7.2 — Monitoring

```
[ ] Admin dashboard usage analytics reviewed monthly
[ ] Anomalous usage patterns investigated
[ ] Seat utilization tracked for access reviews

Evidence:
  - Monthly usage report screenshots
  - Incident response log for anomalies
  - User activity summary
```

## Audit Checklist: GDPR

### Data Mapping

```
Data Category: Source code snippets
Processing Purpose: AI-assisted code generation
Legal Basis: Legitimate interest (developer productivity)
Data Location: In-transit only (zero retention with Privacy Mode)
Sub-processors: OpenAI, Anthropic, Turbopuffer (embeddings)
Retention: None (Privacy Mode) or per provider policy (no Privacy Mode)
```

### Individual Rights

| Right | Cursor Support |
|-------|---------------|
| Right to access | Account settings at cursor.com/settings |
| Right to erasure | Account deletion removes all server-side data |
| Right to portability | Settings export (settings.json) |
| Right to restriction | Privacy Mode limits processing |
| Right to object | Privacy Mode + .cursorignore |

### GDPR Compliance Checklist

```
[ ] Data Processing Agreement (DPA) signed with Cursor (Enterprise)
[ ] Privacy Mode enabled for all EU team members
[ ] Sub-processor list reviewed (cursor.com/privacy)
[ ] Data protection impact assessment (DPIA) completed
[ ] Team briefed on not pasting PII into Chat/Composer

Evidence:
  - Signed DPA
  - Privacy Mode enforcement confirmation
  - DPIA document
  - Team training records
```

## HIPAA Assessment

**Current status:** Cursor does not offer a Business Associate Agreement (BAA) as of early 2026.

### Mitigations for Healthcare Organizations

```
If your organization handles PHI:

1. Enable Privacy Mode (mandatory)
2. Configure .cursorignore to exclude ALL PHI-containing files:
   .cursorignore:
     **/patient-data/
     **/medical-records/
     **/hl7/
     **/fhir-resources/
     **/*.hl7
     **/*.ccda

3. Consider BYOK through Azure with BAA:
   - Azure OpenAI has HIPAA BAA option
   - Route Cursor AI requests through Azure
   - Azure handles data governance

4. Train developers: NEVER paste PHI into Chat or Composer
5. Code review policy: verify no PHI in AI-generated code

6. CRITICAL: Consult your compliance team before any Cursor
   usage with systems that process PHI
```

## Remediation Playbook

### Finding: Privacy Mode Not Enforced

```
Severity: High
Risk: Code may be retained by model providers for training

Remediation:
1. Admin Dashboard > Privacy > Enable enforcement (immediate)
2. Notify all team members (email)
3. Verify enforcement: check each member's status in dashboard
4. Document: date of enforcement, approval authority
```

### Finding: No .cursorignore

```
Severity: Medium
Risk: Sensitive files may be included in AI context

Remediation:
1. Create .cursorignore at project root
2. Add patterns for: .env*, secrets/, credentials/, PII directories
3. Commit to git (PR review required)
4. Verify: Cursor Settings > Codebase Indexing > View included files
5. Confirm sensitive files absent from indexed list
```

### Finding: Unmanaged API Keys (BYOK)

```
Severity: Medium
Risk: Shared or unrotated API keys

Remediation:
1. Audit which team members use BYOK keys
2. Verify keys are personal (not shared team keys)
3. Implement quarterly key rotation schedule
4. Document key management policy
5. Consider centralizing through Azure gateway (Enterprise)
```

### Finding: No Access Review

```
Severity: Medium
Risk: Former employees retaining Cursor access

Remediation:
1. Export current member list from admin dashboard
2. Cross-reference with HR active employee list
3. Deactivate accounts for departed employees
4. Enable SCIM for automatic deprovisioning
5. Schedule quarterly access reviews
```

## Enterprise Considerations

- **SOC 2 report**: Request directly from Cursor (Enterprise plan) or via your account manager
- **Vendor risk assessment**: Use Cursor's security page (cursor.com/security) as starting input
- **Third-party audit**: Cursor's SOC 2 report covers their controls; your audit covers your configuration
- **Continuous monitoring**: Set calendar reminders for quarterly access reviews and annual policy updates

## Output

- A dated audit record with redacted evidence and control-by-control status.
- A remediation register with owners, deadlines, and verification criteria.

## Error Handling

| Condition | Safe response |
|---|---|
| Admin evidence is incomplete | Mark the control unverified; do not infer compliance from plan level or screenshots alone. |
| Sensitive code may have been exposed | Activate the incident process, restrict evidence distribution, and consult security/privacy owners. |
| A policy conflicts with tenant configuration | Keep the restrictive policy in effect and escalate for a documented decision. |

## Examples

For a privacy-mode control, capture the enforced tenant setting and a sampled member status, redact personal identifiers, and record the reviewer and date. If enforcement is absent, create a high-severity finding, assign the tenant admin, and verify again after the approved change.

## Resources

- [Cursor Security](https://cursor.com/security)
- [Cursor Data Use Policy](https://cursor.com/data-use)
- [Cursor Privacy Policy](https://cursor.com/privacy)
- [Privacy and Data Governance Docs](https://docs.cursor.com/enterprise/privacy-and-data-governance)
