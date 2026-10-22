---
name: genkit-production-expert
description: 'Build production Firebase Genkit applications including RAG systems,
  multi-step flows, and tool calling for Node.js/Python/Go. Deploy to Firebase Functions
  or Cloud Run with AI monitoring. Use when asked to "create genkit flow" or "implement
  RAG". Trigger with relevant phrases based on skill purpose.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(cmd:*)
version: 2.27.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
effort: medium
tags:
- ai
- deployment
- monitoring
- python
compatibility: Designed for Claude Code
---
# Genkit Production Expert

## Overview

Build production-grade Firebase Genkit applications including RAG systems, multi-step flows, and tool-calling agents for Node.js, Python, and Go. This skill covers the full lifecycle from project scaffolding and schema validation through flow implementation, local testing with the Genkit Developer UI, and deployment to Firebase Functions or Cloud Run with AI monitoring and OpenTelemetry tracing.

## Prerequisites

- Node.js 18+ (TypeScript), Python 3.10+ (Python), or Go 1.21+ (Go) runtime
- Genkit CLI and core packages (`npm install genkit @genkit-ai/googleai` for TypeScript)
- Google Cloud project with Vertex AI API enabled for Gemini model access
- Firebase CLI for Firebase Functions deployments (`npm install -g firebase-tools`)
- Zod (TypeScript), Pydantic (Python), or Go structs for input/output schema validation
- Environment variables configured for API keys (never hardcoded; use Secret Manager)

## Instructions

1. Analyze the requirements to determine target language, flow complexity (simple, multi-step, or RAG), model selection (Gemini 2.5 Flash vs Pro), and deployment target
2. Initialize the project structure with appropriate config files (`tsconfig.json`, `genkit.config.ts`, or equivalent)
3. Install Genkit core, provider plugins, and schema validation dependencies
4. Define input/output schemas using Zod, Pydantic, or Go structs to enforce type safety at runtime
5. Implement the Genkit flow using `ai.defineFlow()` with model configuration, temperature tuning, and token limits
6. Add tool definitions using `ai.defineTool()` with scoped schemas for each external capability the flow requires
7. For RAG flows: implement a retriever using `ai.defineRetriever()` with embedding generation (text-embedding-gecko) and vector database integration
8. Configure error handling for safety blocks (`SAFETY_BLOCK`), quota exceeded (`QUOTA_EXCEEDED`), and provider timeouts
9. Enable OpenTelemetry tracing with custom span attributes for cost and latency tracking
10. Test locally using the Genkit Developer UI, then deploy to Firebase Functions or Cloud Run with auto-scaling configuration

See [`references/how-it-works.md`](references/how-it-works.md) for the phased workflow and [`references/production-best-practices-applied.md`](references/production-best-practices-applied.md) for the production checklist.

## Output

- Complete Genkit flow implementation with typed schemas and model bindings
- Tool definitions with Zod/Pydantic-validated inputs and outputs
- Retriever configuration for RAG flows (embeddings, vector search, context injection)
- Deployment configuration: Firebase Functions (`firebase.json`) or Cloud Run service YAML
- Monitoring setup: OpenTelemetry tracing, Firebase Console integration, alert policies
- Cost optimization report: model selection rationale, token usage estimates, caching strategy

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `SAFETY_BLOCK` response | Model safety filters triggered on input or output | Review prompt content; adjust safety settings; add input sanitization before generation |
| `QUOTA_EXCEEDED` | API rate limit or daily token quota reached | Implement exponential backoff with jitter; request quota increase; cache repeated prompts |
| Schema validation failure | Runtime input does not match Zod/Pydantic schema | Add descriptive error messages to schema; validate inputs before calling `ai.generate()` |
| Retriever returns empty results | Vector database query found no matches above similarity threshold | Lower similarity threshold; verify embeddings are indexed; check embedding model version match |
| Deployment timeout | Cold start exceeds Firebase Functions 60s limit | Increase memory allocation; use Cloud Run for long-running flows; enable min instances > 0 |

See [`references/errors.md`](references/errors.md) for additional error scenarios.

## Examples

**Scenario 1: Question-Answering Flow** -- Create a Genkit flow using Gemini 2.5 Flash with Zod input/output schemas. Set temperature to 0.3 for factual responses. Deploy to Firebase Functions with token usage monitoring. Expected latency: under 2 seconds per query.

**Scenario 2: RAG Document Search** -- Implement a retriever with text-embedding-gecko embeddings connected to Firestore vector search. Build a RAG flow that retrieves top-5 relevant documents, injects them as context, and generates grounded answers with source citations. Include context caching for repeated queries.

**Scenario 3: Multi-Tool Agent** -- Define weather and calendar tools with typed schemas. Create an agent flow that routes user queries to appropriate tools, handles multi-turn conversations, and traces each tool execution for debugging. Deploy to Cloud Run with auto-scaling (2-10 instances).

See [`references/workflow-examples.md`](references/workflow-examples.md) for complete code examples.

## Resources

- [Firebase Genkit Documentation](https://firebase.google.com/docs/genkit) -- flows, tools, retrievers, deployment
- [Genkit GitHub Repository](https://github.com/genkit-ai/genkit) -- source code and examples
- [Zod Schema Library](https://zod.dev) -- TypeScript schema validation
- [OpenTelemetry for Node.js](https://opentelemetry.io/docs/languages/js/) -- tracing and observability
- Gemini model selection guide: Flash for throughput, Pro for reasoning quality
- Context caching and token optimization strategies for cost management
