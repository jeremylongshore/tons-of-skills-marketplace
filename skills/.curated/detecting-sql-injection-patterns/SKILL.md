---
name: detecting-sql-injection-patterns
description: |
  Scan a source tree for SQL-injection vulnerable patterns: string
  concatenation into queries, f-string interpolation in SQL,
  string-format substitution into raw queries, deprecated cursor
  methods (cursor.execute with % formatting), Knex / Sequelize raw()
  with template interpolation, sequelize.query with replacements.
  Use when: pre-commit code review, post-feature SQL-touching
  release, inheriting a legacy codebase that predates ORMs, or
  post-bug-report investigation.
  Threshold: any source line where SQL keywords (SELECT / INSERT /
  UPDATE / DELETE / FROM / WHERE) appear in a string that's being
  built via concatenation, f-string, %-format, or .format() with
  variable input.
  Trigger with: "scan for sqli", "sql injection patterns",
  "check raw queries", "audit cursor.execute".
allowed-tools:
  - Read
  - Bash(python3:*)
  - Glob
  - Grep
disallowed-tools:
  - Bash(rm:*)
  - Bash(curl:*)
version: 3.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - static-analysis
  - sql-injection
  - pentest
---

# Detecting SQL Injection Patterns

## Overview

SQL injection (CWE-89, OWASP A03:2021) remains one of the highest-
impact and most-easily-introduced vulnerability classes. The fix is
near-universal: use parameterized queries. The cause when introduced:
an engineer concatenates user input into a SQL string because the
ORM's parameterization mechanism wasn't obvious, or because they
"just need to add a quick condition."

The scanner reads source files and grades each apparent SQL-string
construction against the threshold table.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| f-string with SQL keywords + user input | **CRITICAL** | `f"SELECT * FROM users WHERE id = {user_id}"` | CWE-89 |
| String concat into SQL keyword string | **CRITICAL** | `"SELECT ... " + var + " ..."` | CWE-89 |
| %-format SQL string | **HIGH** | `"SELECT * FROM %s" % table_name` | CWE-89 |
| `.format()` into SQL string | **HIGH** | `"SELECT {} FROM users".format(col)` | CWE-89 |
| `cursor.execute(f"...")` | **CRITICAL** | f-string passed directly to cursor.execute | CWE-89 |
| `sequelize.query` with template literal | **HIGH** | `sequelize.query(\`SELECT * FROM ${table}\`)` | CWE-89 |
| Knex / sequelize raw() with interpolation | **HIGH** | `knex.raw('SELECT * FROM ' + table)` | CWE-89 |
| Django `.extra()` with raw SQL | **MEDIUM** | `Model.objects.extra(where=['col = ' + val])` | CWE-89 |
| `cursor.executemany` with string-built query | **CRITICAL** | Same risk as execute | CWE-89 |
| JDBC `Statement.execute` with concat | **HIGH** | Java pattern: not PreparedStatement | CWE-89 |
| Rails `where()` with string interpolation | **HIGH** | `User.where("name = '#{name}'")` | CWE-89 |
| Go `db.Query` with `fmt.Sprintf` | **HIGH** | `db.Query(fmt.Sprintf("...", arg))` | CWE-89 |

## Prerequisites

- Python 3.9+
- Target source tree on local filesystem

## Instructions

### Step 1 — Run the scanner

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-sql-injection-patterns/scripts/scan_sqli.py /path/to/repo
```

Options:

```
Usage: scan_sqli.py PATH [OPTIONS]

Options:
  --output FILE      Write findings to FILE
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --include-tests    Include test directories (default: excluded)
  --languages LIST   Comma-separated: python,javascript,typescript,java,
                     ruby,go,php,csharp (default: all)
```

### Step 2 — Interpret findings

CRITICAL = direct user-input → query string construction. Fix the
specific query AND audit nearby code for the same pattern.

HIGH = pattern suggests interpolation but might be a fixed
identifier (table/column name). Verify by reading the code.

MEDIUM = framework-specific pattern that's safe ONLY with strict
input validation (Django `.extra()`, Rails string `where()`).

### Step 3 — Remediation

For each finding, the fix is the same shape per language: use the
language/library's parameterized-query API. See
`references/PLAYBOOK.md` for per-language snippets.

### Step 4 — Cross-skill chaining

Consider running `scanning-for-hardcoded-secrets` (#10) on the same
target — same audit, different class of finding.

## Examples

### Example 1 — Pre-merge code review

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-sql-injection-patterns/scripts/scan_sqli.py \
    --min-severity high $(git diff --name-only main...HEAD | tr '\n' ' ')
```

Scans only files changed in the current branch — fast feedback for
PR review.

### Example 2 — Legacy codebase audit

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-sql-injection-patterns/scripts/scan_sqli.py \
    /path/to/legacy-app --format markdown > sqli-audit.md
```

Expect dozens to hundreds of findings on a pre-ORM Java/PHP
codebase. Prioritize by reachability: the queries reached from
public endpoints first.

## Output

JSON / JSONL / Markdown. Exit codes: 0 clean, 1 high/critical, 2 error.

## Error Handling

- **False positives on fixed-identifier interpolation** (e.g.,
  `f"SELECT * FROM {tablename}"` where `tablename` is hardcoded) →
  verify manually. The scanner can't reason about variable
  provenance without a full AST + control-flow pass.
- **String-built dynamic-table queries** are sometimes legitimate
  (multi-tenant routing). Flag and review; the fix is usually
  allow-list validation + identifier quoting.

## Resources

- `references/THEORY.md` — Per-language interpolation patterns,
  ORM-specific safe vs unsafe APIs, why prepared statements work
- `references/PLAYBOOK.md` — Per-language parameterization snippets
  (Python sqlite3 + psycopg + SQLAlchemy, Node mysql2 + pg + knex
  - sequelize, Ruby ActiveRecord, Go database/sql, Java JDBC
  PreparedStatement, PHP PDO)
