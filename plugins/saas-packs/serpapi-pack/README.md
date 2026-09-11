# SerpAPI Skill Pack

> Eighteen governed workflows for search clients, engine contracts, testing, capacity, privacy, deployment, and operations.

This pack is grounded in SerpAPI's current first-party API, Account API, client-library, error, pricing, security, retention, ZeroTrace, and archive documentation. It uses the official Python and JavaScript `serpapi` clients, treats Python responses as `SerpResults` mappings, discovers account capacity dynamically, and models every live call as an explicit allowance boundary.

It does **not** hard-code a durable plan catalog, treat every empty result as an error, expose the private key to browsers, confuse a 429 with a single failure cause, combine `async` with `no_cache`, or invent a generic completion webhook. Re-fetch the applicable engine and account contract before production use.

## Installation

```bash
/plugin install serpapi-pack@claude-code-plugins-plus
```

## Workflows

| Skill | Production purpose |
|---|---|
| `serpapi-install-auth` | Install an official client and verify server-side account access safely |
| `serpapi-hello-world` | Run one controlled Google Search smoke test |
| `serpapi-local-dev-loop` | Develop with sanitized fixtures and an explicit live recorder |
| `serpapi-sdk-patterns` | Build a typed, testable gateway around current official clients |
| `serpapi-core-workflow-a` | Execute bounded, reproducible Google Search workflows |
| `serpapi-core-workflow-b` | Govern multi-engine parameter and result contracts |
| `serpapi-common-errors` | Classify HTTP, search-status, account, and parser failures |
| `serpapi-debug-bundle` | Prepare a privacy-safe support evidence bundle |
| `serpapi-rate-limits` | Derive admission and retry budgets from Account API capacity |
| `serpapi-security-basics` | Threat-model keys, browser exposure, data, and retention |
| `serpapi-prod-checklist` | Issue an evidence-backed production-readiness decision |
| `serpapi-upgrade-migration` | Migrate legacy Python or JavaScript clients safely |
| `serpapi-ci-integration` | Gate with fixtures and isolate protected live CI |
| `serpapi-deploy-integration` | Canary and promote a server-side search gateway |
| `serpapi-webhooks-events` | Implement documented async polling or scheduled monitoring |
| `serpapi-performance-tuning` | Tune latency, payload, caching, and concurrency from evidence |
| `serpapi-cost-tuning` | Forecast demand and remove allowance waste |
| `serpapi-reference-architecture` | Design governed trust, data, cache, and capacity boundaries |

## Current Contract Highlights

- Search APIs use a private `api_key`; this pack standardizes its server-side environment name as `SERPAPI_KEY`.
- Account API reports current usage, searches left, renewal, and hourly throughput without consuming monthly searches.
- A 429 can mean hourly throughput exhaustion or no searches remaining; inspect the account before choosing a remedy.
- Exactly matching searches may use SerpAPI's one-hour server cache for free; `no_cache=true` forces a fresh request.
- Async submission uses `async=true` and archive polling. It must not be combined with `no_cache`.
- Standard search data is documented as expiring after 31 days. Enterprise ZeroTrace skips stored search parameters, files, and metadata and therefore changes debugging and replay.
- JSON is the structured default; Markdown output and JSON Restrictor can reduce agent-token or payload cost.

## Validation

```bash
python3 scripts/validate-skills-schema.py --marketplace --min-grade A --verbose \
  plugins/saas-packs/serpapi-pack
python3 -m unittest tests.test_serpapi_pack_contract
```

## Primary Sources

- [SerpAPI documentation](https://serpapi.com/)
- [Official Python client](https://github.com/serpapi/serpapi-python)
- [Official JavaScript client](https://github.com/serpapi/serpapi-javascript)
- [Account API](https://serpapi.com/account-api)
- [Status and error codes](https://serpapi.com/api-status-and-error-codes)
- [Security](https://serpapi.com/security)

## License

MIT
