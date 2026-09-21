# Fly.io Operator Skill Pack

> 18 source-grounded skills for controlled Fly.io application, Machine, data, security, deployment, and observability workflows.

## What this pack does

This pack turns Fly.io platform operations into bounded, reviewable procedures. It covers Fly Launch and `fly.toml`, the Machines REST API, scoped access tokens, progressive delivery, health and lifecycle evidence, Managed Postgres, region-bound Fly Volumes, private 6PN networking, cost and performance review, and operational change detection.

The skills do not claim that a planned command ran successfully. Live creation, deployment, scaling, restart, stop, suspension, deletion, token rotation, or data migration requires explicit operator approval and post-operation reconciliation.

## Current provider boundaries

- Use scoped tokens created with `fly tokens create`; do not use the deprecated hidden `fly auth token` output as a routine CI credential.
- The public Machines API base is `https://api.machines.dev`; authenticated requests use a bearer token.
- Machines API action limits are generally per action and per Machine or app identifier, not the old invented organization-wide table.
- Managed Postgres is the provider-managed database service. The older unmanaged Postgres-app documentation is not presented as the supported default.
- Fly Volumes are local NVMe storage tied to Machines and regions; snapshots do not make a single volume globally replicated.
- Rolling, canary, blue-green, and immediate are provider-supported deploy strategies. Canary and blue-green cannot be used with attached Machine volumes; blue-green requires health checks.
- Current regions and capacity are discovered from the provider rather than frozen as a marketing count.
- General Fly Apps do not have a documented customer-configured webhook subscription and signing contract. The event skill uses supported state reads, waits, health evidence, and log shipping.

## Installation

`/plugin install flyio-pack@claude-code-plugins-plus`

## Skills

| Skill | Operator outcome |
| --- | --- |
| `flyio-install-auth` | Install or upgrade flyctl and establish expiring least-privilege tokens. |
| `flyio-hello-world` | Review and verify a minimal first Fly Launch deployment. |
| `flyio-local-dev-loop` | Separate local container checks from disposable remote integration tests. |
| `flyio-sdk-patterns` | Build a typed local Machines API adapter without inventing an official SDK. |
| `flyio-core-workflow-a` | Operate app configuration, secrets, deployment, scaling, and rollback. |
| `flyio-core-workflow-b` | Design Managed Postgres, Fly Volumes, and private 6PN data paths. |
| `flyio-common-errors` | Triage release, Machine, health, routing, private DNS, and volume failures. |
| `flyio-debug-bundle` | Produce minimal redacted support evidence with hashes and retention. |
| `flyio-rate-limits` | Enforce documented per-action and per-identifier Machines API pacing. |
| `flyio-security-basics` | Harden tokens, deploy authority, App secrets, images, and networks. |
| `flyio-prod-checklist` | Gate production across ownership, resilience, data, cost, and rollback. |
| `flyio-upgrade-migration` | Migrate current runtime, config, Machine, region, volume, or database surfaces. |
| `flyio-ci-integration` | Build protected deterministic CI release lanes. |
| `flyio-deploy-integration` | Select and govern rolling, canary, or blue-green delivery. |
| `flyio-webhooks-events` | Detect supported Machine, health, release, and log changes without fake webhooks. |
| `flyio-performance-tuning` | Tune placement, resources, concurrency, autostart, and data locality. |
| `flyio-cost-tuning` | Reconcile current bills and optimize without freezing volatile prices. |
| `flyio-reference-architecture` | Design explicit routing, Machine, data, identity, and recovery boundaries. |

## Evidence and maintenance

Every skill includes `references/official-docs.md` with first-party URLs, retrieval date, snapshot fingerprints, applied facts, and a refresh rule. The provider-maintained flyctl repository was observed at `v0.4.102` on 2026-09-10. Re-fetch first-party sources before changing token types, commands, API paths, limits, state names, regions, deployment strategies, storage behavior, or price-sensitive guidance.

## License

MIT
