# BambooHR Operator Skill Pack

> 18 Claude Code skills for building and operating governed BambooHR integrations.

This pack covers tenant-scoped authentication, employee and dataset pipelines,
time-off/benefit/file controls, webhook security, reliability, diagnostics,
deployment, and release readiness. Its contracts were reviewed against
BambooHR's official Python and PHP SDK repositories and public OpenAPI on
2026-09-11.

## Installation

```bash
/plugin install bamboohr-pack@claude-code-plugins-plus
```

## Source and package status

- BambooHR publishes official Python and PHP SDK source repositories.
- `bamboohr/api` 2.0.1 was available on Packagist at the review date.
- The official Python repository documents `bamboohr-sdk` 1.0.0, but the public
  PyPI registry did not expose that distribution and the repository had no tag
  or GitHub release at the review date. Reverify before installing; an approved
  source use must pin an immutable commit.
- The pack does not claim an official npm SDK, universal numeric API quota, or
  per-request BambooHR price.

## Skills

| Skill | Operator outcome |
|---|---|
| `bamboohr-install-auth` | Choose OAuth or a least-privilege API key and design safe token/key custody |
| `bamboohr-hello-world` | Prove a tenant connection without exporting employee data |
| `bamboohr-sdk-patterns` | Select and wrap a verified Python, PHP, or direct HTTP transport |
| `bamboohr-core-workflow-a` | Build a minimized, reconciled employee/dataset v2 sync |
| `bamboohr-core-workflow-b` | Separate and govern time-off, benefit, and employee-file reads/writes |
| `bamboohr-webhooks-events` | Operate webhooks with one-time key custody, HMAC, replay, and idempotency controls |
| `bamboohr-common-errors` | Triage typed failures and incomplete responses by request ID and contract layer |
| `bamboohr-rate-limits` | Apply finite retry, backpressure, queue, and circuit-breaker behavior |
| `bamboohr-performance-tuning` | Remove N+1 traffic and tune dataset projection/pagination with reconciliation |
| `bamboohr-cost-tuning` | Reduce measurable connector waste without invented API pricing |
| `bamboohr-security-basics` | Threat-model employee data, tenant isolation, credentials, logs, and webhooks |
| `bamboohr-debug-bundle` | Produce a PII-minimized diagnostic receipt rather than a raw log archive |
| `bamboohr-local-dev-loop` | Develop offline with synthetic fixtures and a no-network fake transport |
| `bamboohr-ci-integration` | Gate changes with pinned OpenAPI contracts and fork-safe synthetic tests |
| `bamboohr-deploy-integration` | Promote immutable artifacts with isolated secrets, canaries, and rollback |
| `bamboohr-reference-architecture` | Design control/data planes, queues, checkpoints, destinations, and recovery |
| `bamboohr-upgrade-migration` | Move SDK/endpoint/auth contracts through dual-read comparison and rollback |
| `bamboohr-prod-checklist` | Issue an evidence-backed GO/NO-GO decision for a specific release |

## Safety boundary

The skills do not authorize credential creation, tenant reads, HR mutations,
deployment, permission expansion, or evidence transmission. Those actions need
explicit approval and the owning organization's HR, privacy, security, and
operations controls. Never place employee payloads, access/refresh tokens, API
keys, or webhook private keys in source control, CI artifacts, chat transcripts,
or general logs.

## Current API direction

New bulk employee-data workflows should prefer the current dataset v2 contract
and use v1.2 dataset/field discovery. Dataset v1 data retrieval and legacy report
operations carry deprecation notices. Webhook creation returns a verification
`privateKey` only once; capture it directly into an approved secret manager.

Every skill contains a dated `references/official-docs.md` register with the
reviewed repository commits, registry checks, and primary-source links.

## License

MIT
