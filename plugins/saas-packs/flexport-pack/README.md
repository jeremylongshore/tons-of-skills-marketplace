# Flexport Operator Pack

> 24 governed Claude Code workflows for Flexport REST v3, the official Flexport MCP server, signed webhooks, and freight operations.

## Install

```bash
/plugin install flexport-pack@claude-code-plugins-plus
```

The public npm package is `@intentsolutionsio/flexport-pack`. The skill slugs remain stable across the 2.0.0 quality release.

## What changed in 2.0.0

This release replaces the repeated v2 tutorial lattice with distinct operator outcomes grounded in current first-party documentation. It removes invented endpoints, response shapes, limits, event names, retention rules, and unsafe concurrent-production-write guidance.

Key boundaries:

- REST resources use `https://api.flexport.com` and the account/default `Flexport-Version` model.
- OAuth client credentials select endpoint resources; API keys are broad and require an explicit risk decision.
- Client-credential JWTs last 24 hours and token requests are limited to 10 per day, so tokens must be cached and refreshed with single-flight control.
- Flexport MCP uses Streamable HTTP JSON-RPC at `https://mcp.flexport.com/mcp`; per-tool documentation paths are synthetic, not REST endpoints.
- Webhook SHA-256 verification uses the raw request body and `X-Hub-Signature-256`.
- Bookings and trade-record mutations require approval, durable operation identity, and reconciliation before retry.

## Skills

| Skill | Operator outcome |
| --- | --- |
| `flexport-install-auth` | Scope OAuth clients, budget token acquisition, and rotate credentials |
| `flexport-hello-world` | Prove v3 connectivity with one metadata-only read receipt |
| `flexport-core-workflow-a` | Search and evaluate rates, then book only after exact approval |
| `flexport-core-workflow-b` | Create and reconcile POs, commercial invoices, and documents |
| `flexport-sdk-patterns` | Keep REST and MCP transports behind distinct typed adapters |
| `flexport-common-errors` | Classify auth, permission, validation, provider, and ambiguous failures |
| `flexport-rate-limits` | Control request volume from documented and observed evidence |
| `flexport-webhooks-events` | Verify raw-body signatures, deduplicate, and reconcile gaps |
| `flexport-enterprise-rbac` | Map endpoint-scoped OAuth and MCP role permissions to workloads |
| `flexport-cost-tuning` | Tune volume and freshness without unsupported pricing claims |
| `flexport-data-handling` | Minimize logistics, customs, financial, and document data |
| `flexport-debug-bundle` | Produce an allowlisted metadata-only support manifest |
| `flexport-deploy-integration` | Canary and roll back provider-neutral releases |
| `flexport-incident-runbook` | Contain and reconcile delivery gaps and uncertain mutations |
| `flexport-local-dev-loop` | Develop against sanitized v3, MCP, and webhook fixtures |
| `flexport-migration-deep-dive` | Migrate through shadow reads and a single controlled writer |
| `flexport-multi-env-setup` | Isolate credentials, callbacks, queues, stores, and mutation policy |
| `flexport-observability` | Observe outcomes without leaking identifiers or payloads |
| `flexport-performance-tuning` | Tune pagination and concurrency with reconciliation evidence |
| `flexport-prod-checklist` | Gate auth, contracts, data, writes, webhooks, launch, and rollback |
| `flexport-reference-architecture` | Separate REST, MCP, webhook, approval, ledger, and reconciliation |
| `flexport-security-basics` | Harden credentials, tokens, signatures, data, and mutation controls |
| `flexport-upgrade-migration` | Upgrade versions with additive-tolerant readers and canaries |
| `flexport-ci-integration` | Run fork-safe fixture gates plus optional protected read smoke tests |

## Operating standard

Every skill includes explicit triggers, prerequisites, authentication, bounded steps, outputs, failure handling, and dated first-party source notes. Provider-side mutations are never implied by installation or a successful read.

Validate the pack from the repository root:

```bash
python3 scripts/validate-skills-schema.py --marketplace --fail-on-warn --min-grade A plugins/saas-packs/flexport-pack
python3 -m unittest tests.test_flexport_pack_contract -v
```

## First-party documentation

- [Flexport developer portal](https://developers.flexport.com/)
- [Flexport API v3 reference](https://apidocs.flexport.com/v3/)
- [Flexport MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
- [Using API credentials](https://developers.flexport.com/tutorials/using-api-credentials/)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)

## License

MIT
