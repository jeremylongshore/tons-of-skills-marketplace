# QuickNode Operator Pack

> 18 governed workflows for operating QuickNode blockchain RPC and data infrastructure safely.

## Scope

This pack treats QuickNode as several distinct operational surfaces instead of one generic Web3 API:

- endpoint data-plane access with endpoint tokens, JSON-RPC, and WebSocket subscriptions;
- account and control-plane automation through the Admin API, `qn` CLI, and QuickNode SDK;
- Streams and Webhooks event delivery with explicit authentication, acknowledgement, retry, and deduplication contracts;
- production observability, security, credit attribution, deployment, and migration controls.

Endpoint tokens and account API keys are different credentials. Supported chains, methods, archive history, pruning behavior, security controls, metrics, logs, and product availability vary by chain and plan. Every workflow requires those boundaries to be verified before a change is made.

## Installation

```bash
/plugin install quicknode-pack@claude-code-plugins-plus
```

## Operator Map

| Workflow | Operational outcome |
| --- | --- |
| `quicknode-install-auth` | Select the correct endpoint or control-plane credential, prove access, and establish rotation ownership |
| `quicknode-hello-world` | Run one raw, read-only JSON-RPC probe without leaking an endpoint token |
| `quicknode-sdk-patterns` | Design around the current unified SDK and its product-specific clients |
| `quicknode-rate-limits` | Diagnose and control per-second, per-minute, daily, and method-specific limits |
| `quicknode-common-errors` | Triage transport, JSON-RPC, chain, security-filter, and application failures |
| `quicknode-security-basics` | Harden endpoint tokens, JWTs, referrers, domains, methods, and IP policy |
| `quicknode-core-workflow-a` | Submit EVM transactions with simulation, nonce, fee, confirmation, and replacement safeguards |
| `quicknode-core-workflow-b` | Verify chain, node type, archive depth, pruning, and add-on requirements before historical reads |
| `quicknode-webhooks-events` | Engineer Webhooks or Streams consumers for authentication, retries, duplicates, reorgs, and backpressure |
| `quicknode-performance-tuning` | Improve tail latency using endpoint metrics, method mix, payload size, and connection behavior |
| `quicknode-cost-tuning` | Attribute credits by product, endpoint, method, chain, and tag without inventing universal prices |
| `quicknode-debug-bundle` | Produce a bounded, redacted incident bundle while respecting log-plan boundaries |
| `quicknode-ci-integration` | Separate fork-safe offline contract tests from protected, read-only live probes |
| `quicknode-deploy-integration` | Ship endpoint-dependent services through preflight, canary, observation, and rollback |
| `quicknode-local-dev-loop` | Build deterministic local tests around an injected JSON-RPC transport |
| `quicknode-prod-checklist` | Run a fail-closed readiness review covering chain, auth, security, limits, events, and recovery |
| `quicknode-reference-architecture` | Separate control-plane, read, write, event, and observability paths with distinct failure policy |
| `quicknode-upgrade-migration` | Migrate SDKs, endpoints, chains, or products with compatibility evidence and a rehearsed rollback |

## Current Product Boundaries

- The unified QuickNode SDK exposes product clients such as Admin, RPC, Streams, Webhooks, Key-Value Store, and SQL; availability depends on the SDK target and product.
- The `qn` CLI and Admin API operate account resources. The Admin API uses an `x-api-key` credential and is available on paid plans.
- Endpoint metrics expose latency percentiles and request behavior. Detailed logs have additional plan boundaries.
- Streams destinations include Webhook, S3, Azure Blob Storage, PostgreSQL, and Kafka. Delivery is sequential by batch, destinations must acknowledge successfully, and consumers must tolerate retries and duplicates.
- Webhooks and Streams are separate products. Choose based on the delivery and transformation contract instead of using their names interchangeably.

## Documentation

- [QuickNode SDK](https://www.quicknode.com/docs/sdk)
- [QuickNode CLI](https://www.quicknode.com/docs/cli)
- [Admin API](https://www.quicknode.com/docs/admin-api)
- [Streams](https://www.quicknode.com/docs/streams)
- [Webhooks](https://www.quicknode.com/docs/webhooks)
- [Supported chains and node types](https://www.quicknode.com/docs/platform/supported-chains-node-types)

Each skill also carries a consulted, workflow-specific source record in `references/official-docs.md`.

## License

MIT
