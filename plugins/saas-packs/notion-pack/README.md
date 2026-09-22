# Notion Skill Pack

> 32 operator-grade workflows for current Notion integrations

The pack covers connection access, databases and data sources, pages and blocks,
webhooks, reliability, governance, migrations, and production operations. Every
skill is grounded in dated first-party documentation and treats invocation as
planning authority—not permission to access a workspace or mutate content.

## Installation

```bash
/plugin install notion-pack@claude-code-plugins-plus
```

## Operating contract

- Pin and test the Notion API and SDK combination named in current first-party
  version and upgrade documentation.
- Keep database containers, data sources, pages, blocks, files, and webhook
  signals as distinct object contracts.
- Bind each credential to its connection type, workspace, environment,
  capabilities, and explicitly shared content.
- Require explicit approval before live access, capability or sharing changes,
  content writes, subscriptions, file transfers, deployment, spend, or deletion.
- Honor runtime limits and `Retry-After`, paginate completely, tolerate additive
  response fields, and reconcile independently of webhook delivery.

## Skills

### Access and development

| Skill | Operator outcome |
|---|---|
| `notion-install-auth` | Establish a least-privilege connection and credential lifecycle |
| `notion-hello-world` | Prove bot identity and one explicitly shared read-only fixture |
| `notion-local-dev-loop` | Build an isolated fixture and sandbox development loop |
| `notion-multi-env-setup` | Separate connections, content roots, secrets, and promotion rules |
| `notion-sdk-patterns` | Isolate the SDK behind version-aware typed operation boundaries |
| `notion-known-pitfalls` | Detect recurring identity, access, version, and retry mistakes |

### Data and content

| Skill | Operator outcome |
|---|---|
| `notion-core-workflow-a` | Query a data source with schema and pagination evidence |
| `notion-core-workflow-b` | Create or update pages with idempotency and read-back |
| `notion-content-management` | Control page, block, markdown, file, move, and trash changes |
| `notion-search-retrieve` | Search and retrieve shared content within documented limits |
| `notion-data-handling` | Govern classification, minimization, retention, and deletion |
| `notion-migration-deep-dive` | Migrate content with identity maps and reconciliation |
| `notion-upgrade-migration` | Upgrade SDK and API contracts with compatibility evidence |

### Reliability and scale

| Skill | Operator outcome |
|---|---|
| `notion-common-errors` | Classify structured failures and choose bounded recovery |
| `notion-rate-limits` | Apply adaptive throttling, fairness, and retry budgets |
| `notion-reliability-patterns` | Select idempotency, checkpoint, circuit, and replay controls |
| `notion-performance-tuning` | Improve measured latency without losing completeness |
| `notion-load-scale` | Establish a tested capacity and backpressure envelope |
| `notion-cost-tuning` | Remove workload waste without inventing API pricing |
| `notion-webhooks-events` | Verify, deduplicate, process, and reconcile webhook signals |

### Production operations and governance

| Skill | Operator outcome |
|---|---|
| `notion-architecture-variants` | Choose a topology from explicit consistency and recovery needs |
| `notion-reference-architecture` | Standardize trust, operation, queue, and reconciliation boundaries |
| `notion-ci-integration` | Gate contracts without exposing tokens to untrusted CI |
| `notion-deploy-integration` | Promote immutable artifacts with canary and rollback controls |
| `notion-observability` | Define content-safe metrics, logs, traces, and alerts |
| `notion-debug-bundle` | Package reproducible, redacted incident evidence |
| `notion-advanced-troubleshooting` | Diagnose difficult failures from request and access evidence |
| `notion-incident-runbook` | Contain, recover, reconcile, and communicate incidents |
| `notion-prod-checklist` | Issue an evidence-backed production readiness decision |
| `notion-security-basics` | Establish credential, webhook, tenant, and write security |
| `notion-enterprise-rbac` | Map effective authorization across Notion and application layers |
| `notion-policy-guardrails` | Enforce security and correctness rules as gates |

## Evidence

Each skill includes `references/official-docs.md`, reviewed on 2026-09-12.
Recheck those sources and the selected connection contract at execution time.

## License

MIT
