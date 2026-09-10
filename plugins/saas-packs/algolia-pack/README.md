# Algolia Skill Pack

> 24 Grade-A Claude Code skills for building, releasing, and operating Algolia search safely.

## What This Is

A production operator pack grounded in the Algolia JavaScript v5 contract and current first-party documentation. The skills cover search, indexing, credentials, events, migration, deployment, observability, incidents, privacy, cost, and performance without hard-coded pricing, invented quotas, or universal latency claims.

## Installation

```bash
/plugin install algolia-pack@claude-code-plugins-plus
```

## Skills

| Skill | Operator outcome |
|---|---|
| `algolia-install-auth` | Install the v5 client and separate browser search from trusted write credentials |
| `algolia-hello-world` | Prove a write, task wait, search, and cleanup cycle on a disposable index |
| `algolia-local-dev-loop` | Combine deterministic offline tests with an optional disposable-index check |
| `algolia-sdk-patterns` | Centralize typed v5 client, task, error, timeout, and index-name policy |
| `algolia-core-workflow-a` | Build a bounded single-index search contract with filters, facets, and pagination |
| `algolia-core-workflow-b` | Publish deterministic records and configuration with task and rollback evidence |
| `algolia-common-errors` | Diagnose failures from status, message, request ID, operation, and client version |
| `algolia-debug-bundle` | Produce a redacted, size-bounded support or incident evidence bundle |
| `algolia-rate-limits` | Control measured request pressure with bounded queues and retry budgets |
| `algolia-security-basics` | Audit credentials, record exposure, restrictions, rotation, and tenant controls |
| `algolia-prod-checklist` | Make a release-bound go/no-go decision with required evidence and rollback |
| `algolia-upgrade-migration` | Migrate JavaScript v4 integrations to the client-level v5 API |
| `algolia-ci-integration` | Gate search changes with offline tests and protected disposable-index smoke tests |
| `algolia-deploy-integration` | Coordinate code, index, credential, and event release surfaces |
| `algolia-webhooks-events` | Separate Insights interaction events from source-to-index synchronization |
| `algolia-performance-tuning` | Improve an observed search path against an owned baseline and relevance suite |
| `algolia-cost-tuning` | Trace current invoice and usage drivers without embedding stale commercial terms |
| `algolia-reference-architecture` | Design repo-grounded data, trust, query, event, and failure boundaries |
| `algolia-multi-env-setup` | Isolate environment targets, credentials, data, promotion, and cleanup |
| `algolia-observability` | Instrument availability, latency, freshness, relevance, and event health |
| `algolia-incident-runbook` | Triage and recover search incidents without assuming provider causality |
| `algolia-data-handling` | Map record and event data lifecycle, minimization, correction, and deletion |
| `algolia-enterprise-rbac` | Map people and services to current team, ACL, SSO, and secured-key controls |
| `algolia-migration-deep-dive` | Execute a measured, reversible migration from another search system |

## Current Contract

- JavaScript v5 operations live on the client and receive `indexName`; the removed `initIndex` pattern is not used.
- Browser code receives only a search-only or backend-generated secured key.
- Interaction events use `search-insights` or a supported framework integration; source synchronization remains an application-owned indexing pipeline.
- Prices, plan entitlements, quotas, regions, and support behavior must be verified from the current account and first-party sources.
- Production changes require explicit target validation, task receipts, representative queries, and rollback evidence.

Each skill includes a dated `references/official-docs.md` and declares only the file and documentation tools it uses.

## Quality

All 24 skills pass the marketplace validator at Grade A and the five-check Tier-2 production gate. Regression coverage prevents stale pricing, fabricated latency targets, unsafe Admin-key shortcuts, and the old embedded-Insights claim from returning.

## License

MIT
