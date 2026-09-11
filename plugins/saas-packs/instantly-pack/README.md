# Instantly Operator Pack

> Operator-grade Instantly API v2 workflows for campaigns, sending accounts, leads, scoped access, webhooks, reliability, and governed delivery.

This pack contains 24 source-grounded Claude Code skills. It treats outreach mutations, account connections, cross-workspace delegation, data handling, commercial changes, and external disclosures as explicit approval boundaries.

## Current platform contract

- Base URL: `https://api.instantly.ai/api/v2`
- Authentication: scoped API v2 bearer keys
- General rate limits: 100 requests/second and 6,000 requests/minute, shared across API v1/v2 and all keys in a workspace
- Official SDK: `@instantlyai/sdk` beta, Node.js 22+
- Official CLI: `@instantlyai/cli`, Node.js 18+
- API v1: deprecated on January 19, 2026; v2 requires new, incompatible keys
- Webhooks: documented event schema and management APIs; no unpublished signature or fixed retry contract is assumed

Recheck the linked first-party references before production changes because endpoint schemas, package releases, limits, plans, and commercial terms can change.

## Installation

```bash
/plugin install instantly-pack@claude-code-plugins-plus
```

## Skills

| Area | Skills |
|---|---|
| Setup and proof | `instantly-install-auth`, `instantly-hello-world`, `instantly-local-dev-loop`, `instantly-sdk-patterns` |
| Campaign and account operations | `instantly-core-workflow-a`, `instantly-core-workflow-b`, `instantly-common-errors`, `instantly-debug-bundle` |
| Reliability and launch | `instantly-rate-limits`, `instantly-security-basics`, `instantly-prod-checklist`, `instantly-ci-integration`, `instantly-deploy-integration` |
| Events and scale | `instantly-webhooks-events`, `instantly-performance-tuning`, `instantly-cost-tuning`, `instantly-reference-architecture` |
| Governance and lifecycle | `instantly-multi-env-setup`, `instantly-observability`, `instantly-incident-runbook`, `instantly-data-handling`, `instantly-enterprise-rbac`, `instantly-migration-deep-dive`, `instantly-upgrade-migration` |

`instantly-migration-deep-dive` owns the one-time API v1-to-v2 cutover. `instantly-upgrade-migration` owns ongoing SDK, CLI, OpenAPI-type, and API v2 contract upgrades.

## Safety model

Every skill is inspection-first. Live requests use bounded synthetic or approved data, least-privilege scopes, redacted evidence, and explicit workspace identity. Campaign activation, account connection, lead import/deletion, webhook changes, key/member changes, plan changes, and diagnostic sharing require accountable-owner approval.

## Primary documentation

- [Instantly developer documentation](https://developer.instantly.ai/)
- [API v2 quickstart](https://developer.instantly.ai/quickstart)
- [Authorization](https://developer.instantly.ai/getting-started/authorization)
- [Rate limits](https://developer.instantly.ai/getting-started/rate-limit)
- [API v1-to-v2 migration](https://developer.instantly.ai/guides/api-v1-migration)
- [Webhook event schema](https://developer.instantly.ai/guides/webhook-events)
- [Workspace groups](https://developer.instantly.ai/guides/workspace-group)
- [Official SDK](https://developer.instantly.ai/sdk/introduction)
- [Official CLI](https://developer.instantly.ai/cli/introduction)

## License

MIT
