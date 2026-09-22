# ClickUp Operator Skill Pack

> 24 production-grade Claude Code skills for designing, building, testing, and operating governed ClickUp integrations.

The pack is grounded in ClickUp's current official API documentation. It treats API v2 as the primary work-management surface and routes selected v3 capabilities endpoint by endpoint; it does not assume a platform-wide v2-to-v3 cutover. Every skill includes explicit authentication, plan, approval, redaction, failure, and verification boundaries.

**Links:** [ClickUp developer documentation](https://developer.clickup.com/) · [ClickUp status](https://status.clickup.com/) · [Tons of Skills](https://tonsofskills.com)

## Installation

```bash
/plugin install clickup-pack@claude-code-plugins-plus
```

## Current provider contract

- Personal tokens begin with `pk_`; user-facing apps use OAuth Authorization Code with server-side secret handling and Workspace verification.
- Rate limits are per personal or OAuth token and depend on the hosting Workspace plan. Operators use `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and Unix `X-RateLimit-Reset` rather than hard-coded concurrency.
- Get Tasks uses 100-item, zero-based pages. Closed tasks, subtasks, and Tasks in Multiple Lists require deliberate request options.
- Webhooks use raw-body HMAC-SHA256 in hexadecimal `X-Signature`, durable idempotency, fast acknowledgement, and reconciliation.
- ClickUp publishes separate v2 and v3 OpenAPI specifications. Generated or custom clients must route each operation to its documented version.
- Enterprise-only user/guest management, audit logs, and ACL effects are treated as plan- and authority-gated operations.

## Skills

| Skill | Operator outcome |
|---|---|
| `clickup-install-auth` | Configure personal-token or OAuth access and verify authorized Workspaces. |
| `clickup-hello-world` | Prove a minimal, read-only connection with zero writes. |
| `clickup-core-workflow-a` | Reconcile task lifecycle operations with durable source identity. |
| `clickup-core-workflow-b` | Inventory and change Spaces, Folders, Lists, tags, and views safely. |
| `clickup-common-errors` | Diagnose authentication, plan, schema, throttling, and provider failures. |
| `clickup-debug-bundle` | Produce a minimal redacted diagnostic artifact with retention controls. |
| `clickup-rate-limits` | Size queues and concurrency from observed per-token budgets. |
| `clickup-security-basics` | Threat-model credentials, tenants, webhooks, logs, and write boundaries. |
| `clickup-sdk-patterns` | Build typed, version-explicit transports from official OpenAPI inputs. |
| `clickup-local-dev-loop` | Keep routine development deterministic and offline with bounded live probes. |
| `clickup-ci-integration` | Gate adapters with offline contracts and a protected read-only live lane. |
| `clickup-deploy-integration` | Deploy with server-side secrets, canaries, health checks, and rollback. |
| `clickup-prod-checklist` | Issue an evidence-backed production go/no-go decision. |
| `clickup-upgrade-migration` | Evolve endpoint and schema contracts without assuming a global version swap. |
| `clickup-webhooks-events` | Register, verify, queue, monitor, and reconcile signed webhooks. |
| `clickup-performance-tuning` | Improve throughput without losing completeness or freshness. |
| `clickup-cost-tuning` | Reduce avoidable request and plan cost while preserving SLOs. |
| `clickup-reference-architecture` | Design trust, tenancy, version, event, reconciliation, and evidence boundaries. |
| `clickup-multi-env-setup` | Isolate development, staging, and production Workspaces and credentials. |
| `clickup-observability` | Instrument content-free metrics, traces, alerts, and reconciliation. |
| `clickup-incident-runbook` | Triage, contain, recover, and review ClickUp integration incidents. |
| `clickup-data-handling` | Govern ClickUp-derived work data across retention and deletion flows. |
| `clickup-enterprise-rbac` | Enforce role, group, audit-log, ACL, and Enterprise plan boundaries. |
| `clickup-migration-deep-dive` | Run resumable, mapped, reconciled migrations into or between Workspaces. |

## Quality contract

Each published `SKILL.md` carries marketplace metadata, explicit tool discipline, a current-contract snapshot, numbered execution steps, approval boundaries, structured output, failure handling, and an official-source reference file. The pack's regression test protects the provider facts most likely to drift or be overgeneralized.

## License

MIT
