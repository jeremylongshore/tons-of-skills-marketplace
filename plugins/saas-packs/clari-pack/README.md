# Clari Skill Pack

> 18 governed Claude Code workflows for Clari Revenue API exports, v2 ingestion, Copilot, and production operations

## Provider Surfaces

This pack keeps Clari's public integration surfaces separate:

- The [Clari Revenue API](https://developer.clari.com/default/documentation/external_spec) uses token authentication in the `apikey` header. Its published contract covers asynchronous forecast, activity, and audit exports; direct audit and opportunity reads; organization export limits; and ingestion operations.
- Clari's ingestion examples use the v2 base URL and require both `apikey` and `partnerkey`.
- The [Clari Copilot API](https://api-doc.copilot.clari.com/) uses `X-Api-Key` plus `X-Api-Password` on `rest-api.copilot.clari.com`. It exposes calls, call details, users, topics, scorecards, and account/contact/deal operations.
- The current public Revenue contract does not define a general webhook subscription endpoint. The preserved `clari-webhooks-events` route therefore implements supported audit polling and asynchronous activity exports.

Each skill includes first-party evidence, explicit authentication and tool boundaries, failure handling, and a reviewable output contract. The workflows do not claim provider certification or successful tenant execution without runtime receipts.

## Installation

Install the plugin from the marketplace:

```bash
/plugin install clari-pack@claude-code-plugins-plus
```

Install an individual skill with the public skills CLI:

```bash
npx skills add jeremylongshore/tons-of-skills-marketplace --skill clari-hello-world
```

## Skills

| Skill | Operator outcome |
| --- | --- |
| `clari-install-auth` | Create and validate least-privilege Revenue, ingestion, or Copilot credentials |
| `clari-hello-world` | Complete one forecast request, poll, and result-retrieval lifecycle |
| `clari-local-dev-loop` | Develop offline with synthetic contracts and deterministic job states |
| `clari-sdk-patterns` | Build typed local REST wrappers without claiming an official SDK |
| `clari-core-workflow-a` | Land, normalize, reconcile, and publish forecast data to a warehouse |
| `clari-core-workflow-b` | Extract governed Copilot call, user, topic, and scorecard datasets |
| `clari-common-errors` | Triage auth, entitlement, quota, job, schema, and empty-result failures |
| `clari-debug-bundle` | Produce a minimal, redacted provider support bundle |
| `clari-rate-limits` | Schedule exports, ingestion, and Copilot reads within separate limits |
| `clari-security-basics` | Threat-model credentials, revenue data, call content, and mutations |
| `clari-prod-checklist` | Make a fail-closed production readiness decision |
| `clari-upgrade-migration` | Dual-read and migrate hosts, versions, clients, or schemas safely |
| `clari-ci-integration` | Gate clients and pipelines with offline contract tests |
| `clari-deploy-integration` | Deploy a single-writer scheduler with durable checkpoints |
| `clari-webhooks-events` | Build supported audit and activity change feeds without fake webhooks |
| `clari-performance-tuning` | Tune measured latency inside correctness and provider limits |
| `clari-cost-tuning` | Govern export quota, requests, transfer, storage, and warehouse work |
| `clari-reference-architecture` | Separate provider adapters, control state, landing, and publication |

## Asynchronous Export Lifecycle

A safe Revenue export flow is explicit:

1. Freeze the forecast or activity request and read applicable capacity.
2. Queue the export and persist the returned job ID.
3. Poll the job with bounded backoff through `SCHEDULED` or `STARTED`.
4. Retrieve results only after `DONE`; diagnose `ABORTED` without blindly re-queuing.
5. Land immutably, validate and reconcile, then publish atomically.
6. Retain redacted lineage and remove temporary sensitive data under policy.

## Validation

All 18 skills are held to marketplace Grade A and the static production gate:

```bash
python3 scripts/validate-skills-schema.py \
  --marketplace --fail-on-warn --min-grade A \
  plugins/saas-packs/clari-pack
python3 -m unittest tests.test_clari_pack_contract
```

## First-Party References

- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
- [Clari public GitHub organization](https://github.com/clari)
- [Clari service status](https://clari.statuspage.io/)

## License

MIT
