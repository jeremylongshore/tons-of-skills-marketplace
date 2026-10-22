---
name: auditing-access-control
description: Audit access control implementations for security vulnerabilities and
  misconfigurations. Use when reviewing authentication and authorization. Trigger
  with 'audit access control', 'check permissions', or 'validate authorization'.
version: 1.25.0
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(security:*), Bash(scan:*), Bash(audit:*)
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- security
- authentication
- audit
compatibility: Designed for Claude Code
---
# Access Control Auditing

## Overview

Audit access control implementations across codebases, cloud configurations, and
application layers for security vulnerabilities and policy violations. This skill
targets IAM policies, ACLs, RBAC configurations, file permissions, and API
authorization logic to identify privilege escalation paths, overly permissive
grants, and violations of the principle of least privilege.

## Prerequisites

- Access to the target codebase and configuration files in `${CLAUDE_SKILL_DIR}/`
- Familiarity with the authorization model in use (RBAC, ABAC, ACL, or IAM)
- `grep`, `find`, and standard shell utilities available via Bash
- For cloud audits: CLI tools such as `aws iam`, `gcloud`, or `az role` installed and authenticated
- Reference: [`references/README.md`](references/README.md) for IAM best practices, ACL vulnerability patterns, and NIST/GDPR access control standards

## Instructions

1. Enumerate all access control definitions by scanning for IAM policy files, RBAC configuration, ACL definitions, middleware authorization checks, and `.htaccess` or equivalent files using Glob and Grep.
2. Map each role or principal to its granted permissions, building a permission matrix that identifies which subjects access which resources at which privilege level.
3. Evaluate each permission grant against the principle of least privilege -- flag any wildcard permissions (`*`), overly broad resource scopes, or administrative access granted to non-admin roles.
4. Check for separation of duties violations where a single role combines mutually exclusive privileges (e.g., both "create user" and "approve user").
5. Identify privilege escalation paths by tracing role inheritance chains, looking for roles that can modify their own permissions or assume higher-privileged roles.
6. Inspect API route handlers and middleware for missing or inconsistent authorization checks -- compare route definitions against their corresponding auth guards.
7. Verify that default-deny is enforced: confirm that unauthenticated or unauthorized requests are rejected unless explicitly allowed.
8. Cross-reference findings against compliance requirements (NIST AC-1 through AC-25, GDPR Article 25, SOC 2 CC6.1) and flag gaps.
9. Classify each finding by severity (critical, high, medium, low) based on exploitability and blast radius.
10. Generate a remediation plan with specific configuration changes, code patches, or policy updates for each finding.

## Output

- **Permission matrix**: Role-to-resource mapping table showing all grants
- **Findings report**: Each finding includes severity, affected resource, description, CWE reference (e.g., CWE-269 Improper Privilege Management, CWE-285 Improper Authorization), and remediation steps
- **Compliance gap analysis**: Checklist of NIST SP 800-53 AC controls and GDPR access control requirements with pass/fail status
- **Privilege escalation paths**: Diagram or list of role chains that enable escalation
- **Executive summary**: Total findings by severity, top risks, and recommended priority actions

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Permission denied reading config files | Insufficient filesystem access | Run with elevated permissions or request read access to the target directory |
| IAM CLI command not found | Cloud CLI tools not installed | Install `aws-cli`, `gcloud`, or `az` and authenticate before running cloud audits |
| Empty role/permission scan results | Incorrect glob patterns for the framework | Adjust search patterns to match the target framework (e.g., `@Roles()` for NestJS, `[Authorize]` for .NET) |
| Timeout scanning large codebases | Too many files in scope | Narrow the scan scope with `--exclude` patterns for `node_modules`, `vendor`, or `dist` directories |
| Inconsistent policy format | Mixed IAM policy versions or formats | Normalize policies to a single format before analysis; flag format inconsistencies in the report |

## Examples

### Auditing a Node.js Express API

Scan route definitions in `${CLAUDE_SKILL_DIR}/src/routes/` for missing authorization
middleware. Grep for `router.post`, `router.put`, `router.delete` and verify
each has a corresponding `authMiddleware` or `requireRole()` call. Flag any
state-changing endpoint lacking authorization as CWE-862 (Missing Authorization),
severity high.

### Reviewing AWS IAM Policies

Parse all JSON policy files in `${CLAUDE_SKILL_DIR}/infra/iam/`. Flag policies containing
`"Effect": "Allow"` with `"Resource": "*"` or `"Action": "*"` as CWE-269
(Improper Privilege Management), severity critical. Recommend scoping to specific
ARNs and actions per the principle of least privilege.

### RBAC Configuration Audit

Analyze role definitions in `${CLAUDE_SKILL_DIR}/config/roles.yaml`. Build a permission
matrix, identify roles with overlapping admin-level privileges, and flag any role
that can both create and approve its own resources as a separation-of-duties
violation (NIST AC-5), severity medium.

## Resources

- [OWASP Access Control Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Access_Control_Cheat_Sheet.html)
- [NIST SP 800-53 AC Controls](https://csf.tools/reference/nist-sp-800-53/r5/ac/)
- [CWE-269: Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html)
- [CWE-285: Improper Authorization](https://cwe.mitre.org/data/definitions/285.html)
- [CWE-862: Missing Authorization](https://cwe.mitre.org/data/definitions/862.html)
