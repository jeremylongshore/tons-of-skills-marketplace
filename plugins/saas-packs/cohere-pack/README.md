# Cohere v2 Operator Skill Pack

> 24 source-grounded Claude Code skills for Cohere application and model operations.

## What This Is

This pack covers current Cohere v2 clients, Chat, Embed, Rerank, retrieval-augmented generation, tool use, streaming, testing, security, privacy, access control, migrations, deployment, incidents, observability, and cost control.

The pack deliberately avoids stale shortcuts:

- Model IDs are resolved from the live catalog; `command-a-plus-05-2026`, `embed-v4.0`, and Rerank v4 are dated reference candidates, not permanent aliases.
- API v2 requires explicit models, a `messages` history for Chat, embedding types for Embed, JSON Schema tools, and tool-call correlation.
- Limits are endpoint-, model-, key-, and account-aware rather than a blanket `1,000 requests/minute` claim.
- Managed v1 connectors and other retired surfaces are replaced with application-owned v2 tools.
- Team Owner/User roles are distinguished from fine-grained application authorization.
- Privacy, retention, residency, and training claims are tied to the governing enterprise agreement.
- Provider response streams are not mislabeled as signed inbound webhooks.

## Installation

```bash
/plugin install cohere-pack@claude-code-plugins-plus
```

## Skills

| Skill | Operator outcome |
|---|---|
| `cohere-install-auth` | Install a v2 SDK, protect the key, and run a read-only access probe |
| `cohere-hello-world` | Prove one bounded Chat, Embed, or Rerank request |
| `cohere-local-dev-loop` | Keep normal tests offline with an opt-in live smoke lane |
| `cohere-sdk-patterns` | Build a typed adapter with timeouts, bounded retries, and streaming |
| `cohere-core-workflow-a` | Run asymmetric Embed, retrieval, Rerank v4, Chat, and citation validation |
| `cohere-core-workflow-b` | Execute a bounded, authorized, correlated tool-use loop |
| `cohere-common-errors` | Classify authentication, validation, model, limit, and provider failures |
| `cohere-debug-bundle` | Produce a minimal redacted support evidence bundle |
| `cohere-rate-limits` | Control endpoint-aware capacity, queues, backoff, and headroom |
| `cohere-security-basics` | Enforce key, tenant, input, output, tool, and safety controls |
| `cohere-prod-checklist` | Issue an evidence-backed production go/no-go decision |
| `cohere-upgrade-migration` | Migrate API v1, old SDKs, models, and legacy features to v2 |
| `cohere-ci-integration` | Split required offline CI from a protected live verification lane |
| `cohere-deploy-integration` | Deploy server-side, streaming-safe, canaried services |
| `cohere-webhooks-events` | Handle typed streams and application-owned durable events correctly |
| `cohere-performance-tuning` | Tune measured latency, throughput, retrieval quality, and batching |
| `cohere-cost-tuning` | Forecast and control cost from live prices and measured usage |
| `cohere-reference-architecture` | Design governed Chat, RAG, tool, evaluation, and operations boundaries |
| `cohere-multi-env-setup` | Isolate keys and promote model configuration across environments |
| `cohere-observability` | Instrument safe, low-cardinality operations and quality telemetry |
| `cohere-incident-runbook` | Triage and mitigate provider, model, capacity, and application incidents |
| `cohere-data-handling` | Bind data minimization and retention controls to approved terms |
| `cohere-enterprise-rbac` | Map Team roles to workload keys and application authorization |
| `cohere-migration-deep-dive` | Migrate providers with parallel indexes, evaluation, canarying, and rollback |

## Primary Sources

- [Create a Cohere v2 client](https://docs.cohere.com/docs/create-client)
- [Live model catalog](https://docs.cohere.com/docs/models)
- [API key types and rate limits](https://docs.cohere.com/docs/rate-limits)
- [API v1 to v2 migration](https://docs.cohere.com/docs/migrating-v1-to-v2)
- [Deprecations](https://docs.cohere.com/docs/deprecations)
- [Teams and roles](https://docs.cohere.com/reference/teams-and-roles)

## License

MIT
