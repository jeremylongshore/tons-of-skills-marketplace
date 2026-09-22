# Canva Operator Pack

Thirty governed workflows for building and operating a Canva Connect backend.
The pack covers OAuth, explicit authorization, designs and asynchronous jobs,
assets and autofill, environment isolation, observability, incident response,
and safe release controls.

## Installation

```bash
/plugin install canva-pack@claude-code-plugins-plus
```

## Operating Boundary

- Canva Connect uses OAuth 2.0 Authorization Code with SHA-256 PKCE.
- The current REST operation base is `https://api.canva.com/rest/v1/`.
- Token exchange stays on a backend; refresh tokens are single-use and rotate.
- Scopes are explicit and non-implied.
- Mutating and asynchronous operations require durable identity and reconciliation.
- Webhooks and the public `connect/keys` endpoint are preview surfaces; Canva
  says public integrations using preview features cannot pass review.
- Endpoint behavior and limits come from the current first-party OpenAPI and
  endpoint references, not hard-coded folklore.

## Workflows

### Build and Integrate

- `canva-install-auth` — backend PKCE, callback state, token rotation, disconnect
- `canva-hello-world` — minimal read-only connection proof
- `canva-local-dev-loop` — mock-first local development
- `canva-sdk-patterns` — typed application-owned REST adapter
- `canva-core-workflow-a` — design creation and export reconciliation
- `canva-core-workflow-b` — assets, datasets, autofill, and folders

### Diagnose and Recover

- `canva-common-errors` — status/provider-code classification
- `canva-debug-bundle` — minimal redacted evidence
- `canva-rate-limits` — endpoint- and user-scoped throttling
- `canva-advanced-troubleshooting` — layered hard-failure isolation
- `canva-incident-runbook` — containment, mitigation, and recovery
- `canva-reliability-patterns` — operation identity, reconciliation, dead letters
- `canva-known-pitfalls` — preventive integration review

### Secure and Govern

- `canva-security-basics` — OAuth, secrets, tenants, and webhook authenticity
- `canva-data-handling` — collection-through-deletion lifecycle controls
- `canva-enterprise-rbac` — capability-aware application authorization
- `canva-policy-guardrails` — repository and runtime enforcement
- `canva-prod-checklist` — evidence-backed production approval

### Deploy and Scale

- `canva-ci-integration` — fork-safe offline and protected-live CI
- `canva-deploy-integration` — immutable release and callback gate
- `canva-multi-env-setup` — environment and credential isolation
- `canva-observability` — privacy-safe metrics, traces, logs, and alerts
- `canva-performance-tuning` — measured cache, pagination, and polling changes
- `canva-load-scale` — mock-first capacity testing
- `canva-cost-tuning` — request and entitlement evidence

### Architect and Migrate

- `canva-reference-architecture` — production backend blueprint
- `canva-architecture-variants` — topology decision from explicit constraints
- `canva-migration-deep-dive` — staged provider/application migration
- `canva-upgrade-migration` — pinned OpenAPI and changelog upgrade
- `canva-webhooks-events` — preview webhook verification and routing

## First-Party Sources

- [Canva Connect documentation](https://www.canva.dev/docs/connect/)
- [Authentication](https://www.canva.dev/docs/connect/authentication/)
- [Security recommendations](https://www.canva.dev/docs/connect/guidelines/security/)
- [Latest OpenAPI contract](https://www.canva.dev/sources/connect/api/latest/api.yml)
- [API versions](https://www.canva.dev/docs/connect/versions/)

Every skill also includes a dated `references/official-docs.md` evidence file.

## License

MIT
