# Miro Skill Pack

Twenty-four production operator workflows for Miro REST API v2 and the Web SDK. The pack covers OAuth, tenant-safe board operations, cursor reconciliation, credit budgets, enterprise governance, security, deployment, incidents, and v1-to-v2 migration.

Each skill is source-grounded in current official Miro documentation, declares its approval boundary, and produces a redacted receipt. The pack does not teach the retired experimental REST webhook endpoints; it replaces them with bounded reconciliation or explicitly session-scoped Web SDK events.

## Installation

```bash
/plugin install miro-pack@claude-code-plugins-plus
```

## Workflow Map

| Domain | Skills |
|---|---|
| Authorization and setup | `miro-install-auth`, `miro-hello-world`, `miro-local-dev-loop`, `miro-multi-env-setup` |
| Board operations | `miro-core-workflow-a`, `miro-core-workflow-b`, `miro-sdk-patterns`, `miro-performance-tuning` |
| Reliability and delivery | `miro-common-errors`, `miro-debug-bundle`, `miro-ci-integration`, `miro-deploy-integration`, `miro-prod-checklist` |
| Capacity and operations | `miro-rate-limits`, `miro-cost-tuning`, `miro-observability`, `miro-incident-runbook` |
| Security and governance | `miro-security-basics`, `miro-data-handling`, `miro-enterprise-rbac` |
| Architecture and change | `miro-reference-architecture`, `miro-upgrade-migration`, `miro-migration-deep-dive`, `miro-webhooks-events` |

## Current Platform Boundaries

- [REST resources](https://developers.miro.com/reference/overview) use `https://api.miro.com/v2`; OAuth exchange remains at `https://api.miro.com/v1/oauth/token`.
- [Expiring-token apps](https://developers.miro.com/docs/authorization-flow-for-expiring-access-tokens) use one-hour access tokens and rotating refresh tokens with a sixty-day lifetime.
- [REST limits](https://developers.miro.com/reference/rate-limiting) are per user/application and credit weighted. Responses expose limit, remaining, and reset headers.
- [Bulk creation](https://developers.miro.com/reference/create-items) accepts at most twenty items and is transactional; each item consumes the endpoint's Level 2 credits.
- Miro discontinued `/v2-experimental/webhooks/board_subscriptions` [on December 5, 2025](https://developers.miro.com/changelog/removed-experimental-webhooks-support). There is no documented production REST webhook replacement. [Web SDK UI events](https://developers.miro.com/docs/websdk-reference-ui) are active-board session behavior, not durable server event delivery.

See each skill's `references/official-docs.md` for the verified primary-source set.

## License

MIT
