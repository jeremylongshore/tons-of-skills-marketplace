# Mindtickle Skill Pack

> Eighteen governed workflows for tenant access, learning programs, readiness, integrations, security, and operations.

This pack is grounded in Mindtickle's public product, integration, Trust, subscription, professional-services, Support, and SLA material. It recognizes tenant-specific URLs and entitlements; distinct browser SSO, user provisioning, managed connector, and API paths; REST-based Content, User, and Reporting API families; and SCIM, SAML, and OpenID standards.

It does **not** claim a universal API host, route set, public SDK package, credential header, webhook contract, numeric throttle, or public unit price. Exact technical behavior must come from current customer-authorized tenant documentation or written Mindtickle guidance.

## Installation

```bash
/plugin install mindtickle-pack@claude-code-plugins-plus
```

## Workflows

| Skill | Production purpose |
|---|---|
| `mindtickle-hello-world` | Discover licensed tenant capabilities and run a safe first proof |
| `mindtickle-install-auth` | Select SSO, provisioning, managed connector, or API access |
| `mindtickle-core-workflow-a` | Launch and reconcile a governed learning program |
| `mindtickle-core-workflow-b` | Govern readiness and coaching measurement |
| `mindtickle-sdk-patterns` | Build a typed adapter from an authorized tenant contract |
| `mindtickle-local-dev-loop` | Develop against sanitized contract fixtures without live access |
| `mindtickle-ci-integration` | Gate changes and isolate an optional protected tenant smoke test |
| `mindtickle-deploy-integration` | Canary, reconcile, promote, and roll back an adapter |
| `mindtickle-common-errors` | Triage failures by customer, integration, and platform boundary |
| `mindtickle-debug-bundle` | Build a privacy-safe support evidence bundle |
| `mindtickle-rate-limits` | Discover and enforce tenant-specific capacity and retry policy |
| `mindtickle-performance-tuning` | Tune measured integration bottlenecks without sacrificing correctness |
| `mindtickle-security-basics` | Threat-model identities, tenancy, data, content, and integrations |
| `mindtickle-prod-checklist` | Issue an evidence-backed production-readiness decision |
| `mindtickle-upgrade-migration` | Migrate contracts, mappings, connectors, or configuration safely |
| `mindtickle-reference-architecture` | Design tenant-scoped trust boundaries and data flows |
| `mindtickle-cost-tuning` | Review contracted spend, entitlements, adoption, and outcomes |
| `mindtickle-webhooks-events` | Select documented events, polling, exports, or managed connectors |

## Validation

```bash
python3 scripts/validate-skills-schema.py --marketplace --min-grade A --verbose \
  plugins/saas-packs/mindtickle-pack
python3 -m unittest tests.test_mindtickle_pack_contract
```

Re-fetch the applicable official page and the customer's authorized tenant contract before relying on an entitlement, field, route, credential, limit, event, or support behavior.

## License

MIT
