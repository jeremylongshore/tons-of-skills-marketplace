# Salesforce Skill Pack

> 30 governed operator workflows for Salesforce API access, records, bulk operations, events, security, delivery, data, and production operations.

## Installation

```bash
/plugin install salesforce-pack@claude-code-plugins-plus
```

## Scope and Contract Boundary

This pack starts from the target org and its current contract. It discovers supported API versions, app type, OAuth flow, edition, entitlements, objects, fields, permissions, sharing, limits, event channels, and customer change policy before execution.

Salesforce restricts creation of Connected Apps as of Spring '26 and recommends External Client Apps for new integrations. Existing Connected Apps can continue, but no workflow in this pack defaults to username-password automation, hard-codes a release API version, exposes secrets, assumes a universal allocation, or treats an administrator session as proof of runtime access.

Mutating workflows require an explicit preview, named approvers, a bounded non-production canary, stable identifiers, result evidence, reconciliation, and rollback or a compensating action.

## Skills

| Skill | Operator outcome |
|---|---|
| `salesforce-install-auth` | Select and verify an External Client App or approved existing Connected App authorization contract |
| `salesforce-hello-world` | Prove identity, version, resource, object, and field access without mutation |
| `salesforce-local-dev-loop` | Build a source-driven scratch-org or sandbox development loop |
| `salesforce-sdk-patterns` | Contain API and client-library churn behind a typed adapter |
| `salesforce-core-workflow-a` | Run metadata-aware SOQL and governed record operations |
| `salesforce-core-workflow-b` | Select and reconcile Bulk API 2.0 or Composite operations |
| `salesforce-common-errors` | Diagnose authorization, schema, validation, locking, limits, jobs, and event failures |
| `salesforce-debug-bundle` | Produce a privacy-safe Salesforce support bundle |
| `salesforce-rate-limits` | Allocate shared org capacity from current Limits and header evidence |
| `salesforce-security-basics` | Secure identity, permissions, sharing, fields, data, secrets, and revocation |
| `salesforce-prod-checklist` | Gate production readiness, canary, reconciliation, and rollback |
| `salesforce-upgrade-migration` | Migrate API, seasonal release, CLI, library, metadata, and integration contracts |
| `salesforce-ci-integration` | Separate fork-safe checks from protected org validation and promotion |
| `salesforce-deploy-integration` | Release an immutable Salesforce-connected application safely |
| `salesforce-webhooks-events` | Choose among Pub/Sub, CDC, Platform Events, relay, Streaming, Outbound Messages, or polling |
| `salesforce-performance-tuning` | Tune query, batching, caching, automation, and async behavior from measurements |
| `salesforce-cost-tuning` | Govern commercial and operating cost using dated customer evidence |
| `salesforce-reference-architecture` | Define authority, trust, data, event, capacity, and recovery boundaries |
| `salesforce-multi-env-setup` | Govern scratch-org, sandbox, staging, and production topology |
| `salesforce-observability` | Connect platform, application, limit, job, event, and business signals |
| `salesforce-incident-runbook` | Contain, recover, and reconcile Salesforce incidents |
| `salesforce-data-handling` | Operate classified data, retention, subject requests, holds, and deletion safely |
| `salesforce-enterprise-rbac` | Govern effective access through layered permission and sharing controls |
| `salesforce-migration-deep-dive` | Run dependency-ordered, external-ID-based data migrations |
| `salesforce-advanced-troubleshooting` | Falsify complex hypotheses with minimum diagnostic evidence |
| `salesforce-load-scale` | Measure bounded capacity with synthetic non-production load |
| `salesforce-reliability-patterns` | Design idempotency, retries, durable state, reconciliation, and recovery |
| `salesforce-policy-guardrails` | Gate unsafe queries, secrets, versions, access, mutations, retries, and event handling |
| `salesforce-architecture-variants` | Compare direct, middleware, event, replicated-data, and hybrid patterns |
| `salesforce-known-pitfalls` | Audit recurring cross-boundary Salesforce integration failures |

## First-Party References

- [REST API authorization](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)
- [REST API end-of-life policy](https://developer.salesforce.com/docs/platform/api-rest/guide/api-rest-eol.html)
- [REST Limits resource](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-limits.html)
- [Bulk API 2.0](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_api_2_0.htm)
- [Pub/Sub API](https://developer.salesforce.com/docs/platform/pub-sub-api/overview)
- [Change Data Capture](https://developer.salesforce.com/docs/atlas.en-us.change_data_capture.meta/change_data_capture/cdc_intro.htm)
- [Salesforce integration patterns](https://developer.salesforce.com/docs/atlas.en-us.integration_patterns_and_practices.meta/integration_patterns_and_practices/)
- [Salesforce Status](https://status.salesforce.com)

## Validation

```bash
python3 scripts/validate-skills-schema.py --marketplace --min-grade A plugins/saas-packs/salesforce-pack
python3 scripts/validate-skills-schema.py --marketplace --deep plugins/saas-packs/salesforce-pack
python3 -m unittest tests.test_salesforce_pack_contract
```

## License

MIT
