# Navan Operator Skill Pack

> 26 marketplace Grade A Claude Code skills for governed Navan travel, expense, identity, data, security, reliability, and migration work.

This pack converts Navan's public product surfaces and tenant-specific integration contracts into bounded operator workflows. It recognizes Booking API, Expense API, SFTP, direct integrations, SCIM, SAML, and OpenID Connect without inventing universal endpoints, schemas, webhook signatures, grants, or quotas. Live facts come from the selected customer's current in-account documentation.

**Links:** [Navan integrations](https://navan.com/integrations) · [Security](https://navan.com/security) · [Privacy](https://navan.com/privacy) · [Status](https://status.navan.com/) · [Tons of Skills](https://tonsofskills.com/learn/navan/)

## Installation

```bash
/plugin install navan-pack@claude-code-plugins-plus
```

## Current Contract

- Navan publicly offers Booking API and Expense API integration surfaces alongside direct integrations and secure file-transfer options.
- User-management and security integrations include HRIS, HR-SFTP, SCIM, SAML, OpenID Connect, and vendor-specific SSO connections.
- Exact hosts, methods, credentials, scopes, schemas, lifecycle states, pagination, limits, prices, and delivery behavior are account- and contract-specific.
- Traveler profiles, itineraries, payment information, receipts, location, and support content require explicit purpose, access, retention, and processor controls.
- Third-party AI and MCP connections can process Navan personal information and require a separately approved data boundary.
- Invocation never authorizes booking, payment, expense approval, reimbursement, identity or policy changes, transfer, deployment, or deletion.

## Skills

| Skill | Operator outcome |
|---|---|
| `navan-install-auth` | Tenant-specific integration access and credential intake |
| `navan-hello-world` | One bounded read-only connectivity proof |
| `navan-local-dev-loop` | Offline sanitized fixtures and denied networking |
| `navan-sdk-patterns` | Application-owned, contract-bound adapter |
| `navan-core-workflow-a` | Booking-data ingestion and reconciliation |
| `navan-core-workflow-b` | Expense-data reconciliation and finance controls |
| `navan-common-errors` | Layered contract-failure triage |
| `navan-debug-bundle` | Content-free, privacy-safe support evidence |
| `navan-rate-limits` | Tenant-evidenced capacity and backpressure |
| `navan-security-basics` | End-to-end travel and expense threat model |
| `navan-prod-checklist` | Evidence-backed production readiness gate |
| `navan-upgrade-migration` | Contract and schema upgrade control |
| `navan-ci-integration` | Required offline tests and protected live lane |
| `navan-deploy-integration` | Tenant-isolated canary and rollback deployment |
| `navan-webhooks-events` | Actual delivery-mode verification and reconciliation |
| `navan-performance-tuning` | Measured pipeline performance tuning |
| `navan-cost-tuning` | T&E and integration cost governance |
| `navan-reference-architecture` | Governed multi-system integration architecture |
| `navan-multi-env-setup` | Tenant and environment isolation |
| `navan-observability` | Content-free service and reconciliation signals |
| `navan-incident-runbook` | Containment, reconciliation, and recovery |
| `navan-data-handling` | Personal and corporate data governance |
| `navan-enterprise-rbac` | Enterprise access and toxic-combination controls |
| `navan-migration-deep-dive` | Platform migration with staged cutover |
| `navan-data-sync` | Multi-surface checkpoints, lineage, and reconciliation |
| `navan-entity-management` | Workforce and organization lifecycle governance |

Every skill contains a dated five-link first-party evidence map. Recheck it and the selected tenant's documentation before relying on mutable integration behavior.

## Safety Defaults

- Ordinary review and offline CI receive no Navan credential and open no network connection.
- Live reads, file transfers, traveler or expense access, and all state changes require explicit approval.
- Receipts exclude credentials, personal data, itinerary content, payment details, receipts, and free text.
- Unknown delivery outcomes are reconciled before retry; checkpoints advance only after durable destination acknowledgement.
- Public product pages establish capabilities, not tenant entitlements or executable API contracts.

## License

MIT
