# Anthropic Skill Pack

> Claude Code skill pack for Anthropic Claude API integration (30 skills)

Build production Claude API integrations with the Messages API, tool use, streaming, Message Batches, prompt caching, and multi-model routing. Real code examples using the official Python (`anthropic`) and TypeScript (`@anthropic-ai/sdk`) SDKs.

## Installation

```bash
/plugin install anthropic-pack@claude-code-plugins-plus
```

## What You Can Build

- **Chatbots & assistants** with multi-turn conversations and streaming
- **AI agents** with tool use (function calling) and agentic loops
- **Batch processing pipelines** with 50% cost savings via Message Batches API
- **Multi-model routers** that select Haiku/Sonnet/Opus per task complexity
- **Production services** with prompt caching, rate limiting, and observability

## Skills Included

### Standard Skills (S01-S12)

| Skill | Description |
|-------|-------------|
| `anth-install-auth` | Install SDK (Python/TS) and configure API key authentication |
| `anth-hello-world` | First Messages API call: text, vision, and streaming examples |
| `anth-local-dev-loop` | Dev environment with hot-reload, mocks, and cost tracking |
| `anth-sdk-patterns` | Typed wrappers, conversation manager, structured output, multi-tenant |
| `anth-core-workflow-a` | Tool use (function calling) with agentic loops |
| `anth-core-workflow-b` | SSE streaming and Message Batches API (50% cheaper bulk) |
| `anth-common-errors` | All error types by HTTP code with diagnostic commands |
| `anth-debug-bundle` | Collect request IDs, rate limit headers, and API diagnostics |
| `anth-rate-limits` | Token-bucket rate limiting, RPM/TPM management, queue-based control |
| `anth-security-basics` | API key rotation, prompt injection defense, output scanning |
| `anth-prod-checklist` | Production deployment checklist with alerting thresholds |
| `anth-upgrade-migration` | SDK upgrades, Text Completions to Messages migration |

### Pro Skills (P13-P18)

| Skill | Description |
|-------|-------------|
| `anth-ci-integration` | GitHub Actions with mock tests and prompt regression tests |
| `anth-deploy-integration` | Docker, Cloud Run, Kubernetes deployment with secret management |
| `anth-webhooks-events` | SSE event handling, batch callbacks, async processing patterns |
| `anth-performance-tuning` | Prompt caching (90% savings), model selection, streaming optimization |
| `anth-cost-tuning` | Pricing calculator, model routing, spend tracking, budget alerts |
| `anth-reference-architecture` | Sync gateway, async queue, multi-model router architectures |

### Flagship Skills (F19-F24)

| Skill | Description |
|-------|-------------|
| `anth-multi-env-setup` | Dev/staging/prod with Workspaces and per-env configuration |
| `anth-observability` | Prometheus metrics, structured logging, cost dashboards |
| `anth-incident-runbook` | Triage, diagnostic commands, graceful degradation, postmortem |
| `anth-data-handling` | PII redaction, audit logging, GDPR/CCPA compliance |
| `anth-enterprise-rbac` | Workspaces, Console roles, application-level access control |
| `anth-migration-deep-dive` | OpenAI-to-Claude migration with side-by-side code mapping |

### Flagship+ Skills (X25-X30)

| Skill | Description |
|-------|-------------|
| `anth-advanced-troubleshooting` | Context overflow, tool use failures, streaming issues |
| `anth-load-scale` | Load testing, capacity planning, horizontal scaling patterns |
| `anth-reliability-patterns` | Circuit breaker, graceful degradation, idempotency |
| `anth-policy-guardrails` | Input/output validation, content policy, cost governance |
| `anth-architecture-variants` | Serverless, microservice, queue-based, orchestrator patterns |
| `anth-known-pitfalls` | Top 10 mistakes: wrong imports, missing max_tokens, response access |

## Key APIs Covered

| API | Endpoint | Use Case |
|-----|----------|----------|
| Messages | `POST /v1/messages` | Text generation, vision, tool use |
| Streaming | `POST /v1/messages` (stream) | Real-time SSE responses |
| Message Batches | `POST /v1/messages/batches` | Bulk processing (50% cheaper) |
| Token Counting | `POST /v1/messages/count_tokens` | Pre-flight token estimation |

## Resources

- [Anthropic API Docs](https://platform.claude.com/docs/en/api/overview)
- [Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript)
- [Console](https://console.anthropic.com)
- [API Status](https://status.anthropic.com)

## License

MIT
