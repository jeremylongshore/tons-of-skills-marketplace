---
name: vertex-infra-expert
description: 'Execute use when provisioning Vertex AI infrastructure with Terraform.
  Trigger with phrases like "vertex ai terraform", "deploy gemini terraform", "model
  garden infrastructure", "vertex ai endpoints terraform", or "vector search terraform".
  Provisions Model Garden models, Gemini endpoints, vector search indices, ML pipelines,
  and production AI services with encryption and auto-scaling.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(terraform:*), Bash(gcloud:*)
version: 2.23.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- devops
- deployment
- terraform
- ml
compatibility: Designed for Claude Code
---
# Vertex Infra Expert

## Overview

Provision Vertex AI infrastructure with Terraform (endpoints, deployed models, vector search indices, pipelines) with production guardrails: encryption, autoscaling, IAM least privilege, and operational validation steps. Use this skill to generate a minimal working Terraform baseline and iterate toward enterprise-ready deployments.

## Prerequisites

Before using this skill, ensure:

- Google Cloud project with Vertex AI API enabled
- Terraform 1.0+ installed
- gcloud CLI authenticated with appropriate permissions
- Understanding of Vertex AI services and ML models
- KMS keys created for encryption (if required)
- GCS buckets for model artifacts and embeddings

## Instructions

1. **Define AI Services**: Identify required Vertex AI components (endpoints, vector search, pipelines)
2. **Configure Terraform**: Set up backend and define project variables
3. **Provision Endpoints**: Deploy Gemini or custom model endpoints with auto-scaling
4. **Set Up Vector Search**: Create indices for embeddings with appropriate dimensions
5. **Configure Encryption**: Apply KMS encryption to endpoints and data
6. **Implement Monitoring**: Set up Cloud Monitoring for model performance
7. **Apply IAM Policies**: Grant least privilege access to AI services
8. **Validate Deployment**: Test endpoints and verify model availability

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

- Vertex AI Terraform: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/vertex_ai_endpoint
- Vertex AI documentation: https://cloud.google.com/vertex-ai/docs
- Model Garden: https://cloud.google.com/model-garden
- Vector Search guide:
- Terraform examples in ${CLAUDE_SKILL_DIR}/vertex-examples/
