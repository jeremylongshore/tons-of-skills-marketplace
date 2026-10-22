---
name: gh-actions-validator
description: 'Validate use when validating GitHub Actions workflows for Google Cloud
  and Vertex AI deployments. Trigger with phrases like "validate github actions",
  "setup workload identity federation", "github actions security", "deploy agent with
  ci/cd", or "automate vertex ai deployment". Enforces Workload Identity Federation
  (WIF), validates OIDC permissions, ensures least privilege IAM, and implements security
  best practices.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(git:*), Bash(gcloud:*)
version: 2.27.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- devops
- deployment
- gcp
- security
compatibility: Designed for Claude Code
---
# Gh Actions Validator

## Overview

Validate and harden GitHub Actions workflows that deploy to Google Cloud (especially Vertex AI) using Workload Identity Federation (OIDC) instead of long-lived service account keys. Use this to audit existing workflows, propose a secure replacement, and add CI checks that prevent common credential and permission mistakes.

## Prerequisites

Before using this skill, ensure:

- GitHub repository with Actions enabled
- Google Cloud project with billing enabled
- gcloud CLI authenticated with admin permissions
- Understanding of Workload Identity Federation concepts
- GitHub repository secrets configured
- Appropriate IAM roles for CI/CD automation

## Instructions

1. **Audit Existing Workflows**: Scan .github/workflows/ for security issues
2. **Validate WIF Usage**: Ensure no JSON service account keys are used
3. **Check OIDC Permissions**: Verify id-token: write is present
4. **Review IAM Roles**: Confirm least privilege (no owner/editor roles)
5. **Add Security Scans**: Include secret detection and vulnerability scanning
6. **Validate Deployments**: Add post-deployment health checks
7. **Configure Monitoring**: Set up alerts for deployment failures
8. **Document WIF Setup**: Provide one-time WIF configuration commands

## Output

      - uses: actions/checkout@v4
      - name: Authenticate to GCP (WIF)
      - name: Deploy to Vertex AI
            --project=${{ secrets.GCP_PROJECT_ID }} \
            --region=us-central1
      - name: Validate Deployment

## Error Handling

See `${CLAUDE_SKILL_DIR}/references/errors.md` for comprehensive error handling.

## Examples

See `${CLAUDE_SKILL_DIR}/references/examples.md` for detailed examples.

## Resources

- Workload Identity Federation: https://cloud.google.com/iam/docs/workload-identity-federation
- GitHub OIDC: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments
- Vertex AI Agent Engine: https://cloud.google.com/vertex-ai/docs/agent-engine
- google-github-actions/auth: https://github.com/google-github-actions/auth
- WIF setup guide in ${CLAUDE_SKILL_DIR}/docs/wif-setup.md
