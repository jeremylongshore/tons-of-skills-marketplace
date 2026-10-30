# Jeremy GitHub Actions GCP

GitHub Actions expert for Google Cloud and Vertex AI deployments with Workload Identity Federation (WIF), comprehensive security validation, and deployment best practices enforcement.

## Overview

This plugin ensures secure, production-ready CI/CD pipelines for Vertex AI Agent Engine and Google Cloud services. It enforces Workload Identity Federation (WIF) instead of JSON service account keys, validates post-deployment health, and implements GitHub Actions best practices.

## Installation

```bash
/plugin install jeremy-github-actions-gcp@claude-code-plugins-plus
```

## Features

✅ **Workload Identity Federation (WIF)**: Keyless authentication from GitHub to GCP
✅ **Vertex AI Agent Engine**: Automated deployment and validation pipelines
✅ **Security Enforcement**: No JSON keys, least privilege IAM, secrets scanning
✅ **Post-Deployment Validation**: Comprehensive health checks for deployed agents
✅ **A2A Protocol Compliance**: AgentCard validation and endpoint testing
✅ **Automated Hooks**: Pre-commit validation of workflow files
✅ **Best Practices**: OIDC permissions, security scanning, monitoring setup

## Components

### Agent

- **gh-actions-gcp-expert**: Expert in GitHub Actions for Vertex AI / GCP deployments

### Skills (Auto-Activating)

- **gh-actions-validator**: Validates and enforces GitHub Actions best practices
  - **Tool Permissions**: Read, Write, Edit, Grep, Glob, Bash
  - **Version**: 1.0.0 (2026 schema compliant)

### Hooks

- **PreToolUse**: Validates workflow files before writing/editing
  - Triggers on: `.github/workflows/*.yml`, `.github/workflows/*.yaml`
  - Runs: `scripts/validate-workflow.sh`

## Quick Start

### Natural Language Activation

Simply mention what you need:

```
"Create GitHub Actions workflow for Vertex AI deployment"
"Set up Workload Identity Federation for my project"
"Deploy ADK agent to Vertex AI Engine with CI/CD"
"Validate my GitHub Actions security"
"Automate Vertex AI agent deployment"
```

The skill auto-activates and enforces best practices.

## Validation Rules Enforced

### 1. Workload Identity Federation (WIF) Mandatory

❌ **NEVER ALLOWED - JSON Service Account Keys**:

```yaml
# ❌ FORBIDDEN
- uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_SA_KEY }}  # ❌ BLOCKS HOOK
```

✅ **REQUIRED - WIF with OIDC**:

```yaml
# ✅ ENFORCED
permissions:
  id-token: write  # ✅ REQUIRED for WIF

- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
```

### 2. OIDC Permissions Required

```yaml
# ✅ ENFORCED - Must have id-token: write
permissions:
  contents: read
  id-token: write  # REQUIRED for WIF
```

### 3. IAM Least Privilege

❌ **Overly Permissive Roles Blocked**:

- `roles/owner` - ❌ Blocked
- `roles/editor` - ❌ Blocked

✅ **Least Privilege Roles Required**:

- `roles/run.admin` - Cloud Run deployments
- `roles/iam.serviceAccountUser` - Service account impersonation
- `roles/aiplatform.user` - Vertex AI operations

### 4. Post-Deployment Validation

For Vertex AI deployments, validation is **REQUIRED**:

```yaml
- name: Post-Deployment Validation
  run: |
    python scripts/validate-deployment.py \
      --agent-id=production-agent
```

**Validation Checklist**:

- ✅ Agent state is RUNNING
- ✅ Code Execution Sandbox enabled (7-14 day TTL)
- ✅ Memory Bank configured
- ✅ A2A Protocol compliant (AgentCard accessible)
- ✅ Model Armor enabled (prompt injection protection)
- ✅ VPC Service Controls configured
- ✅ Service account has minimal permissions
- ✅ Monitoring and alerting configured

### 5. Security Scanning

**Recommended** (warnings if missing):

```yaml
- name: Scan for secrets
  uses: trufflesecurity/trufflehog@main

- name: Vulnerability scanning
  uses: aquasecurity/trivy-action@master
```

## Workflow Templates

### Template 1: Vertex AI Agent Engine Deployment

```yaml
name: Deploy Vertex AI Agent

on:
  push:
    branches: [main]
    paths:
      - 'agent/**'

permissions:
  contents: read
  id-token: write

env:
  AGENT_ID: 'production-agent'
  REGION: 'us-central1'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Authenticate to GCP (WIF)
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Validate Agent Config
        run: python scripts/validate-agent-config.py

      - name: Deploy to Vertex AI Engine
        run: |
          python scripts/deploy-agent.py \
            --project-id=${{ secrets.GCP_PROJECT_ID }} \
            --agent-id=${{ env.AGENT_ID }}

      - name: Post-Deployment Validation
        run: |
          python scripts/validate-deployment.py \
            --agent-id=${{ env.AGENT_ID }}

      - name: Setup Monitoring
        run: |
          python scripts/setup-monitoring.py \
            --agent-id=${{ env.AGENT_ID }}
```

### Template 2: WIF Setup (One-Time)

```yaml
name: Setup Workload Identity Federation

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  setup-wif:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Authenticate (one-time setup key)
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SETUP_KEY }}

      - name: Run WIF setup script
        run: bash scripts/setup-wif.sh

      - name: Output WIF configuration
        run: cat wif-config.txt
```

### Template 3: Security Validation

```yaml
name: Security Checks

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  security-events: write

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Scan for secrets
        uses: trufflesecurity/trufflehog@main

      - name: Vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Validate no service account keys
        run: |
          if find . -name "*service-account*.json"; then
            echo "❌ Service account keys detected"
            exit 1
          fi

      - name: Validate WIF usage
        run: |
          if grep -r "credentials_json" .github/workflows/; then
            echo "❌ JSON credentials detected (use WIF)"
            exit 1
          fi
```

## Hook Validation

The plugin includes a **PreToolUse** hook that validates workflow files **before** they're written:

The hook reads native JSON on stdin and checks the proposed `Write` content or
the result of an `Edit`, scoped to `.github/workflows/*.yml` and `*.yaml` in the
event's working directory. It does not write the workflow. A policy violation or
unverifiable proposed edit exits **2**, which is the native blocking signal.
An explicit filename remains a manual audit and exits **1** on failure.
Python 3.10+ is required. These are lexical checks, not a YAML parser or a complete
credential/deployment security review.

```text
# Automatically runs on .github/workflows/*.yml files

scripts/validate-workflow.sh <workflow-file>

# Validates:
# ✅ No JSON service account keys (credentials_json)
# ✅ OIDC permissions present (id-token: write)
# ✅ No overly permissive IAM roles (owner/editor)
# ✅ No hardcoded credentials
# ⚠️  Vertex AI deployments have validation steps
# ⚠️  Production workflows have security scanning
```

## Use Cases

### Use Case 1: Migrate from JSON Keys to WIF

**Problem**: Using insecure JSON service account keys in workflows

**Solution**: Plugin enforces WIF and blocks JSON keys

```
User: "Create deployment workflow for Vertex AI"

Plugin provides:
1. WIF-based authentication workflow
2. One-time WIF setup script
3. Post-deployment validation
4. Hook prevents JSON key usage
```

### Use Case 2: Secure Vertex AI Deployment

**Problem**: Need production-ready CI/CD for ADK agents

**Solution**: Comprehensive deployment pipeline with validation

```
User: "Deploy my ADK agent to Vertex AI Engine"

Plugin provides:
1. GitHub Actions workflow with WIF
2. Pre-deployment config validation
3. Automated deployment script
4. Post-deployment health checks
5. Monitoring dashboard setup
6. A2A protocol validation
```

### Use Case 3: Enforce Security Best Practices

**Problem**: Workflows missing security scanning or using weak IAM

**Solution**: Hook validation + skill enforcement

```
User: "Update my deployment workflow"

Plugin validates:
1. No JSON keys (blocks if found)
2. OIDC permissions required
3. IAM least privilege
4. Security scanning recommended
5. Post-deployment validation required
```

## Integration with Other Plugins

### jeremy-adk-orchestrator

- Provides CI/CD for ADK agent deployments
- Automates A2A protocol validation

### jeremy-vertex-validator

- GitHub Actions calls validator for post-deployment checks
- Production readiness scoring

### jeremy-vertex-engine

- CI/CD triggers vertex-engine-inspector
- Continuous health monitoring

### jeremy-adk-terraform

- GitHub Actions deploys Terraform infrastructure
- Automated provisioning

## Best Practices Summary

### Security (ENFORCED)

✅ Workload Identity Federation (WIF) - no JSON keys
✅ OIDC permissions (`id-token: write`)
✅ IAM least privilege (no owner/editor)
✅ Attribute-based access control
✅ No hardcoded credentials
✅ Secrets scanning (Trufflehog)
✅ Vulnerability scanning (Trivy)

### Vertex AI Specific (ENFORCED)

✅ Code Execution Sandbox (7-14 day TTL)
✅ Memory Bank enabled
✅ A2A Protocol compliance
✅ Model Armor enabled
✅ Post-deployment validation
✅ Monitoring dashboards
✅ Alerting policies

### CI/CD (RECOMMENDED)

✅ Conditional job execution
✅ Dependency caching
✅ Concurrent jobs
✅ Rollback strategies
✅ Health check endpoints

## Requirements

- Google Cloud Project with Vertex AI enabled
- GitHub repository with Actions enabled
- WIF configured (one-time setup)
- Python 3.10+ (for deployment scripts)
- gcloud CLI

## License

MIT

## Support

- Issues: https://github.com/jeremylongshore/claude-code-plugins/issues
- Discussions: https://github.com/jeremylongshore/claude-code-plugins/discussions

## Version

1.0.0 (2025) - Initial release with WIF enforcement, Vertex AI validation, security scanning, and automated hooks
