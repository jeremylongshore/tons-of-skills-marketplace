---
name: performing-security-code-review
description: 'Execute this skill enables AI assistant to conduct a security-focused
  code review using the security-agent plugin. it analyzes code for potential vulnerabilities
  like sql injection, xss, authentication flaws, and insecure dependencies. AI assistant
  uses this skill wh... Use when assessing security or running audits. Trigger with
  phrases like ''security scan'', ''audit'', or ''vulnerability''.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(cmd:*)
version: 1.29.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- example
- security
- authentication
- audit
compatibility: Designed for Claude Code
---
# Performing Security Code Review

## Overview

Conducts security-focused code reviews by scanning source files for common vulnerability patterns including SQL injection, XSS, authentication flaws, insecure dependencies, and secret exposure. Produces structured severity-rated reports with specific remediation guidance.

## Prerequisites

- Read access to all source files in the target project
- `grep` available on PATH for pattern matching
- Access to `package.json` or equivalent dependency manifest for dependency auditing
- Familiarity with OWASP Top 10 vulnerability categories

## Instructions

1. Identify the scope of the review: specific files, directories, or the entire codebase. Confirm the primary language(s) and framework(s) in use.
2. Scan for hardcoded secrets and credentials:
   - Search for patterns matching API keys, tokens, passwords, AWS access keys (`AKIA...`), and private key headers (`BEGIN PRIVATE KEY`).
   - Flag any `.env` files or configuration files containing plaintext secrets.
3. Analyze code for injection vulnerabilities:
   - Identify raw SQL string concatenation (SQL injection risk).
   - Locate unsanitized user input rendered in HTML (XSS risk).
   - Check for `eval()`, `exec()`, or `Function()` calls with dynamic input (code injection risk).
4. Review authentication and authorization logic:
   - Verify password hashing uses strong algorithms (bcrypt, argon2) rather than MD5/SHA1.
   - Check for missing authentication on sensitive endpoints.
   - Identify overly permissive CORS configurations.
5. Audit dependencies for known vulnerabilities:
   - Run `npm audit` or equivalent package manager audit command.
   - Cross-reference dependency versions against known CVE databases.
6. Check for insecure communication patterns:
   - Flag HTTP URLs where HTTPS is expected.
   - Identify disabled TLS certificate verification.
7. Compile findings into a structured report sorted by severity (Critical, High, Medium, Low), including the vulnerable code location, explanation, and remediation steps.

## Output

A structured security review report containing:

- Summary with total findings count by severity level
- Per-finding entries with: file path, line number, vulnerability type, severity, code snippet, explanation, and recommended fix
- Dependency audit results with CVE identifiers where applicable
- Overall risk assessment (Critical / High / Medium / Low / Clean)

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| No source files found | Incorrect scope path or empty directory | Verify the target directory path and confirm it contains source files |
| Binary files in scan | Non-text files matched by search patterns | Exclude binary extensions and `node_modules/` from scans |
| Dependency manifest missing | No `package.json`, `requirements.txt`, or equivalent | Skip dependency audit; note in report that dependency analysis was not possible |
| Permission denied on files | Restricted file access | Request read permissions or narrow the review scope to accessible files |
| False positive on secret pattern | Benign string matching secret regex | Verify context before reporting; mark as potential false positive if the match appears in test fixtures or documentation |

## Examples

**SQL injection review:**
Trigger: "Review this database query code for SQL injection vulnerabilities."
Process: Scan all files containing SQL query construction. Identify string concatenation with user input (`"SELECT * FROM users WHERE id = " + userId`). Report as High severity with remediation: use parameterized queries or prepared statements.

**Dependency vulnerability scan:**
Trigger: "Check this project's dependencies for known security vulnerabilities."
Process: Run `npm audit` on the project. Parse output for vulnerabilities. Report each finding with CVE identifier, affected package, installed version, and patched version. Recommend `npm audit fix` or manual version pinning.

**Full codebase security audit:**
Trigger: "Run a security scan on this codebase."
Process: Execute all seven scan categories (secrets, injection, auth, dependencies, communication, dangerous commands, obfuscation). Produce a comprehensive report with findings grouped by category and sorted by severity.

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) -- industry-standard vulnerability classification
- [Node.js Security Checklist](https://blog.risingstack.com/node-js-security-checklist/) -- Node-specific security guidance
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/) -- most dangerous software weaknesses
- [`references/README.md`](references/README.md) -- bundled reference materials
