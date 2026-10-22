---
name: generating-compliance-reports
description: Generate comprehensive compliance reports for security standards. Use
  when creating compliance documentation. Trigger with 'generate compliance report',
  'compliance status', or 'audit compliance'.
version: 1.26.0
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(security:*), Bash(scan:*), Bash(audit:*)
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- security
- compliance
- audit
compatibility: Designed for Claude Code
---
# Generating Compliance Reports

## Overview

Generate structured compliance reports for major security frameworks including
PCI DSS, HIPAA, SOC 2, GDPR, and ISO 27001. This skill scans codebases,
configurations, and infrastructure definitions to assess compliance posture,
maps findings to specific framework controls, and produces audit-ready
documentation with evidence references and gap analysis.

## Prerequisites

- Access to the target codebase, infrastructure configs, and policy documents in `${CLAUDE_SKILL_DIR}/`
- Knowledge of the target compliance framework and its applicable scope
- Standard shell utilities and Grep/Glob available for evidence gathering
- Reference: [`references/README.md`](references/README.md) for PCI DSS guidelines, HIPAA compliance checklist, SOC 2 framework overview, config schema, and API documentation

## Instructions

1. Determine the target compliance framework (PCI DSS, HIPAA, SOC 2, GDPR, ISO 27001, or custom) and identify applicable control domains based on the system under audit.
2. Enumerate the control requirements for the target framework -- for PCI DSS, map the 12 requirements and their sub-controls; for HIPAA, map Administrative, Physical, and Technical Safeguards; for SOC 2, map Trust Services Criteria (CC1-CC9).
3. Scan the codebase for evidence of control implementation: encryption at rest and in transit (TLS configuration, database encryption), access controls (RBAC definitions, IAM policies), logging and monitoring (audit log configuration, SIEM integration), and data retention policies.
4. Evaluate each control as Compliant, Partially Compliant, Non-Compliant, or Not Applicable -- document the evidence file path and line number for each assessment.
5. For Partially Compliant and Non-Compliant controls, describe the specific gap: what is missing, what risk it introduces, and what remediation is required.
6. Calculate an overall compliance score as percentage of applicable controls that are fully compliant.
7. Generate the report with these sections: Executive Summary, Scope and Methodology, Control-by-Control Assessment, Gap Analysis, Risk Rating, Remediation Roadmap with priority and effort estimates, and Evidence Appendix.
8. Write the report to `${CLAUDE_SKILL_DIR}/compliance-report-[framework]-[date].md` using the Write tool.
9. Validate the report against the config schema in [`references/README.md`](references/README.md) if applicable.

## Output

- **Compliance report**: Markdown document with Executive Summary, Scope, Control Assessment (table with Control ID, Description, Status, Evidence, Gap), Risk Rating, and Remediation Roadmap
- **Compliance score**: Percentage of applicable controls rated Compliant, broken down by control domain
- **Gap analysis**: Prioritized list of non-compliant controls with risk impact and remediation effort (high/medium/low)
- **Evidence index**: File paths and line references for each control assessment
- **Remediation roadmap**: Prioritized action items with estimated effort, owner assignment placeholders, and target dates

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Unknown compliance framework requested | Framework not in supported list | Map the custom framework controls manually or select the closest standard framework as a baseline |
| Insufficient evidence for control assessment | Codebase lacks configuration files or documentation | Mark the control as "Evidence Not Available" and recommend documenting the control implementation |
| Mixed framework versions | Codebase references multiple versions of a standard (e.g., PCI DSS 3.2.1 vs 4.0) | Clarify the target version and assess against that version only; note version discrepancies in the report |
| Large codebase scan timeout | Too many files to scan within time limits | Scope the scan to relevant directories (e.g., `src/`, `config/`, `infra/`) and exclude generated code |
| Conflicting control evidence | Different parts of the codebase implement conflicting security policies | Flag as Partially Compliant and document both implementations; recommend standardization |

## Examples

### PCI DSS Compliance Report

Scan an e-commerce application in `${CLAUDE_SKILL_DIR}/` for PCI DSS v4.0 compliance.
Assess Requirement 2 (Apply Secure Configurations) by checking for default
credentials in config files, Requirement 3 (Protect Stored Account Data) by
verifying encryption of cardholder data fields, and Requirement 6 (Develop and
Maintain Secure Systems) by checking dependency vulnerability status. Produce a
report rating each requirement as Compliant/Non-Compliant with file-level evidence.

### HIPAA Technical Safeguards Audit

Evaluate a healthcare application against HIPAA Technical Safeguards. Check
164.312(a)(1) Access Control by reviewing authentication and RBAC implementations,
164.312(e)(1) Transmission Security by verifying TLS 1.2+ enforcement, and
164.312(b) Audit Controls by confirming audit logging captures access to PHI.
Generate a gap analysis with remediation steps for each non-compliant safeguard.

### SOC 2 Type II Readiness Assessment

Assess SOC 2 Trust Services Criteria CC6 (Logical and Physical Access Controls)
and CC7 (System Operations) by scanning for access control policies, change
management procedures, incident response documentation, and monitoring
configurations. Produce a readiness report indicating which criteria need
additional evidence or implementation before a formal SOC 2 audit.

## Resources

- [PCI DSS v4.0 Requirements](https://www.pcisecuritystandards.org/document_library/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- AICPA SOC 2 Trust Services Criteria
- [ISO 27001:2022 Controls](https://www.iso.org/standard/27001)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
