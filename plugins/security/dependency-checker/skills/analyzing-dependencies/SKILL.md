---
name: analyzing-dependencies
description: Analyze dependencies for known security vulnerabilities and outdated
  versions. Use when auditing third-party libraries. Trigger with 'check dependencies',
  'scan for vulnerabilities', or 'audit packages'.
version: 1.28.0
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(security:*), Bash(scan:*), Bash(audit:*)
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- security
- audit
- analyzing-dependencies
compatibility: Designed for Claude Code
---
# Analyzing Dependencies

## Overview

Analyze project dependencies for known security vulnerabilities, outdated
versions, and license compliance issues across multiple package ecosystems.
This skill inspects npm, pip, Composer, Gem, Go module, and Cargo manifests
and lock files, cross-references findings against CVE databases, and produces
actionable remediation guidance with upgrade paths.

## Prerequisites

- Access to the target project directory and manifest files in `${CLAUDE_SKILL_DIR}/`
- At least one package manager CLI available: `npm`, `pip`/`pip-audit`, `composer`, `gem`, `go`, or `cargo`
- Network access for querying vulnerability databases (NVD, GitHub Advisory Database, OSV)
- Reference: [`references/README.md`](references/README.md) for npm/pip audit report formats, license compatibility matrix, and dependency management best practices

## Instructions

1. Detect the project ecosystem by scanning `${CLAUDE_SKILL_DIR}/` for manifest files: `package.json` and `package-lock.json` (npm/Node.js), `requirements.txt`/`pyproject.toml`/`Pipfile.lock` (Python), `composer.json`/`composer.lock` (PHP), `Gemfile`/`Gemfile.lock` (Ruby), `go.mod`/`go.sum` (Go), `Cargo.toml`/`Cargo.lock` (Rust).
2. For npm projects, run `npm audit --json` and parse the structured output. Map each advisory to its CVE identifier, CVSS score, severity level, vulnerable version range, and patched version.
3. For Python projects, run `pip-audit --format=json` or parse `safety check --json` output. Cross-reference each vulnerability against the OSV database for additional context.
4. For other ecosystems, run the equivalent audit command (`composer audit`, `bundle audit`, `cargo audit`, `govulncheck`) and normalize the output to a common finding format.
5. Analyze the dependency tree for transitive vulnerabilities -- identify which direct dependency pulls in the vulnerable transitive dependency, and whether upgrading the direct dependency resolves the issue.
6. Check for outdated packages by comparing installed versions against the latest available versions. Categorize updates as patch (safe), minor (likely safe), or major (breaking changes possible).
7. Audit license compliance by extracting license declarations from each dependency. Flag packages using copyleft licenses (GPL, AGPL) in proprietary projects, packages with no declared license, and packages with license conflicts per the compatibility matrix in [`references/README.md`](references/README.md).
8. Identify abandoned or unmaintained packages: flag dependencies with no releases in over 2 years, archived repositories, or known deprecation notices.
9. Classify each finding by severity (critical, high, medium, low) using CVSS scores: critical >= 9.0, high >= 7.0, medium >= 4.0, low < 4.0.
10. Generate a remediation plan with specific upgrade commands, alternative packages for abandoned dependencies, and a priority order based on severity and exploitability.

## Output

- **Vulnerability report**: Table with columns: Package, Installed Version, Vulnerability (CVE ID), CVSS Score, Severity, Patched Version, Direct/Transitive
- **Outdated packages**: Table with columns: Package, Current Version, Latest Version, Update Type (patch/minor/major), Breaking Changes Risk
- **License audit**: Table with columns: Package, License, Compatibility Status (OK, Warning, Conflict), Notes
- **Dependency tree visualization**: For critical vulnerabilities, the chain from direct dependency to vulnerable transitive dependency
- **Remediation commands**: Ready-to-run commands (e.g., `npm install package@version`, `pip install --upgrade package==version`) prioritized by severity
- **Executive summary**: Total dependencies scanned, total vulnerabilities by severity, outdated count, license conflicts count

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `npm audit` returns exit code 1 | Vulnerabilities found (expected behavior) | Parse the JSON output normally; exit code 1 indicates findings, not a tool failure |
| `pip-audit` not installed | Tool not available in the environment | Install with `pip install pip-audit` or fall back to manual `pip list --outdated` combined with OSV API queries |
| Lock file missing or outdated | Dependencies not properly locked | Run `npm install`, `pip freeze`, or equivalent to generate/update the lock file before scanning |
| Network timeout querying vulnerability DB | Firewall or connectivity issue | Retry with increased timeout; fall back to offline analysis of lock file versions against cached CVE data |
| Mixed ecosystem project | Multiple manifest files in one repo | Scan each ecosystem independently and combine results into a unified report |
| Private registry packages not found | Audit tools cannot resolve private packages | Skip private packages in the vulnerability scan; note them as "unverifiable" in the report |

## Examples

### npm Pre-Deployment Audit

Run `npm audit --json` in `${CLAUDE_SKILL_DIR}/`. Parse the output to identify critical
and high severity advisories. For each, trace the dependency chain from direct
dependency to vulnerable package. Produce upgrade commands:
`npm install express@4.19.2` to resolve CVE-2024-XXXXX in `path-to-regexp`.
Flag any advisory without a fix available as requiring a workaround or alternative package.

### Python Dependency Security Check

Run `pip-audit --format=json -r ${CLAUDE_SKILL_DIR}/requirements.txt`. Map each
vulnerability to its CVE, CVSS score, and fixed version. For transitive
dependencies, identify the direct dependency pulling in the vulnerable package.
Recommend pinning to safe versions in `requirements.txt` and adding
`pip-audit` to the CI pipeline.

### License Compliance Scan

Extract licenses from `${CLAUDE_SKILL_DIR}/node_modules/` using `license-checker --json`
or equivalent. Flag any GPL-3.0 or AGPL-3.0 licensed package used in a
proprietary application as a license conflict. Flag packages with `UNLICENSED`
or missing license fields as requiring legal review before production use.

## Resources

- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [National Vulnerability Database (NVD)](https://nvd.nist.gov/)
- [GitHub Advisory Database](https://github.com/advisories)
- [OSV: Open Source Vulnerabilities](https://osv.dev/)
- [SPDX License List](https://spdx.org/licenses/)
