# Salesloft Skill Pack

> 18 Claude Code skills for building, releasing, and operating Salesloft integrations safely.

## What This Is

A production operator pack grounded in Salesloft's current REST v2, OAuth, API-key, pagination, rate-limit, webhook, API Logs, people, and cadence documentation. The skills replace demo CRM writes and obsolete endpoint assumptions with read-first proofs, explicit tenant boundaries, controlled mutations, exact error envelopes, and reconciliation.

## Installation

```bash
/plugin install salesloft-pack@claude-code-plugins-plus
```

## Skills

| Skill | Operator outcome |
|---|---|
| `salesloft-install-auth` | Select partner OAuth, customer API key, or approved private client credentials safely |
| `salesloft-hello-world` | Prove auth and team identity with one bounded read and no CRM mutation |
| `salesloft-local-dev-loop` | Test envelopes, failures, paging, and webhook signatures with sanitized fixtures |
| `salesloft-sdk-patterns` | Build a tenant-bound typed REST adapter with endpoint-specific contracts |
| `salesloft-core-workflow-a` | Resolve a person and perform explicitly approved cadence enrollment |
| `salesloft-core-workflow-b` | Reconcile mutable cadence membership state and engagement counts incrementally |
| `salesloft-common-errors` | Diagnose 401/403/404/422/429/5xx failures from redacted evidence |
| `salesloft-debug-bundle` | Produce a minimal checksummed escalation bundle without credentials or CRM payloads |
| `salesloft-rate-limits` | Govern team-wide endpoint cost, deep pages, fairness, and bounded retries |
| `salesloft-security-basics` | Enforce tenant isolation, least privilege, redaction, rotation, and SHA-1 webhook HMAC |
| `salesloft-prod-checklist` | Issue a release-SHA-bound production go/no-go decision |
| `salesloft-upgrade-migration` | Migrate used contracts through diffs, shadow reads, canaries, and rollback |
| `salesloft-ci-integration` | Gate changes with offline fixtures and a fork-safe optional read-only smoke lane |
| `salesloft-deploy-integration` | Stage rollout through secret checks, read proof, canary, monitoring, and rollback |
| `salesloft-webhooks-events` | Verify exact raw-body signatures and process retrying deliveries idempotently |
| `salesloft-performance-tuning` | Improve sync latency with cursor polling while preserving reconciliation |
| `salesloft-cost-tuning` | Reduce measured API capacity waste without inventing dollar savings |
| `salesloft-reference-architecture` | Design tenant, auth, limiter, cursor, webhook, queue, and repair boundaries |

## Current Contract

- Salesloft REST v2 uses `https://api.salesloft.com/v2`; paths, request formats, fields, and scopes remain endpoint-specific.
- Partners use OAuth. Customer API keys act as their issuing user. Admin-enabled client credentials are for private applications, expire after 7,200 seconds, and do not have refresh tokens.
- Responses use `data`; list responses can include `metadata`; 403/404 use `error`, while 422 uses field-keyed `errors`.
- The default rate limit is currently 600 cost per minute per team and can be adjusted. Deep pages cost more; clients should measure `x-ratelimit-endpoint-cost` and `x-ratelimit-remaining-minute`.
- Webhook deliveries use `x-salesloft-event` and a hexadecimal SHA-1 HMAC signature over exact raw body bytes with the subscription callback token as key. Failures are retried three additional times, 15 seconds apart.
- Production writes require explicit team and payload approval, consent and permission checks, read-after-write evidence, idempotency, and reconciliation.

Each skill includes a dated `references/official-docs.md` and declares only the file and documentation tools it uses.

## Quality

The regression contract prevents SHA-256 or timestamp-header inventions, universal `.json` paths, wrong rate-header names, partner API-key guidance, unsafe diagnostic dumping, and generic v1-to-v2 migration claims from returning.

## License

MIT
