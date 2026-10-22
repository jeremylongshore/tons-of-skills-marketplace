---
name: detecting-sql-injection-vulnerabilities
description: 'Detect and analyze SQL injection vulnerabilities in application code
  and database queries.

  Use when you need to scan code for SQL injection risks, review query construction,
  validate input sanitization, or implement secure query patterns.

  Trigger with phrases like "detect SQL injection", "scan for SQLi vulnerabilities",
  "review database queries", or "check SQL security".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(code-scan:*), Bash(security-test:*)
version: 1.32.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- security
- database
- detecting-sql
compatibility: Designed for Claude Code
---
# Detecting SQL Injection Vulnerabilities

## Overview

Scan application source code for SQL injection vulnerabilities (CWE-89, OWASP A03:2021) by tracing user input from entry points through data flows into database query construction. Detect string concatenation, format string interpolation, and inadequate parameterization across raw SQL, ORM raw query methods, stored procedure calls, and dynamic query builders.

## Prerequisites

- Application source code accessible in `${CLAUDE_SKILL_DIR}/`
- Database query files, ORM models, and repository/DAO layers available
- Framework and language identified (Django, Rails, Express, Spring, Laravel, ASP.NET, Go, etc.)
- Database type known (MySQL, PostgreSQL, SQLite, MSSQL, Oracle) for syntax-specific detection
- Write permissions for reports in `${CLAUDE_SKILL_DIR}/security-reports/`

## Instructions

1. **Discover database interaction code**: search for SQL keywords (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `EXEC`) and ORM raw query methods (`raw()`, `execute()`, `createNativeQuery()`, `$wpdb->query()`) across all source files.
2. **Identify input surfaces**: map all user-controllable data entry points -- HTTP parameters, request bodies, URL path segments, headers, cookies, file uploads, and WebSocket messages.
3. **Trace data flows**: follow each input surface through the code to determine whether user data reaches a SQL query. Flag any path where input is not passed through parameterized query binding.
4. **Detect vulnerable patterns**:
   - String concatenation: `"SELECT * FROM users WHERE id=" + userId`
   - f-string/format interpolation: Python f-strings embedding variables directly into SQL strings
   - Template literals: `` `SELECT * FROM users WHERE id=${req.params.id}` ``
   - ORM raw queries without bindings: `Model.objects.raw("SELECT * FROM t WHERE x='" + val + "'")`
5. **Classify each finding**: assign CVSS 3.1 score, identify attack type (classic injection, blind boolean/time-based, UNION-based exfiltration, second-order/stored injection), and document exploitability (authentication required, network access).
6. **Assess impact per finding**: determine data exposure scope (authentication bypass, data exfiltration, data modification, OS command execution via `xp_cmdshell` or `LOAD_FILE()`).
7. **Generate remediation code**: provide parameterized equivalents for each vulnerable query. Use framework-idiomatic patterns -- `%s` placeholders for Python DB-API, `?` for Node.js, `$1` for PostgreSQL, named parameters for Spring JPA.
8. **Recommend defense-in-depth measures**: input validation (allowlists over denylists), stored procedures with parameterized calls, least-privilege database accounts, WAF rules, and ORM-only data access policies.
9. **Produce the vulnerability report** at `${CLAUDE_SKILL_DIR}/security-reports/sqli-scan-YYYYMMDD.md` with per-finding severity, CWE-89 mapping, file path and line number, vulnerable code snippet, attack vector demonstration, and remediated code.

See [`references/implementation.md`](references/implementation.md) for the detection pattern library. See [`references/critical-findings.md`](references/critical-findings.md) for example vulnerability write-ups with attack demonstrations.

## Output

- **Vulnerability Report**: `${CLAUDE_SKILL_DIR}/security-reports/sqli-scan-YYYYMMDD.md` with all findings classified by severity
- **Finding Details**: per-finding file path, line number, vulnerable code, attack vector, CVSS score, and remediation code
- **Remediation Summary**: parameterized query replacements grouped by language/framework
- **Defense Recommendations**: input validation rules, database privilege changes, and WAF configuration

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Unknown ORM or database framework | Custom or uncommon data access library | Apply generic SQL injection pattern detection; note limited framework-specific guidance |
| Cannot analyze compiled/minified code | Production bundles or bytecode instead of source | Request unminified source; document reduced detection accuracy |
| False positive on sanitized input | Proper sanitization exists but not recognized | Trace sanitization implementation manually; whitelist verified-safe patterns |
| Complex dynamic query builder logic | Multi-step query construction across modules | Trace full data flow manually; flag for manual security review |
| Cannot analyze stored procedure definitions | SQL source files not available in `${CLAUDE_SKILL_DIR}/` | Request `.sql` files or database schema exports; focus on application-layer code |

## Examples

- "Scan the codebase for SQL injection risks in dynamic query construction, focusing on controllers and API handlers."
- "Review these query snippets and propose parameterized equivalents with unit tests validating the fix."
- "Detect second-order SQL injection in the user profile update flow where stored data is later used in admin queries."

## Resources

- OWASP SQL Injection Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- CWE-89 Improper Neutralization of SQL Syntax: https://cwe.mitre.org/data/definitions/89.html
- OWASP A03:2021 Injection: https://owasp.org/Top10/A03_2021-Injection/
- CAPEC-66 SQL Injection: https://capec.mitre.org/data/definitions/66.html
- [`references/critical-findings.md`](references/critical-findings.md) -- example vulnerability write-ups with attack vectors
- [`references/errors.md`](references/errors.md) -- full error handling reference
- [`references/examples.md`](references/examples.md) -- additional usage examples
- https://intentsolutions.io
