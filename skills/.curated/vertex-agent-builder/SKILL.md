---
name: vertex-agent-builder
description: |
  Build and deploy generative AI agents on Vertex AI: Gemini model selection,
  RAG with grounded retrieval, function calling, multimodal extraction, evaluation,
  and Agent Engine deployment with operational guardrails (logs, alerts, cost
  controls). Use when designing, deploying, or operating Vertex AI agents on
  Google Cloud. Trigger with "build a Vertex agent", "deploy to Agent Engine",
  or "wire up RAG on Vertex AI".
allowed-tools: Read, Write, Edit, Grep, Bash(cmd:*)
version: 2.3.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- vertex-ai
- deployment
- gcp
compatibility: Designed for Claude Code
---
# Vertex AI Agent Builder

Build and deploy production-ready agents on Vertex AI with Gemini models, retrieval (RAG), function calling, and operational guardrails (validation, monitoring, cost controls).

## Overview

- Produces an agent scaffold aligned with Vertex AI Agent Engine deployment patterns.
- Helps choose models/regions, design tool/function interfaces, and wire up retrieval.
- Includes an evaluation + smoke-test checklist so deployments don’t regress.

## Prerequisites

- Google Cloud project with Vertex AI API enabled
- Permissions to deploy/operate Agent Engine runtimes (or a local-only build target)
- If using RAG: a document source (GCS/BigQuery/Firestore/etc) and an embeddings/index strategy
- Secrets handled via env vars or Secret Manager (never committed)

## Instructions

1. Clarify the agent’s job (user intents, inputs/outputs, latency and cost constraints).
2. Choose model + region and define tool/function interfaces (schemas, error contracts).
3. Implement retrieval (if needed): chunking, embeddings, index, and a “citation-first” response format.
4. Add evaluation: golden prompts, offline checks, and a minimal online smoke test.
5. Deploy (optional): provide the exact deployment command/config and verify endpoints + permissions.
6. Add ops: logs/metrics, alerting, quota/cost guardrails, and rollback steps.

## Output

- A Vertex AI agent scaffold (code/config) with clear extension points
- A retrieval plan (when applicable) and a validation/evaluation checklist
- Optional: deployment commands and post-deploy health checks

## Error Handling

- Quota/region issues: detect the failing service/quota and propose a scoped fix.
- Auth failures: identify the principal and missing role; prefer least-privilege remediation.
- Retrieval failures: validate indexing/embedding dimensions and add fallback behavior.
- Tool/function errors: enforce structured error responses and add regression tests.

## Examples

**Example: RAG support agent**

- Request: “Deploy a support bot that answers from our docs with citations.”
- Result: ingestion plan, retrieval wiring, evaluation prompts, and a smoke test that verifies citations.

**Example: Multimodal intake agent**

- Request: “Build an agent that extracts structured fields from PDFs/images and routes tasks.”
- Result: schema-first extraction prompts, tool interface contracts, and validation examples.

## Resources

- Implementation patterns (model selection, RAG wiring, deployment config): [`references/implementation.md`](references/implementation.md)
- Worked examples (RAG support agent, multimodal extraction): [`references/examples.md`](references/examples.md)
- Error-handling and recovery patterns: [`references/errors.md`](references/errors.md)
- Product / architecture context: [`PRD.md`](PRD.md), [`ARD.md`](ARD.md)
- Vertex AI docs: https://cloud.google.com/vertex-ai/docs
- Agent Engine docs:
