---
name: finding-security-misconfigurations
description: 'Configure identify security misconfigurations in infrastructure-as-code,
  application settings, and system configurations.

  Use when you need to audit Terraform/CloudFormation templates, check application
  config files, validate system security settings, or ensure compliance with security
  best practices.

  Trigger with phrases like "find security misconfigurations", "audit infrastructure
  security", "check config security", or "scan for misconfigured settings".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(config-scan:*), Bash(iac-check:*)
version: 1.30.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- security
- terraform
- compliance
- audit
compatibility: Designed for Claude Code
---
# Finding Security Misconfigurations

## Overview

Scan infrastructure-as-code templates, application configuration files, and system settings to detect security misconfigurations mapped to OWASP A05:2021 (Security Misconfiguration) and CIS Benchmarks. Cover cloud resources (AWS, GCP, Azure), container orchestration (Kubernetes, Docker), web servers (Nginx, Apache), and application frameworks.

## Prerequisites

- Infrastructure-as-code files accessible in `${CLAUDE_SKILL_DIR}/` (Terraform `.tf`, CloudFormation `.yaml/.json`, Ansible playbooks, Kubernetes manifests)
- Application configuration files available (`application.yml`, `config.json`, `.env.example`, `web.config`)
- Container definitions (`Dockerfile`, `docker-compose.yml`, Helm charts)
- Web server configs (`nginx.conf`, `httpd.conf`, `.htaccess`) if applicable
- Write permissions for findings output in `${CLAUDE_SKILL_DIR}/security-findings/`
- Optional: `tfsec`, `checkov`, or `trivy config` installed for automated pre-scanning

## Instructions

1. Discover all configuration files by scanning `${CLAUDE_SKILL_DIR}/` for IaC templates (`.tf`, `.yaml`, `.json`, `.template`), application configs, container definitions, and web server configs.
2. **Cloud storage**: check for publicly accessible S3 buckets, unencrypted storage accounts, missing versioning, and overly permissive bucket policies (CIS AWS 2.1.1, 2.1.2).
3. **Network security**: flag security groups allowing `0.0.0.0/0` ingress on sensitive ports (22, 3389, 3306, 5432, 27017), missing VPC flow logs, and absent network segmentation.
4. **IAM and access**: detect wildcard (`*`) permissions in IAM policies, service accounts with admin privileges, missing MFA enforcement, and hardcoded credentials in source (CWE-798).
5. **Compute resources**: identify EC2/VM instances with unnecessary public IPs, unencrypted volumes, missing IMDSv2 enforcement, and outdated base images.
6. **Database security**: flag publicly accessible RDS/Cloud SQL instances, missing encryption at rest, disabled automated backups, default ports exposed without IP restrictions.
7. **Application config**: detect debug mode enabled in production, default credentials, CORS wildcard (`*`), missing CSRF protection, disabled authentication endpoints, and API keys in config files.
8. **Container security**: check for containers running as root, missing resource limits, `privileged: true`, writable root filesystems, and images without pinned digests.
9. Classify each finding: **Critical** (immediate exploitation risk), **High** (significant security impact), **Medium** (configuration weakness), **Low** (best practice violation).
10. Generate findings report at `${CLAUDE_SKILL_DIR}/security-findings/misconfig-YYYYMMDD.md` with per-finding severity, CIS/CWE mapping, affected file and line, remediation code, and verification command.

See [`references/implementation.md`](references/implementation.md) for the full six-section implementation guide covering IaC, application, and system checks.

## Output

- **Findings Report**: `${CLAUDE_SKILL_DIR}/security-findings/misconfig-YYYYMMDD.md` with all misconfigurations categorized by severity
- **Remediation Plan**: minimal-change fixes with before/after config snippets and verification commands
- **Compliance Mapping**: each finding linked to CIS Benchmark, OWASP, or CWE reference
- **Summary Dashboard**: finding counts by severity and category

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Syntax error in `${CLAUDE_SKILL_DIR}/terraform/main.tf` | Malformed HCL, YAML, or JSON | Validate file syntax first; skip malformed files and note parse errors in report |
| Cannot determine cloud provider from configuration | Missing provider blocks or ambiguous file structure | Look for provider blocks and file naming conventions; fall back to generic security checks |
| Cannot read encrypted configuration | SOPS-encrypted or binary config files | Request decrypted version or exported config; document inability to audit |
| Too many config files (500+) | Large monorepo or multi-service project | Prioritize by file type: IaC first, then app configs, then system configs |
| Flagged configuration is intentional (dev environment) | False positive in non-production context | Support environment-specific exception rules; allow `.securityignore` overrides |

## Examples

- "Scan Terraform files in `${CLAUDE_SKILL_DIR}/` for overly permissive security groups and IAM wildcard policies."
- "Review Kubernetes manifests for insecure defaults: privileged containers, missing resource limits, and root execution."
- "Audit the Nginx and application configs for debug mode, information disclosure, and missing security headers."

## Resources

- CIS Benchmarks: https://www.cisecurity.org/cis-benchmarks/
- OWASP IaC Security Cheatsheet:
- OWASP A05:2021 Security Misconfiguration: https://owasp.org/Top10/A05_2021-Security_Misconfiguration/
- tfsec (Terraform scanner): https://github.com/aquasecurity/tfsec
- Checkov (multi-cloud IaC scanner): https://www.checkov.io/
- CWE-16 Configuration: https://cwe.mitre.org/data/definitions/16.html
- [`references/errors.md`](references/errors.md) -- full error handling reference
- [`references/examples.md`](references/examples.md) -- additional usage examples
- https://intentsolutions.io
