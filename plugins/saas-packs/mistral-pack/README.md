# Mistral Operator Skill Pack

> 24 marketplace Grade A Claude Code skills for current Mistral API integration, reliability, security, governance, and migration work.

This pack turns Mistral's first-party contracts into bounded operator workflows. It keeps credentials server-side, reads mutable model, billing, and workspace-limit facts from current evidence, distinguishes stable and Public Preview surfaces, and requires explicit approval for spend, uploads, stateful resources, administration, deployment, and deletion.

**Links:** [Mistral developer docs](https://docs.mistral.ai/) · [API reference](https://docs.mistral.ai/api/) · [Official clients](https://docs.mistral.ai/getting-started/clients) · [Tons of Skills](https://tonsofskills.com/learn/mistral/)

## Installation

```bash
/plugin install mistral-pack@claude-code-plugins-plus
```

## Current Contract

- REST base: `https://api.mistral.ai`
- Authentication: server-side `Authorization: Bearer`
- Chat: `POST /v1/chat/completions`
- Embeddings: `POST /v1/embeddings`
- Workflows event stream: `GET /v1/workflows/events/stream` over SSE
- Stateful and Public Preview APIs are isolated behind explicit risk and data-lifecycle decisions.
- Models, prices, context limits, quotas, and plan features are read from current first-party and account evidence; this pack intentionally does not freeze them in a table.
- Current ZDR eligibility is operation-specific. Stateful products and APIs require separate retention review.

## Skills

| Skill | Operator outcome |
|---|---|
| `mistral-install-auth` | Workspace, key, secret, billing, and revocation boundary |
| `mistral-hello-world` | One bounded synthetic chat request |
| `mistral-local-dev-loop` | Offline fixtures with an opt-in live smoke |
| `mistral-sdk-patterns` | Pinned typed client adapter |
| `mistral-core-workflow-a` | Chat, streaming, and structured output |
| `mistral-core-workflow-b` | Embeddings, retrieval, and governed tools |
| `mistral-common-errors` | Evidence-led failure classification |
| `mistral-debug-bundle` | Content-free support evidence |
| `mistral-rate-limits` | Workspace-aware admission and backpressure |
| `mistral-security-basics` | Credentials, tenants, content, files, and tool safety |
| `mistral-prod-checklist` | Fail-closed production decision |
| `mistral-upgrade-migration` | SDK and API-surface migration |
| `mistral-ci-integration` | Required offline tests and protected live lane |
| `mistral-deploy-integration` | Runtime, canary, and rollback topology |
| `mistral-webhooks-events` | Workflows SSE checkpoints and reconciliation |
| `mistral-performance-tuning` | Measured latency and throughput tuning |
| `mistral-cost-tuning` | Live-evidence spend governance |
| `mistral-reference-architecture` | Governed workload-to-endpoint architecture |
| `mistral-multi-env-setup` | Workspace, secret, data, and budget isolation |
| `mistral-observability` | Content-free SLO and state telemetry |
| `mistral-incident-runbook` | Bounded containment and recovery |
| `mistral-data-handling` | Data, ZDR, state, retention, and deletion lifecycle |
| `mistral-enterprise-rbac` | Provider administration plus application RBAC |
| `mistral-migration-deep-dive` | Cross-provider evaluation and cutover |

Every skill includes a dated local map of current Mistral sources. Recheck it before relying on a mutable endpoint schema, model, price, quota, preview label, or retention promise.

## Safety Defaults

- Invocation alone never authorizes live calls, paid usage, uploads, state creation, role or billing changes, deployment, cancellation, or deletion.
- Untrusted pull requests and required offline tests never receive `MISTRAL_API_KEY`.
- Receipts exclude credentials, prompts, responses, embeddings, files, tool payloads, and personal billing data.
- The model can propose an action, but trusted application code owns authorization and side effects.
- Provider recovery is incomplete until queues, files, jobs, runs, conversations, and application state converge.

## License

MIT
