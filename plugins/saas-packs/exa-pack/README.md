# Exa Operator Skill Pack

> 30 governed workflows for current Exa Search, Contents, Agent, Monitors, Websets, and enterprise operations.

This pack helps operators build Exa integrations without leaking credentials or retrieved content, preserving legacy search types, ignoring partial crawl failures, or orphaning asynchronous work. It is grounded in current first-party Exa documentation reviewed on 2026-09-12.

## Installation

```bash
/plugin install exa-pack@claude-code-plugins-plus
```

## What You Get

Each skill distinguishes repository inspection, implementation, live retrieval, paid research, privileged team changes, and destructive cleanup. The workflows require Bearer authentication for normal REST calls, explicit product selection, endpoint-specific budgets, per-URL Contents status handling, signed Monitor webhooks, content-free evidence, and lifecycle reconciliation.

New code uses current Search types rather than legacy `neural` terminology. HIPAA mode is treated as an enabled, request-scoped, cache-only Search or Contents contract, not a generic compliance claim.

## Skills Included

### Core retrieval and development

| Skill | What It Does |
|-------|-------------|

| `exa-install-auth` | Configure an Exa client without leaking credentials or mixing API-key, MCP OAuth, enterprise managed authorization, and payment-protocol trust models. |

| `exa-hello-world` | Prove a new Exa Search integration with a bounded synthetic query and content-free assertions. |

| `exa-local-dev-loop` | Build and test an Exa adapter locally using schema fixtures, recorded content-free envelopes, and an explicit opt-in live lane. |

| `exa-sdk-patterns` | Isolate exa-js or exa-py behind an application-owned adapter that preserves current request semantics and safe evidence. |

| `exa-core-workflow-a` | Operate Search and Contents as an explicit two-stage retrieval workflow with bounded context, freshness, and cost. |

| `exa-core-workflow-b` | Run asynchronous Exa Agent research with a bounded schema, effort, terminal-state policy, citations, and cleanup decision. |

| `exa-common-errors` | Classify Exa failures by HTTP status, error tag, endpoint, and per-item crawl status before deciding whether to repair, retry, or escalate. |

| `exa-debug-bundle` | Produce a minimal Exa diagnostic bundle that preserves reproducibility without exposing credentials, queries, retrieved content, or customer data. |

| `exa-rate-limits` | Budget Exa throughput per endpoint and distinguish caller rate limiting from vendor overload and billing exhaustion. |

| `exa-security-basics` | Threat-model Exa credentials, query intent, retrieved web content, generated output, and retained operational evidence as separate trust boundaries. |

| `exa-prod-checklist` | Gate an Exa-backed service on contract, security, cost, reliability, observability, and rollback evidence. |

| `exa-upgrade-migration` | Upgrade Exa SDK or API usage through a contract inventory, fixture diff, canary, and reversible dependency change. |

### Delivery and operations

| Skill | What It Does |
|-------|-------------|

| `exa-ci-integration` | Add deterministic Exa contract checks to CI while keeping live credentials, spend, and volatile web results out of ordinary pull requests. |

| `exa-deploy-integration` | Deploy an Exa integration with server-side credentials, bounded concurrency, canary controls, and explicit rollback of scheduled work. |

| `exa-webhooks-events` | Receive Exa Monitor events through verified signatures, replay resistance, deduplication, and fast acknowledgment. |

| `exa-performance-tuning` | Tune Exa search type, content mode, freshness, result count, and concurrency against measured latency and retrieval quality. |

| `exa-cost-tuning` | Control Exa spend through endpoint selection, bounded result and content work, per-key budgets, and response-derived cost evidence. |

| `exa-reference-architecture` | Design an Exa architecture that separates query policy, retrieval, content handling, asynchronous state, citations, and evidence. |

### Enterprise governance

| Skill | What It Does |
|-------|-------------|

| `exa-multi-env-setup` | Separate Exa development, staging, and production credentials, budgets, schedules, data, and observability. |

| `exa-observability` | Instrument Exa calls with content-free metrics, traces, cost, and asynchronous lifecycle signals that support diagnosis without logging retrieved text. |

| `exa-incident-runbook` | Contain Exa credential, data, cost, capacity, or correctness incidents while preserving safe evidence and vendor request IDs. |

| `exa-data-handling` | Govern queries, public-web retrieval, generated summaries, citations, and downstream copies across their full retention lifecycle. |

| `exa-enterprise-rbac` | Govern Exa membership, API and service keys, team budgets, MCP OAuth, and enterprise managed authorization through least privilege and revocation evidence. |

| `exa-migration-deep-dive` | Migrate a legacy web-search integration to Exa through semantic, filter, freshness, relevance, cost, and rollback comparisons. |

### Scale and architecture

| Skill | What It Does |
|-------|-------------|

| `exa-advanced-troubleshooting` | Localize complex Exa failures across query planning, retrieval, crawling, synthesis, SDK mapping, queues, and downstream consumption. |

| `exa-load-scale` | Validate Exa capacity with synthetic workload models, endpoint-specific budgets, bounded queues, and stop conditions. |

| `exa-reliability-patterns` | Design bounded Exa retries, deadlines, partial-result behavior, and tested fallbacks by endpoint and failure class. |

| `exa-policy-guardrails` | Enforce query, domain, moderation, freshness, content, and downstream-use policy before and after Exa retrieval. |

| `exa-architecture-variants` | Choose among direct Search, staged Contents, Answer, Agent, Monitors, Websets, and Batch using explicit latency, verification, volume, and lifecycle criteria. |

| `exa-known-pitfalls` | Audit an Exa integration for stale search types, unsafe secrets, ignored partial failures, unbounded content work, weak citations, and orphaned asynchronous resources. |

## Current Contract Highlights

- Normal REST calls use `Authorization: Bearer`; administrative service keys and MCP authorization are separate boundaries.
- Search types are `auto`, `fast`, `instant`, `deep-lite`, `deep`, and `deep-reasoning`; `neural` is legacy terminology.
- Contents callers inspect per-URL statuses even when the outer request succeeds.
- Agent runs, Monitors, Websets, and Batches have explicit asynchronous lifecycles.
- Monitor webhook secrets are returned once and deliveries require raw-body HMAC verification.
- Current price, limit, beta, compliance, and retention facts are verified before live work.

## License

MIT
