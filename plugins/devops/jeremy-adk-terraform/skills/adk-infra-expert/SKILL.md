---
name: adk-infra-expert
description: 'Execute use when provisioning Vertex AI ADK infrastructure with Terraform.
  Trigger with phrases like "deploy ADK terraform", "agent engine infrastructure",
  "provision ADK agent", "vertex AI agent terraform", or "code execution sandbox terraform".
  Provisions Agent Engine runtime, 14-day code execution sandbox, Memory Bank, VPC
  Service Controls, IAM roles, and secure multi-agent infrastructure.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(terraform:*), Bash(gcloud:*)
version: 2.23.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- devops
- deployment
- terraform
- iam
compatibility: Designed for Claude Code
---
# Adk Infra Expert

## Overview

Provision production-grade Vertex AI ADK infrastructure with Terraform: secure networking, least-privilege IAM, Agent Engine runtime, Code Execution sandbox defaults, and Memory Bank configuration. Use this skill to generate/validate Terraform modules and a deployment checklist that matches enterprise security constraints (including VPC Service Controls when required).

## Prerequisites

Before using this skill, ensure:

- Google Cloud project with billing enabled
- Terraform 1.0+ installed
- gcloud CLI authenticated with appropriate permissions
- Vertex AI API enabled in target project
- VPC Service Controls access policy created (for enterprise)
- Understanding of Agent Engine architecture and requirements

## Instructions

1. **Initialize Terraform**: Set up backend for remote state storage
2. **Configure Variables**: Define project_id, region, agent configuration
3. **Provision VPC**: Create network infrastructure with Private Service Connect
4. **Set Up IAM**: Create service accounts with least privilege roles
5. **Deploy Agent Engine**: Configure runtime with code execution and memory bank
6. **Enable VPC-SC**: Apply service perimeter for data exfiltration protection
7. **Configure Monitoring**: Set up Cloud Monitoring dashboards and alerts
8. **Validate Deployment**: Test agent endpoint and verify all components

## Output

- Configuration files or code changes applied to the project
- Validation report confirming correct implementation
- Summary of changes made and their rationale

See Terraform implementation details for output format specifications.

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- Agent Engine: https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview
- VPC-SC: https://cloud.google.com/vpc-service-controls/docs
- Terraform Google Provider: https://registry.terraform.io/providers/hashicorp/google/latest
- ADK Terraform examples in ${CLAUDE_SKILL_DIR}/examples/
