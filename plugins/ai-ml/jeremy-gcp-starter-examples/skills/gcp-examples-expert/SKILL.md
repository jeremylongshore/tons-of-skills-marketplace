---
name: gcp-examples-expert
description: 'Generate production-ready Google Cloud code examples from official repositories
  including ADK samples, Genkit templates, Vertex AI notebooks, and Gemini patterns.
  Use when asked to "show ADK example" or "provide GCP starter kit". Trigger with
  relevant phrases based on skill purpose.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(cmd:*)
version: 2.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
effort: medium
argument-hint: '[framework or use-case]'
tags:
- ai
- gcp
- gcp-examples
compatibility: Designed for Claude Code
---
# GCP Examples Expert

## Overview

Generate production-ready Google Cloud Platform code examples sourced from official repositories including ADK samples, Agent Starter Pack, Firebase Genkit, Vertex AI samples, Generative AI examples, and AgentSmithy. This skill maps user requirements to the appropriate GCP framework and delivers working code with security, monitoring, and deployment best practices baked in.

## Prerequisites

- Google Cloud project with billing enabled and Vertex AI API activated
- `gcloud` CLI authenticated with appropriate IAM roles (Vertex AI User, Cloud Run Developer)
- Node.js 18+ for Genkit/TypeScript examples or Python 3.10+ for ADK/Vertex AI examples
- Firebase CLI for Genkit deployments (`npm install -g firebase-tools`)
- API keys or service account credentials configured via Secret Manager (never hardcoded)

## Instructions

1. Identify the target framework by matching the request to one of six categories: ADK agents, Agent Starter Pack, Genkit flows, Vertex AI training, Generative AI multimodal, or AgentSmithy orchestration
2. Select the appropriate source repository and code pattern from [`references/code-example-categories.md`](references/code-example-categories.md)
3. Adapt the template to the specified programming language (TypeScript, Python, or Go)
4. Configure security settings: IAM least-privilege service accounts, VPC Service Controls, Model Armor for prompt injection protection
5. Add monitoring instrumentation: Cloud Monitoring dashboards, alerting policies, structured logging, OpenTelemetry tracing
6. Set auto-scaling parameters with appropriate min/max instance counts for the deployment target
7. Include cost optimization: select Gemini 2.5 Flash for simple tasks, Gemini 2.5 Pro for complex reasoning, batch predictions for bulk workloads
8. Generate deployment configuration for the target platform (Cloud Run, Firebase Functions, or Vertex AI Endpoints)
9. Provide Terraform or IaC templates for reproducible infrastructure provisioning
10. Cite the source repository and link to official documentation for each pattern used

See [`references/workflow.md`](references/workflow.md) for the phased workflow and [`references/best-practices-applied.md`](references/best-practices-applied.md) for the full best-practices checklist.

## Output

- Complete, runnable code example with imports, configuration, and error handling
- Deployment configuration (Cloud Run service YAML, Firebase function config, or Terraform module)
- Environment variable template listing required secrets and API keys
- Monitoring setup: dashboard JSON, alerting policy definitions, log-based metrics
- Cost estimate guidance based on model selection and expected throughput
- Source repository citation and documentation links

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid GCP project or API not enabled | Vertex AI API disabled or project ID misconfigured | Run `gcloud services enable aiplatform.googleapis.com`; verify project ID in `gcloud config list` |
| Permission denied on Vertex AI resources | Service account missing required IAM roles | Grant `roles/aiplatform.user` and `roles/run.developer`; check VPC-SC perimeter allows access |
| Model not available in region | Requested Gemini model not deployed in specified location | Use `us-central1` or `europe-west4` where Gemini models are available; check regional availability docs |
| Quota exceeded for API calls | Rate limit hit on Vertex AI prediction endpoint | Request quota increase via Cloud Console; implement exponential backoff with jitter |
| Dependency version conflict | Incompatible versions of AI SDK, Genkit, or provider packages | Pin versions in `package.json` or `requirements.txt`; use lockfile to ensure reproducibility |

See [`references/errors.md`](references/errors.md) for additional error scenarios.

## Examples

**Scenario 1: ADK Agent with Code Execution** -- Create a production ADK agent using `google/adk-samples` patterns. Enable Code Execution Sandbox with 14-day state TTL, configure Memory Bank for persistent context, apply VPC Service Controls and IAM least-privilege. Deploy to Vertex AI Agent Engine.

**Scenario 2: Genkit RAG Flow** -- Implement a retrieval-augmented generation system using Firebase Genkit. Define a retriever with text-embedding-gecko embeddings, connect to a vector database, build a RAG flow with Zod-validated input/output schemas. Deploy to Cloud Run with auto-scaling (2-10 instances).

**Scenario 3: Gemini Multimodal Analysis** -- Analyze video content using the `generative-ai` repository patterns. Create a multimodal prompt combining video URIs with text questions using Gemini 2.5 Pro. Include safety filter configuration, token counting for cost estimation, and structured output parsing.

See [`references/example-interactions.md`](references/example-interactions.md) for detailed interaction examples.

## Resources

- [google/adk-samples](https://github.com/google/adk-samples) -- ADK agent creation patterns
- [GoogleCloudPlatform/agent-starter-pack](https://github.com/GoogleCloudPlatform/agent-starter-pack) -- production agent templates
- [genkit-ai/genkit](https://github.com/genkit-ai/genkit) -- RAG flows, tool calling, evaluation
- [GoogleCloudPlatform/vertex-ai-samples](https://github.com/GoogleCloudPlatform/vertex-ai-samples) -- model training, tuning, deployment
- [GoogleCloudPlatform/generative-ai](https://github.com/GoogleCloudPlatform/generative-ai) -- Gemini multimodal, function calling, grounding
- [GoogleCloudPlatform/agentsmithy](https://github.com/GoogleCloudPlatform/agentsmithy) -- multi-agent orchestration
