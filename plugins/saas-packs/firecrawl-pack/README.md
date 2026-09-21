# Firecrawl Operator Skill Pack

> 30 production-oriented skills for Firecrawl v2 acquisition, governance, and operations

## What It Does

Firecrawl exposes scrape, crawl, map, search, batch, parse, structured extraction,
agentic, and browser workflows. This pack teaches current v2 client contracts and
the operational controls around them: source authorization, explicit limits,
complete pagination, content validation, spend, retention, observability,
incident response, access governance, and rollback.

- Node install surface: `firecrawl`, named `Firecrawl` client
- Python install surface: `firecrawl-py`, `Firecrawl` client
- REST base: `https://api.firecrawl.dev/v2`
- Cloud authentication: `Authorization: Bearer` with a secret-managed API key
- Evidence snapshot: Firecrawl docs commit
  `8bd51cb7e68e3b931d6895f6094e1cf5c709de09`, reviewed 2026-09-11

Plan limits, prices, feature availability, and self-host release pins can change.
Each skill links to the current first-party evidence that must be re-checked.

## Installation

```bash
/plugin install firecrawl-pack@claude-code-plugins-plus
```

## Skills

| Skill | Operator outcome |
| --- | --- |
| `firecrawl-install-auth` | Install the current SDK and establish secret-managed identity |
| `firecrawl-hello-world` | Verify one minimal v2 scrape with provenance assertions |
| `firecrawl-local-dev-loop` | Use deterministic fakes and a bounded self-host evaluation |
| `firecrawl-sdk-patterns` | Build a typed application-owned v2 adapter |
| `firecrawl-core-workflow-a` | Run governed scrape and crawl acquisition |
| `firecrawl-core-workflow-b` | Map, search, batch, parse, and extract typed data |
| `firecrawl-common-errors` | Classify errors and retry only documented classes |
| `firecrawl-debug-bundle` | Create privacy-safe support evidence |
| `firecrawl-rate-limits` | Control team RPM, browser concurrency, and queue pressure |
| `firecrawl-security-basics` | Protect keys, targets, webhooks, content, and retention |
| `firecrawl-prod-checklist` | Produce an evidence-backed production decision |
| `firecrawl-upgrade-migration` | Migrate legacy v0/v1 methods and defaults to v2 |
| `firecrawl-ci-integration` | Gate contracts and safety with synthetic CI |
| `firecrawl-deploy-integration` | Deploy Cloud clients or hardened self-hosted stacks |
| `firecrawl-webhooks-events` | Verify, deduplicate, process, and reconcile signed events |
| `firecrawl-performance-tuning` | Improve latency without losing quality or freshness |
| `firecrawl-cost-tuning` | Attribute and control credit spend |
| `firecrawl-reference-architecture` | Design a governed ingestion platform |
| `firecrawl-multi-env-setup` | Separate identities, policy, data, and budgets by environment |
| `firecrawl-observability` | Measure jobs, queue, credits, origin status, and quality |
| `firecrawl-incident-runbook` | Stabilize and recover production incidents |
| `firecrawl-data-handling` | Govern provenance, validation, storage, and deletion |
| `firecrawl-enterprise-rbac` | Apply real team, key, IP, SSO, and separation controls |
| `firecrawl-migration-deep-dive` | Replace custom scrapers with measured parity and rollback |
| `firecrawl-advanced-troubleshooting` | Isolate failures layer by layer |
| `firecrawl-load-scale` | Establish an authorized capacity envelope |
| `firecrawl-reliability-patterns` | Add durable state, idempotency, and reconciliation |
| `firecrawl-policy-guardrails` | Enforce collection authorization and request policy |
| `firecrawl-architecture-variants` | Select the right endpoint and hosting topology |
| `firecrawl-known-pitfalls` | Review legacy, scope, pagination, retry, and trust hazards |

## Current Node Example

```typescript
import { Firecrawl } from "firecrawl";

const firecrawl = new Firecrawl({
  apiKey: process.env.FIRECRAWL_API_KEY,
});

const document = await firecrawl.scrape("https://docs.example.com", {
  formats: ["markdown"],
  onlyMainContent: true,
});

if (!document.metadata?.sourceURL || document.metadata.statusCode >= 400) {
  throw new Error("Firecrawl returned an invalid source document");
}
```

Use `crawl` for a waiter, `startCrawl` plus `getCrawlStatus` for durable
asynchronous orchestration, and retrieve all result pages before claiming
completeness.

## First-Party References

- [Firecrawl v2 API](https://docs.firecrawl.dev/api-reference/v2-introduction)
- [Node SDK](https://docs.firecrawl.dev/sdks/node)
- [Python SDK](https://docs.firecrawl.dev/sdks/python)
- [Errors and retry guidance](https://docs.firecrawl.dev/api-reference/errors)
- [Billing](https://docs.firecrawl.dev/billing)
- [Rate limits](https://docs.firecrawl.dev/rate-limits)
- [Webhooks](https://docs.firecrawl.dev/webhooks/overview)
- [Self-hosting](https://docs.firecrawl.dev/contributing/self-host)
- [Official source](https://github.com/firecrawl/firecrawl)

## License

MIT
