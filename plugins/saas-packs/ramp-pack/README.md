# Ramp Skill Pack

> Evidence-backed Ramp operator workflows for OAuth, cards, accounting, webhooks, security, reliability, and migration (24 skills)

## What This Covers

This pack turns Ramp's current Developer API contract into production operator workflows. It covers application and OAuth design, read-only verification, fund-backed virtual cards, ERP accounting sync, webhook processing, sandbox development, deployment, observability, incident response, data governance, performance, and enterprise migration.

The skills use the current `/developer/v1` API contract. They distinguish the Ramp sandbox at `demo-api.ramp.com` from production at `api.ramp.com`, treat third-party Authorization Code and internal Client Credentials flows separately, and replace deprecated legacy-card assumptions with Funds and current Virtual Cards guidance.

## Installation

```bash
/plugin install ramp-pack@claude-code-plugins-plus
```

## Skills Included

| Skill | Operator job |
|---|---|
| `ramp-install-auth` | Select OAuth grant, scopes, environments, and secret lifecycle |
| `ramp-hello-world` | Prove bounded read-only transaction connectivity |
| `ramp-local-dev-loop` | Build a fail-closed sandbox and fixture loop |
| `ramp-sdk-patterns` | Implement a narrow typed Developer API adapter |
| `ramp-core-workflow-a` | Issue and deliver fund-backed virtual cards safely |
| `ramp-core-workflow-b` | Reconcile two-way Ramp-to-ERP accounting sync |
| `ramp-common-errors` | Triage status, `error_v2`, trace IDs, and retry safety |
| `ramp-debug-bundle` | Produce a sanitized support evidence bundle |
| `ramp-rate-limits` | Coordinate rolling-window limits and timeout recovery |
| `ramp-security-basics` | Establish OAuth, webhook, data, card, and write controls |
| `ramp-prod-checklist` | Run the fail-closed production readiness gate |
| `ramp-upgrade-migration` | Upgrade schemas, scopes, and deprecated surfaces safely |
| `ramp-ci-integration` | Build deterministic contract and sandbox CI gates |
| `ramp-deploy-integration` | Deploy with isolation, canary, reconciliation, and rollback |
| `ramp-webhooks-events` | Verify raw-body HMAC, deduplicate, queue, and reconcile events |
| `ramp-performance-tuning` | Tune pagination, batching, concurrency, and checkpoints |
| `ramp-cost-tuning` | Reduce redundant workload without losing completeness |
| `ramp-reference-architecture` | Design trust-separated, auditable integration components |
| `ramp-multi-env-setup` | Isolate sandbox and production apps, hosts, and credentials |
| `ramp-observability` | Monitor service health and financial correctness |
| `ramp-incident-runbook` | Contain and recover through object reconciliation |
| `ramp-data-handling` | Govern financial, identity, receipt, and card data |
| `ramp-enterprise-rbac` | Audit effective authority across scopes, roles, and entities |
| `ramp-migration-deep-dive` | Migrate legacy expense platforms by reconciled cohorts |

## Safety Model

- Re-check each skill's dated first-party references and Ramp's current OpenAPI schema before a live request.
- Default to synthetic fixtures and Ramp sandbox.
- Treat access tokens, client secrets, webhook secrets, card data, receipts, identity data, and accounting payloads as sensitive.
- Require explicit business approval for card, accounting, bill, reimbursement, user, application, or configuration writes.
- Reconcile ambiguous writes and downstream financial effects before retrying.
- Preserve exact artifact, environment, scope, entity, idempotency, trace, approval, and rollback evidence.

## First-Party Documentation

- [Ramp Developer API](https://docs.ramp.com/developer-api/v1/introduction)
- [Authorization](https://docs.ramp.com/developer-api/v1/authorization)
- [OpenAPI specification](https://docs.ramp.com/openapi/developer-api.json)
- [Webhooks](https://docs.ramp.com/developer-api/v1/webhooks)
- [ERP integrations](https://docs.ramp.com/developer-api/v1/erp-integrations)
- [Cards and funds](https://docs.ramp.com/developer-api/v1/cards-and-funds)

## License

MIT
