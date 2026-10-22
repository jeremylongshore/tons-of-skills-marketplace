---
name: genkit-infra-expert
description: 'Execute use when deploying Genkit applications to production with Terraform.
  Trigger with phrases like "deploy genkit terraform", "provision genkit infrastructure",
  "firebase functions terraform", "cloud run deployment", or "genkit production infrastructure".
  Provisions Firebase Functions, Cloud Run services, GKE clusters, monitoring dashboards,
  and CI/CD for AI workflows.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(terraform:*), Bash(gcloud:*)
version: 2.22.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- devops
- deployment
- terraform
- monitoring
compatibility: Designed for Claude Code
---
# Genkit Infra Expert

## Overview

Deploy Genkit applications to production with Terraform (Firebase Functions, Cloud Run, or GKE) with secure secrets handling and observability. Use this skill to choose a target, generate the Terraform baseline, wire up Secret Manager, and provide a validation checklist for your Genkit flows.

## Prerequisites

Before using this skill, ensure:

- Google Cloud project with Firebase enabled
- Terraform 1.0+ installed
- gcloud and firebase CLI authenticated
- Genkit application built and containerized
- API keys for Gemini or other AI models
- Understanding of Genkit flows and deployment options

## Instructions

1. **Choose Deployment Target**: Firebase Functions, Cloud Run, or GKE
2. **Configure Terraform Backend**: Set up remote state in GCS
3. **Define Variables**: Project ID, region, Genkit app configuration
4. **Provision Compute**: Deploy functions or containers
5. **Configure Secrets**: Store API keys in Secret Manager
6. **Set Up Monitoring**: Create dashboards for token usage and latency
7. **Enable Auto-scaling**: Configure min/max instances
8. **Validate Deployment**: Test Genkit flows via HTTP endpoints

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

- Genkit Deployment:
- Firebase Terraform: https://registry.terraform.io/providers/hashicorp/google/latest
- Genkit examples in ${CLAUDE_SKILL_DIR}/genkit-examples/
