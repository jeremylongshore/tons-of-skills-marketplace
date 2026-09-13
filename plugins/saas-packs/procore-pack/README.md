# Procore Operator Pack

> 24 governed Claude Code workflows for Procore OAuth, DMSA permissions, REST resources, webhooks, files, integration health, and construction-data synchronization.

## Install

```bash
/plugin install procore-pack@claude-code-plugins-plus
```

The public npm package is `@intentsolutionsio/procore-pack`. Every public skill slug remains stable across the 2.0.0 quality release.

## What changed in 2.0.0

This release replaces the repeated tutorial lattice with distinct operator outcomes grounded in current first-party Procore documentation. It removes guessed fields, one-size-fits-all versions, fixed rate assumptions, unsafe bulk diagnostic archives, and fictional pack-wide version jumps.

Key boundaries:

- User-context apps use OAuth Authorization Code; unattended data connectors use Client Credentials through a permissioned Developer Managed Service Account.
- Company routing, tool permissions, project membership, enabled tools, and DMSA permitted projects jointly determine access.
- Developer, On-Demand, Monthly, and production environments have different key, credential, host, installation, and reset contracts.
- API versions and page limits are endpoint-specific; clients preserve Link, rate, retry, and error metadata.
- Webhooks are best-effort notifications. Durable queues, idempotency, hydration, and periodic REST reconciliation provide complete downstream state.
- Direct uploads, secure downloads, and resource association are separate file contracts.
- Local Grade A validation is not Procore certification, Marketplace approval, or behavioral verification.

## Skills

| Skill | Operator outcome |
| --- | --- |
| `procore-install-auth` | Choose user OAuth or DMSA auth, scope permissions, and govern token lifecycle |
| `procore-hello-world` | Prove identity, company routing, project scope, and pagination read-only |
| `procore-local-dev-loop` | Test fixtures and bounded Developer Sandbox mutations with cleanup |
| `procore-sdk-patterns` | Preserve endpoint versions, routing, pagination, rate headers, and errors |
| `procore-core-workflow-a` | Create and reconcile governed RFI lifecycle changes |
| `procore-core-workflow-b` | Operate version-aware submittal and workflow-data contracts |
| `procore-common-errors` | Classify identity, routing, permission, validation, rate, and provider failures |
| `procore-debug-bundle` | Produce a minimal redacted escalation manifest |
| `procore-rate-limits` | Pace workers from spike, hourly, reset, and Retry-After evidence |
| `procore-security-basics` | Threat-model credentials, tenants, permissions, files, logs, and writes |
| `procore-prod-checklist` | Gate launch with functional, reliability, security, and operations evidence |
| `procore-upgrade-migration` | Cut over one documented endpoint or payload contract at a time |
| `procore-ci-integration` | Run offline adapter gates plus optional protected sandbox checks |
| `procore-deploy-integration` | Align app-version promotion with an immutable integration release |
| `procore-webhooks-events` | Configure hooks and triggers, deduplicate, hydrate, and reconcile gaps |
| `procore-performance-tuning` | Improve useful records per call without sacrificing completeness |
| `procore-cost-tuning` | Recover API and infrastructure budget without invented provider pricing |
| `procore-reference-architecture` | Design tenant-bound queues, adapters, hydration, reconciliation, and receipts |
| `procore-multi-env-setup` | Isolate credentials, hosts, keys, company IDs, installs, and refresh behavior |
| `procore-observability` | Join Integration Health and API activity with route and freshness telemetry |
| `procore-incident-runbook` | Stabilize, classify, mitigate, reconcile, and settle integration incidents |
| `procore-data-handling` | Govern uploads, associations, secure downloads, checksums, and retention |
| `procore-enterprise-rbac` | Map endpoint operations to DMSA or user permissions and permitted projects |
| `procore-migration-deep-dive` | Execute resumable, dependency-ordered, reconciled data migrations |

## Operating standard

Every skill includes explicit triggers, prerequisites, authentication, bounded instructions, outputs, examples, failure handling, and dated first-party source notes. Provider-side mutations are never implied by installation, validation, or a successful read.

Validate the pack from the repository root:

```bash
python3 scripts/validate-skills-schema.py --marketplace --fail-on-warn --min-grade A plugins/saas-packs/procore-pack
python3 -m unittest tests.test_procore_pack_contract -v
```

## First-party documentation

- [Procore developer documentation](https://developers.procore.com/documentation/)
- [Procore REST API reference](https://developers.procore.com/reference/rest)
- [Choose an authentication method](https://developers.procore.com/documentation/oauth-choose-grant-type)
- [Procore sandboxes](https://developers.procore.com/documentation/development-environments)
- [Integration Health](https://developers.procore.com/documentation/integration-health)

## License

MIT
