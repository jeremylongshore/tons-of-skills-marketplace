# Attio Skill Pack

> 18 Claude Code skills for building, releasing, and operating Attio CRM integrations safely.

## What This Is

A production operator pack grounded in Attio's current REST, OAuth, App SDK, rate-limit, and webhook documentation. The skills cover records, lists, authentication, typed clients, testing, deployment, security, reliability, migration, cost, and performance without fabricated universal pagination, historical migration, or signature contracts.

## Installation

```bash
/plugin install attio-pack@claude-code-plugins-plus
```

## Skills

| Skill | Operator outcome |
|---|---|
| `attio-install-auth` | Select workspace-key or OAuth access and prove least-privilege scopes safely |
| `attio-hello-world` | Run a bounded read-first connectivity and schema-discovery check |
| `attio-local-dev-loop` | Combine sanitized fixtures, workspace guards, optional live checks, and cleanup |
| `attio-sdk-patterns` | Build a typed REST wrapper with tenant-bound auth and endpoint-specific pagination |
| `attio-core-workflow-a` | Operate a controlled record lifecycle without overwriting foreign fields |
| `attio-core-workflow-b` | Manage lists, entries, notes, and tasks with correct resource boundaries |
| `attio-common-errors` | Diagnose API failures from redacted evidence and the exact endpoint contract |
| `attio-debug-bundle` | Produce a minimal, checksummed, redacted escalation artifact |
| `attio-rate-limits` | Govern reads, writes, query score, backpressure, and bounded retries |
| `attio-security-basics` | Enforce tenant isolation, least privilege, redaction, HMAC, and rotation controls |
| `attio-prod-checklist` | Make a release-bound go/no-go decision with receipts and rollback evidence |
| `attio-upgrade-migration` | Migrate current contracts through diffs, shadow checks, canaries, and rollback |
| `attio-ci-integration` | Gate changes with fixtures and an optional fork-safe read-only smoke check |
| `attio-deploy-integration` | Stage a release through target checks, read smoke, canary writes, and rollback |
| `attio-webhooks-events` | Verify raw-body signatures and process at-least-once events idempotently |
| `attio-performance-tuning` | Improve measured latency and throughput while preserving correctness |
| `attio-cost-tuning` | Reduce measured request, query, synchronization, and retention waste |
| `attio-reference-architecture` | Design tenant, schema, queue, webhook, reconciliation, and ownership boundaries |

## Current Contract

- Attio REST uses `https://api.attio.com/v2`; required scopes remain endpoint-specific.
- OAuth is the default for multi-workspace applications, while a workspace API key suits one controlled workspace. Both can use Bearer authentication.
- Pagination is endpoint-specific. Record and entry queries use limit and offset, while other endpoints can expose cursor pagination.
- Attio currently documents global ceilings of 100 read requests per second and 25 write requests per second, plus score-based query limits. Reverify hosted limits before production rollout.
- Webhook signatures use SHA-256 HMAC over the exact raw request body. Delivery is at least once, so durable idempotency and reconciliation remain application responsibilities.
- Production mutations require explicit target validation, owned-field boundaries, read-after-write evidence, and rollback or cleanup receipts.

Each skill includes a dated `references/official-docs.md` and declares only the file and documentation tools it uses.

## Quality

All 18 operator skills pass the marketplace validator at Grade A and the five-check Tier-2 production gate. Regression coverage prevents universal cursor-pagination claims, timestamp-based signature inventions, unsafe diagnostic dumping, and generic historical migration claims from returning.

## License

MIT
