# Fireflies.ai Operator Skill Pack

> 24 governed workflows for the current Fireflies.ai GraphQL API and Webhooks V2.

This pack helps operators integrate meeting metadata, transcripts, AskFred, audio ingestion, access controls, and event-driven automation without treating API access as permission to expose meeting data. It is grounded in the current first-party Fireflies documentation reviewed on 2026-09-12.

## Installation

```bash
/plugin install fireflies-pack@claude-code-plugins-plus
```

## What You Get

Each skill distinguishes read-only inspection, implementation, live data access, and privileged mutation. The pack assumes standards-based GraphQL clients rather than inventing a Fireflies SDK. Every workflow includes authentication, data-minimization, approval, error, evidence, and rollback boundaries.

Current contracts covered include `transcript` and `transcripts`, non-deprecated search filters, AskFred threads and AI-credit handling, `uploadAudio`, `addToLiveMeeting`, team access mutations, operation-specific limits, and Webhooks V2 HMAC verification.

## Skills Included

### Core workflows

| Skill | What It Does |
|-------|-------------|
| `fireflies-install-auth` | Configure GraphQL API auth, verify connectivity with `user` query |
| `fireflies-hello-world` | First metadata-only GraphQL query |
| `fireflies-local-dev-loop` | Synthetic fixtures and deterministic local tests |
| `fireflies-sdk-patterns` | Typed standards-based GraphQL client boundary |
| `fireflies-core-workflow-a` | Field-minimized transcript retrieval |
| `fireflies-core-workflow-b` | Current search filters and governed AskFred analysis |
| `fireflies-common-errors` | Transport, GraphQL, plan, permission, and processing failures |
| `fireflies-debug-bundle` | Privacy-safe support evidence |
| `fireflies-rate-limits` | Plan and operation-specific request budgets |
| `fireflies-security-basics` | Bearer keys, HMAC, selection, and log hardening |
| `fireflies-prod-checklist` | Fail-closed production readiness |
| `fireflies-upgrade-migration` | Deprecated-filter and Webhooks V2 migration |

### Delivery and architecture

| Skill | What It Does |
|-------|-------------|
| `fireflies-ci-integration` | Offline GraphQL and webhook contract gates |
| `fireflies-deploy-integration` | Reversible workers and signed webhook receivers |
| `fireflies-webhooks-events` | Webhooks V2 event, signature, dedupe, and ordering controls |
| `fireflies-performance-tuning` | Field, pagination, polling, cache, and concurrency tuning |
| `fireflies-cost-tuning` | Quota, AskFred credit, seat, and retention decisions |
| `fireflies-reference-architecture` | Governed event-driven trust boundaries |

### Enterprise operations

| Skill | What It Does |
|-------|-------------|
| `fireflies-multi-env-setup` | Identity, secret, webhook, queue, and data isolation |
| `fireflies-observability` | Content-free metrics, traces, alerts, and audit receipts |
| `fireflies-incident-runbook` | Containment, evidence, recovery, and post-incident controls |
| `fireflies-data-handling` | Purpose, redaction, retention, export, and deletion propagation |
| `fireflies-enterprise-rbac` | Roles, channels, privacy, shares, and mutation approvals |
| `fireflies-migration-deep-dive` | Governed audio upload and live-meeting onboarding |

## Key API Details

| Detail | Value |
|--------|-------|
| Endpoint | `https://api.fireflies.ai/graphql` |
| Auth | `Authorization: Bearer <API_KEY>` |
| Protocol | GraphQL (POST only) |
| Rate limits | Free/Pro: 50/day, Business/Enterprise: 60/min |
| Transcript list page size | Maximum 50 |
| Webhooks V2 events | `meeting.transcribed`, `meeting.summarized` |
| Webhook auth | `X-Hub-Signature: sha256=<hex>` over the raw body |
| Webhook acknowledgement | `2xx` within 10 seconds |

## Usage

Skills trigger automatically when you discuss Fireflies.ai topics:

- "Help me set up the Fireflies API" -- triggers `fireflies-install-auth`
- "Fetch an authorized meeting transcript" -- triggers `fireflies-core-workflow-a`
- "Search meetings for quarterly review" -- triggers `fireflies-core-workflow-b`
- "Set up a Webhooks V2 receiver" -- triggers `fireflies-webhooks-events`
- "Upload a recording to Fireflies" -- triggers `fireflies-migration-deep-dive`
- "Ask Fred about my last meeting" -- triggers `fireflies-core-workflow-b`

## License

MIT
