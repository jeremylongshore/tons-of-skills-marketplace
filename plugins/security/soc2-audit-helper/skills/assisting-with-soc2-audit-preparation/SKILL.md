---
name: assisting-with-soc2-audit-preparation
description: 'Execute automate SOC 2 audit preparation including evidence gathering,
  control assessment, and compliance gap identification.

  Use when you need to prepare for SOC 2 audits, assess Trust Service Criteria compliance,
  document security controls, or generate readiness reports.

  Trigger with phrases like "SOC 2 audit preparation", "SOC 2 readiness assessment",
  "collect SOC 2 evidence", or "Trust Service Criteria compliance".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(audit-collect:*), Bash(compliance-check:*)
version: 1.31.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- security
- compliance
- audit
compatibility: Designed for Claude Code
---
# Assisting With SOC 2 Audit Preparation

## Overview

Automate SOC 2 Type I and Type II audit preparation by assessing controls across the five AICPA Trust Service Criteria (Security, Availability, Processing Integrity, Confidentiality, Privacy). Inventory existing controls and evidence, perform gap analysis against each Common Criteria point (CC1-CC9), and produce an audit-ready evidence package with a readiness score and remediation backlog.

## Prerequisites

- Policy and procedure documentation accessible in `${CLAUDE_SKILL_DIR}/docs/` (information security policy, incident response plan, BCP/DR plan, vendor management procedures)
- Infrastructure-as-code and configuration files available for control verification
- Cloud provider audit logs accessible (AWS CloudTrail, Azure Activity Log, GCP Audit Logs) or exported
- Employee onboarding/offboarding and security awareness training records available
- Change management and access review logs accessible
- Write permissions for audit workspace in `${CLAUDE_SKILL_DIR}/soc2-audit/`

## Instructions

1. **Define audit scope**: confirm in-scope services, systems, data stores, and audit period (Type I: point-in-time; Type II: observation window, typically 3-12 months). Identify applicable Trust Service Categories beyond the required Security criteria.
2. **Assess CC1 -- Control Environment**: verify organizational structure documentation, security policy, board oversight, and security role/responsibility matrix. Check for gaps in documented accountability.
3. **Assess CC6 -- Logical and Physical Access Controls**: verify MFA implementation, RBAC policies, password policy enforcement, access review cadence, and automated deprovisioning. Flag privileged access without monitoring.
4. **Assess CC7 -- System Operations**: check monitoring and alerting configurations, backup procedures and testing records, incident response logs, and capacity planning documentation.
5. **Assess CC8 -- Change Management**: review change approval workflows, deployment pipelines, rollback procedures, and change logs for the audit period.
6. **Collect evidence artifacts**: organize evidence into the standard directory structure under `${CLAUDE_SKILL_DIR}/soc2-audit/` with subdirectories per criteria (CC1-control-environment/, CC6-access-controls/, CC7-system-operations/, etc.).
7. **Test control effectiveness**: for each control, verify design adequacy (properly designed?) and operating effectiveness (working as intended during the audit period?). Document test results with screenshots, log excerpts, or configuration exports.
8. **Perform gap analysis**: classify findings as missing controls (critical gap), partially implemented controls (needs improvement), improperly documented controls (evidence gap), or ineffective controls (design/operating failure).
9. **Generate readiness report**: produce `${CLAUDE_SKILL_DIR}/soc2-audit/readiness-report-YYYYMMDD.md` with overall readiness score, per-criteria assessment with percentage, remediation roadmap with timelines, and evidence collection checklist.
10. **Prepare auditor interview guide**: draft expected auditor questions by criteria area with suggested evidence references and talking points.

See [`references/implementation.md`](references/implementation.md) for the six-phase implementation guide. See [`references/readiness-by-trust-service-category.md`](references/readiness-by-trust-service-category.md) for example per-criteria readiness breakdowns.

## Output

- **Readiness Report**: `${CLAUDE_SKILL_DIR}/soc2-audit/readiness-report-YYYYMMDD.md` with overall score and per-criteria pass/gap status
- **Evidence Inventory**: organized artifact list mapped to specific CC control points
- **Gap Analysis**: missing and partially implemented controls with severity and remediation priority
- **Remediation Backlog**: prioritized tasks with effort estimates, owners, and target dates
- **Auditor Interview Guide**: expected questions by criteria with evidence pointers

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Cannot locate security policy in `${CLAUDE_SKILL_DIR}/docs/` | Documentation stored elsewhere or not yet created | Request document locations; flag as critical evidence gap requiring immediate creation |
| Log retention < SOC 2 requirement (1 year) | Insufficient log retention configuration | Note current retention period; flag as gap; recommend extending to 12+ months |
| No incident response playbook found | Undocumented procedure | Flag as critical gap; provide template for creating IR playbook |
| Cannot assess cloud controls without API access | No CloudTrail/Audit Log exports available | Request console screenshots or JSON exports as alternative evidence |
| Production and dev configs mixed in `${CLAUDE_SKILL_DIR}/` | Environment separation unclear | Request environment labeling; risk of auditing wrong environment |

## Examples

- "Prepare a SOC 2 evidence checklist for Security and Availability criteria for production systems."
- "Generate a readiness gap analysis with remediation backlog for SOC 2 Type II, covering CC1 through CC9."
- "Assess CC6 access control compliance: verify MFA, RBAC, deprovisioning, and privileged access monitoring."

## Resources

- AICPA Trust Service Criteria (2017):
- SOC 2 Compliance Checklist:
- CIS Controls v8: https://www.cisecurity.org/controls/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- [`references/readiness-by-trust-service-category.md`](references/readiness-by-trust-service-category.md) -- example per-criteria readiness breakdown
- [`references/errors.md`](references/errors.md) -- full error handling reference
- [`references/examples.md`](references/examples.md) -- additional usage examples
- https://intentsolutions.io
