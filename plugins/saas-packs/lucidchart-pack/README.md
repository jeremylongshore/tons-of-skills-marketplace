# Lucidchart Skill Pack

> Eighteen governed workflows for Lucid REST operations, Standard Import, editor extensions, and data connectors.

This pack is grounded in Lucid's public developer contracts. It distinguishes API keys, OAuth user tokens, and OAuth account tokens; uses Bearer authorization and operation-specific API versions; treats rate limits as endpoint-specific; and uses the official `lucid-package` and `lucid-extension-sdk` tooling.

It does **not** claim universal quotas, document locking, generic document/shape/collaboration webhooks, fabricated signature headers, or per-export/API-call pricing. The webhook workflow is intentionally limited to the documented data-connector model.

## Installation

```bash
/plugin install lucidchart-pack@claude-code-plugins-plus
```

## Workflows

| Skill | Production purpose |
|---|---|
| `lucidchart-hello-world` | Validate a minimal Standard Import fixture and optional one-document smoke test |
| `lucidchart-install-auth` | Choose API key, OAuth user token, or OAuth account token safely |
| `lucidchart-core-workflow-a` | Create and verify a governed Standard Import document |
| `lucidchart-core-workflow-b` | Import or synchronize governed data through extensions/connectors |
| `lucidchart-sdk-patterns` | Implement against installed Lucid SDK types and official tooling |
| `lucidchart-local-dev-loop` | Run a fast, secretless extension/connector development loop |
| `lucidchart-ci-integration` | Gate imports, REST clients, extensions, and connectors in CI |
| `lucidchart-deploy-integration` | Package, stage, publish, and roll back integrations |
| `lucidchart-common-errors` | Triage auth, version, import/export, SDK, and connector failures |
| `lucidchart-rate-limits` | Implement endpoint-specific backpressure and safe retry behavior |
| `lucidchart-performance-tuning` | Benchmark and improve imports, exports, extensions, or connectors |
| `lucidchart-security-basics` | Threat-model credentials, scopes, archives, bundles, and data flows |
| `lucidchart-prod-checklist` | Run a fail-closed production readiness gate |
| `lucidchart-upgrade-migration` | Migrate SDK, CLI, manifest, API, format, or connector contracts |
| `lucidchart-reference-architecture` | Select and document the smallest supported integration surface |
| `lucidchart-debug-bundle` | Build a redacted, reproducible escalation bundle |
| `lucidchart-cost-tuning` | Review seats, plans, licensing, operating effort, and realized value |
| `lucidchart-webhooks-events` | Operate documented data-connector webhook-assisted synchronization |

Each skill carries its own dated official-source map. Re-fetch the exact operation page and inspect installed CLI/SDK types before relying on a scope, header, endpoint, command, limit, event, or compatibility claim.

## Validation

```bash
python3 scripts/validate-skills-schema.py --marketplace --min-grade A --verbose \
  plugins/saas-packs/lucidchart-pack
python3 -m unittest tests.test_lucidchart_pack_contract
```

## License

MIT
