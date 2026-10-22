---
name: scanning-for-data-privacy-issues
description: Scan for data privacy issues and sensitive information exposure. Use
  when reviewing data handling practices. Trigger with 'scan privacy issues', 'check
  sensitive data', or 'validate data protection'.
version: 1.24.0
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(security:*), Bash(scan:*), Bash(audit:*)
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- security
- scanning-data
compatibility: Designed for Claude Code
---
# Scanning for Data Privacy Issues

## Overview

Scan codebases for data privacy violations, PII exposure, and non-compliance
with privacy regulations including GDPR, CCPA, HIPAA, and LGPD. This skill
detects hardcoded personal data, unprotected PII in logs and databases,
missing consent mechanisms, improper data retention, and insufficient
anonymization or pseudonymization of sensitive fields.

## Prerequisites

- Access to the target codebase and configuration files in `${CLAUDE_SKILL_DIR}/`
- Knowledge of the data types processed by the application (PII categories, PHI, financial data)
- Standard shell utilities and Grep/Glob available for pattern matching
- Reference: [`references/README.md`](references/README.md) for scanner API documentation, GDPR compliance guide, and sensitive data pattern definitions

## Instructions

1. Define the PII categories relevant to the application: email addresses, phone numbers, Social Security numbers, credit card numbers, IP addresses, geolocation data, biometric data, health records, and any domain-specific identifiers.
2. Scan source code for hardcoded PII using regex patterns -- detect email patterns (`[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+`), SSN patterns (`\d{3}-\d{2}-\d{4}`), credit card patterns (Luhn-valid 13-19 digit sequences), and phone number patterns. Flag each as CWE-312 (Cleartext Storage of Sensitive Information).
3. Examine logging statements (`console.log`, `logger.info`, `logging.debug`, `Log.d`) for PII field references -- flag any logging of user email, password, token, SSN, or credit card fields as CWE-532 (Insertion of Sensitive Information into Log File), severity high.
4. Analyze database schemas and ORM models for PII fields stored without encryption -- check for columns named `email`, `phone`, `ssn`, `date_of_birth`, `address` that lack encryption-at-rest annotations or transparent data encryption.
5. Review data transmission: verify PII is transmitted over TLS only, check for PII in URL query parameters (visible in server logs and browser history), and flag unencrypted API responses containing sensitive fields.
6. Assess consent management: search for cookie consent implementations, privacy policy links, data processing agreements, and opt-in/opt-out mechanisms. Flag applications collecting PII without documented consent flows as a GDPR Article 6/7 gap.
7. Check data retention: look for automated data deletion jobs, retention policy configurations, and user data export/deletion endpoints (GDPR Article 17 Right to Erasure). Flag absence of retention controls.
8. Evaluate anonymization and pseudonymization: verify that analytics, reporting, and non-production environments use anonymized or pseudonymized data rather than production PII. Flag test fixtures containing real PII.
9. Scan configuration files and environment variables for PII used as defaults, seeds, or test data -- flag hardcoded test emails or phone numbers that match real-world patterns.
10. Classify findings by severity and regulation, produce a data flow diagram identifying where PII enters, is stored, is processed, and exits the system.

## Output

- **PII inventory**: Table of all detected PII types, their locations (file:line), storage mechanism, and encryption status
- **Findings report**: Each finding includes severity, regulation reference (GDPR Article, CCPA Section, HIPAA Rule), CWE reference (CWE-312, CWE-532, CWE-359), affected file, and remediation steps
- **Data flow analysis**: Summary of PII entry points (forms, APIs, imports), processing locations, storage mechanisms, and exit points (exports, API responses, logs)
- **Compliance gap matrix**: GDPR/CCPA/HIPAA requirement mapped to implementation status (Compliant, Gap, Not Applicable)
- **Remediation plan**: Prioritized actions including field encryption, log sanitization, consent implementation, and retention policy setup

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| High false positive rate on PII patterns | Regex patterns matching non-PII strings (e.g., UUIDs matching SSN patterns) | Refine patterns with context-aware checks; filter results by file type and surrounding code context |
| Encrypted PII not detected | Application uses transparent encryption that masks PII at the code level | Check encryption configuration separately; mark encrypted fields as "protected" in the inventory |
| Third-party data processors not visible | PII sent to external services via API calls | Grep for HTTP client calls and map destination URLs; flag external services requiring Data Processing Agreements |
| Large codebase scan timeout | Millions of lines to scan | Scope to high-risk directories first (`src/`, `api/`, `config/`); exclude `node_modules/`, `vendor/`, and build artifacts |
| Test data flagged as PII exposure | Test fixtures use realistic but fake data | Verify test data is synthetic; recommend using obviously fake data (e.g., `test@example.com`) to avoid false positives |

## Examples

### PII in Application Logs

Grep `${CLAUDE_SKILL_DIR}/src/` for logging statements that reference user fields:
`logger.info.*email`, `console.log.*password`, `Log.d.*phone`. Flag each match
as CWE-532, severity high. Recommend implementing a log sanitizer middleware
that redacts PII fields before writing to log output.

### GDPR Data Subject Rights

Scan `${CLAUDE_SKILL_DIR}/src/api/` for endpoints supporting data subject rights: user
data export (`GET /api/users/:id/export`), data deletion (`DELETE /api/users/:id`),
and consent withdrawal. Flag missing endpoints as GDPR Article 15/17/21 gaps,
severity high. Recommend implementing a data subject request handler.

### Credit Card Data in Codebase

Search for credit card number patterns across all source files using
`\b[0-9]{13,19}\b` with Luhn validation context. Check that any payment
processing code uses tokenization rather than storing raw card numbers. Flag
PAN storage as PCI DSS Requirement 3 violation and CWE-312, severity critical.

## Resources

- [GDPR Full Text](https://gdpr-info.eu/)
- [CCPA Official Text](https://oag.ca.gov/privacy/ccpa)
- [OWASP Top 10 Privacy Risks](https://owasp.org/www-project-top-10-privacy-risks/)
- [CWE-312: Cleartext Storage of Sensitive Information](https://cwe.mitre.org/data/definitions/312.html)
- [CWE-532: Insertion of Sensitive Information into Log File](https://cwe.mitre.org/data/definitions/532.html)
