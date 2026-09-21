# Bright Data Operator Pack

> 18 Grade-A skills for governed Bright Data proxy, Browser API, and snapshot operations

## What It Does

This pack helps Claude Code design, test, review, and operate authorized public-data collection with current Bright Data contracts. It separates proxy-zone credentials from REST API keys, uses the current Browser API name and Web Scraper snapshot lifecycle, and places policy, cost, data, and rollback controls around every live operation.

The skills are evidence-first. Offline fixtures are the default for development and CI, live checks are bounded and independently protected, and collected data crosses quarantine and schema validation before reaching a consumer or delivery destination.

## Installation

```bash
/plugin install brightdata-pack@claude-code-plugins-plus
```

## Skills

### Foundation and Core Workflows

| Skill | What It Does |
|-------|-------------|
| `brightdata-install-auth` | Separate native proxy authentication from named-user REST API keys |
| `brightdata-hello-world` | Run one authorized proxy smoke test against `geo.brdtest.com` |
| `brightdata-local-dev-loop` | Build a credential-free, fixture-backed development loop |
| `brightdata-sdk-patterns` | Wrap the official Python SDK and REST contracts behind typed adapters |
| `brightdata-core-workflow-a` | Execute a bounded JavaScript-rendered task through Browser API |
| `brightdata-core-workflow-b` | Operate the asynchronous trigger, progress, and snapshot lifecycle |

### Reliability and Governance

| Skill | What It Does |
|-------|-------------|
| `brightdata-common-errors` | Classify current `Proxy-Status` and `x-brd-*` failure evidence |
| `brightdata-debug-bundle` | Produce a redacted, decision-ready provider support bundle |
| `brightdata-rate-limits` | Derive product-specific admission and backoff from observed signals |
| `brightdata-security-basics` | Enforce use authorization, least privilege, and data controls |
| `brightdata-prod-checklist` | Gate production promotion with failure and rollback evidence |
| `brightdata-upgrade-migration` | Migrate SDK, product, endpoint, and response-header contracts safely |

### Delivery and Operations

| Skill | What It Does |
|-------|-------------|
| `brightdata-ci-integration` | Add required offline contracts and an isolated optional live lane |
| `brightdata-deploy-integration` | Split collection, snapshot, validation, and delivery workers |
| `brightdata-webhooks-events` | Receive snapshot delivery with streaming, idempotency, and quarantine |
| `brightdata-performance-tuning` | Tune one measured bottleneck through bounded canaries |
| `brightdata-cost-tuning` | Attribute usage and enforce current-contract budgets and aborts |
| `brightdata-reference-architecture` | Define governed control, collection, quarantine, and delivery planes |

## Current Public Contracts

- Native proxy access uses a zone username and password; REST API access uses a named-user API key.
- Browser API is the current name for the former Scraping Browser product.
- Web Scraper asynchronous work uses `/datasets/v3/trigger`, `/datasets/v3/progress/SNAPSHOT_ID`, and `/datasets/v3/snapshot/SNAPSHOT_ID`.
- Snapshot destination delivery uses `/datasets/v3/deliver/SNAPSHOT_ID`.
- Current proxy diagnostics use `Proxy-Status`, `x-brd-err-code`, `x-brd-error`, and `x-brd-err-msg`.
- Bright Data publishes an official Python SDK.
- The Acceptable Use Policy and the application's approved target manifest are hard boundaries.

Each skill includes a dated `references/official-docs.md` receipt linking the first-party contracts it applies.

## License

MIT
