---
name: generating-security-audit-reports
description: 'Generate comprehensive security audit reports for applications and systems.

  Use when you need to assess security posture, identify vulnerabilities, evaluate
  compliance status, or create formal security documentation.

  Trigger with phrases like "create security audit report", "generate security assessment",
  "audit security posture", or "PCI-DSS compliance report".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(security-scan:*), Bash(report-gen:*)
version: 1.29.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- security
- compliance
- audit
compatibility: Designed for Claude Code
---
# Generating Security Audit Reports

## Overview

Aggregate vulnerability scan results, configuration analyses, and compliance assessments into a structured, auditor-ready security report. Map every finding to a CVSS severity, applicable compliance control (PCI-DSS, HIPAA, SOC 2, GDPR), and a prioritized remediation timeline.

## Prerequisites

- Vulnerability scanner outputs (Nmap, Nessus, OpenVAS, OWASP ZAP) available in `${CLAUDE_SKILL_DIR}/security/`
- Application and infrastructure configuration files accessible
- SAST/DAST tool results (e.g., Semgrep, Snyk, Trivy, Bandit)
- Applicable compliance framework documentation identified (PCI-DSS v4.0, HIPAA Security Rule, SOC 2 TSC, GDPR)
- Write permissions for report output directory `${CLAUDE_SKILL_DIR}/reports/`

## Instructions

1. Inventory all available security data sources by scanning `${CLAUDE_SKILL_DIR}/security/` for scanner outputs, log files, and configuration exports.
2. Parse vulnerability findings and normalize severity using CVSS 3.1 base scores: Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.1-3.9).
3. Cross-reference each finding against applicable compliance controls. Map to specific PCI-DSS requirements (e.g., Req 6.5 for injection flaws), HIPAA safeguards, or SOC 2 Common Criteria.
4. Deduplicate findings across scanners and merge related vulnerabilities into consolidated entries with all affected assets listed.
5. Classify access control weaknesses, encryption gaps, and authentication deficiencies into separate report sections.
6. Generate an executive summary including total findings by severity, overall risk score, and top-5 critical remediation priorities.
7. Build a detailed findings table: finding ID, CWE number, affected component, CVSS score, compliance mapping, remediation steps, and evidence links.
8. Produce a compliance status matrix showing pass/fail/partial for each applicable standard requirement.
9. Create remediation recommendations with effort estimates (hours), priority ranking, and suggested timelines.
10. Format the final report as Markdown to `${CLAUDE_SKILL_DIR}/reports/security-audit-YYYYMMDD.md`. Optionally produce JSON for Jira/ServiceNow import.

See [`references/implementation.md`](references/implementation.md) for the detailed four-phase implementation workflow.

## Output

- **Audit Report**: `${CLAUDE_SKILL_DIR}/reports/security-audit-YYYYMMDD.md` containing executive summary, detailed findings, compliance matrix, and remediation plan
- **Findings JSON**: Machine-readable findings for ticketing system import
- **Compliance Matrix**: Per-requirement pass/fail/partial status for each applicable framework
- **Remediation Backlog**: Prioritized list with effort estimates and owner assignments

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No security scan results found | Scanner outputs missing from `${CLAUDE_SKILL_DIR}/security/` | Specify alternate data source paths or run preliminary scans with `nmap -sV` or `trivy fs .` |
| Cannot assess compliance -- requirements unavailable | Compliance framework checklist not provided | Fall back to OWASP Top 10 and CWE Top 25 as baseline; note limitation in report |
| Permission denied reading config files | Insufficient filesystem access | Request elevated permissions or provide exported configuration snapshots |
| Scan results exceed processing capacity | Thousands of findings from multiple scanners | Process in batches by severity (Critical/High first), then merge |
| Conflicting severity ratings across scanners | Different tools score the same vulnerability differently | Use CVSS 3.1 base score as canonical severity; note discrepancies in appendix |

## Examples

- "Generate a SOC 2 security audit report for the API using scan results in `${CLAUDE_SKILL_DIR}/security/`."
- "Create a PCI-DSS compliance-focused security assessment with a prioritized remediation plan for all Critical and High findings."
- "Produce a HIPAA security audit from the Nessus and Trivy outputs, mapping each finding to the relevant HIPAA safeguard."

## Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CWE Top 25: https://cwe.mitre.org/top25/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- PCI-DSS v4.0 Requirements: https://www.pcisecuritystandards.org/
- CVSS 3.1 Calculator: https://www.first.org/cvss/calculator/3.1
- [`references/errors.md`](references/errors.md) -- full error handling reference
- [`references/examples.md`](references/examples.md) -- additional usage examples
- https://intentsolutions.io
