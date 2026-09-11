# Linear Operator Skill Pack

> 24 source-grounded workflows for building and operating Linear GraphQL, SDK,
> OAuth, webhook, migration, and enterprise integrations.

**Install:** `/plugin install linear-pack@claude-code-plugins-plus`

## What this pack does

The pack covers the full integration lifecycle without treating copied snippets
as production proof. Every skill establishes the current Linear contract,
least-privilege authentication, mutation approval boundaries, redaction rules,
verification evidence, and a rollback or reconciliation path.

The guidance was checked against Linear's first-party documentation on
2026-09-11. Dynamic facts such as SDK releases, GraphQL schema fields, OAuth
scopes, plan entitlements, and rate-limit headers must be rechecked before a
production change.

## Skills

| Skill | Operator outcome |
|---|---|
| `linear-install-auth` | Pin the SDK, select the right auth actor, and prove read-only access |
| `linear-hello-world` | Verify endpoint, viewer, and visible teams without creating test data |
| `linear-local-dev-loop` | Build offline fixtures and raw-body webhook contract tests |
| `linear-sdk-patterns` | Isolate typed SDK, pagination, raw GraphQL, and error patterns |
| `linear-core-workflow-a` | Control issue creation, updates, relations, comments, and archival |
| `linear-core-workflow-b` | Reconcile projects, cycles, initiatives, milestones, and teams |
| `linear-common-errors` | Diagnose transport, GraphQL, auth, schema, and throttling failures |
| `linear-debug-bundle` | Produce a minimal redacted escalation bundle |
| `linear-rate-limits` | Coordinate request, endpoint, and complexity budgets |
| `linear-security-basics` | Harden OAuth, secrets, webhook verification, logging, and rotation |
| `linear-prod-checklist` | Issue an evidence-backed production readiness decision |
| `linear-upgrade-migration` | Upgrade SDK and deprecated schema usage with rollback |
| `linear-ci-integration` | Keep PR tests offline and gate live automation separately |
| `linear-deploy-integration` | Attach approved deployment evidence and state transitions |
| `linear-webhooks-events` | Verify, deduplicate, queue, and reconcile webhook events |
| `linear-performance-tuning` | Reduce query complexity, fan-out, page size, and polling |
| `linear-cost-tuning` | Budget integration compute, quota, storage, and operator load |
| `linear-reference-architecture` | Separate auth, adapter, policy, ingress, queue, and reconciliation |
| `linear-multi-env-setup` | Isolate apps, callbacks, credentials, webhooks, and data by environment |
| `linear-observability` | Measure API, webhook, queue, and reconciliation health safely |
| `linear-incident-runbook` | Contain auth, quota, delivery, and divergence incidents |
| `linear-data-handling` | Minimize, export, retain, and delete Linear-derived data safely |
| `linear-enterprise-rbac` | Govern roles, team access, OAuth scopes, SCIM, and audit evidence |
| `linear-migration-deep-dive` | Pilot and reconcile supported imports into Linear |

## Verified baseline

- GraphQL endpoint: `https://api.linear.app/graphql`
- Personal-key header: `Authorization: <API_KEY>`
- OAuth header: `Authorization: Bearer <ACCESS_TOKEN>`
- API-key limits: 2,500 requests and 3,000,000 complexity points per user/hour
- OAuth limits: 5,000 requests and 2,000,000 complexity points per user or app
  user/hour
- Maximum single-query complexity: 10,000 points
- Webhook verification: HMAC-SHA256 over the exact raw body
- Webhook delivery: HTTP 200 within five seconds; failed attempts retry after
  one minute, one hour, and six hours
- Official TypeScript SDK: `@linear/sdk`; npm reported 95.0.0 and Node.js
  `>=18.x` on the review date

## Safety model

The skills do not authorize credentials, OAuth apps, team access, production
mutations, webhook administration, imports, exports, SCIM changes, audit
streaming, diagnostic transmission, or commercial changes. Those operations
remain explicit owner-approved boundaries.

## License

MIT
