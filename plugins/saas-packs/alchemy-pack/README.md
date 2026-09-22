# Alchemy Skill Pack

Eighteen evidence-backed Claude Code workflows for operating Alchemy Node, Data, Portfolio, NFT, Wallet, Notify, and Admin surfaces across current supported chains.

Every skill includes a dated first-party evidence map, explicit credential and approval boundaries, negative-path validation, and a rollback-aware output contract. The pack no longer teaches the deprecated and archived `alchemy-sdk`, Polygon Mumbai, fixed plan or method-cost tables, an undocumented dashboard stats endpoint, or blanket claims that every application key must stay out of browser code.

## Installation

```bash
/plugin install alchemy-pack@claude-code-plugins-plus
```

## Operator lanes

| Lane | Skills | Outcome |
|---|---:|---|
| Intake and client routing | 3 | Correct credential class, chain/feature proof, viem/Data API/Wallet APIs routing |
| Product workflows | 2 | Portfolio partial-state handling and NFT/indexer/contract-read reconciliation |
| Development and delivery | 3 | Deterministic local forks, trust-aware CI, environment-scoped promotion and rollback |
| Reliability and operations | 6 | Error triage, redacted diagnostics, account-level backpressure, performance, cost, readiness |
| Security and events | 2 | Credential/trust-boundary controls and authentic idempotent Notify intake |
| Architecture and migration | 2 | Capability-separated production design and archived-SDK migration |

## Current non-negotiables

- The `alchemy-sdk` JavaScript repository is archived and deprecated. Use `viem` for JavaScript EVM reads, current Data API adapters for product endpoints, `@alchemy/wallet-apis` for transacting applications and Portfolio support, and Solana Web3.js for Solana.
- An application API key, Admin access key, Notify management token, per-webhook signing key, and wallet signing authority are distinct credentials.
- RPC support on a chain does not prove feature support for NFT, Portfolio, Wallet, Simulation, or Notify surfaces.
- Portfolio fanout can return HTTP 200 with top-level `error.partialErrors`; HTTP success is not proof of a complete multi-chain result.
- Throughput is account-level over a rolling ten-second token-bucket window. Pricing, method costs, included capacity, and elastic behavior must be checked against current account evidence.
- Notify authenticity uses HMAC-SHA256 over the exact raw body and the per-webhook signing key in `X-Alchemy-Signature`.
- Restricted browser application-key patterns require an explicit threat model and current Alchemy controls such as allowlists or short-lived JWTs; confidential, Admin, Notify, webhook, and signing credentials remain isolated.

## Quality contract

All eighteen skills target marketplace Grade A and Tier-2 GREEN with zero warnings and errors. Each skill uses only `Read`, `Glob`, `Grep`, `Write`, and `Edit`; invoking a skill never authorizes network access, credentials, address or customer data, plan changes, spend, key or webhook lifecycle changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Skills

| Skill | Operator outcome |
|---|---|
| `alchemy-install-auth` | Select the current client and prove chain, feature, credential class, and lifecycle |
| `alchemy-hello-world` | Produce a minimal viem connectivity proof with a chain-ID assertion |
| `alchemy-local-dev-loop` | Build reproducible pinned-block tests with synthetic fixtures |
| `alchemy-sdk-patterns` | Route capabilities to viem, Data APIs, Wallet APIs v5, or Solana Web3.js |
| `alchemy-core-workflow-a` | Preserve pagination and partial-network state in portfolio aggregation |
| `alchemy-core-workflow-b` | Reconcile NFT index results, metadata provenance, and typed contract reads |
| `alchemy-common-errors` | Classify transport, RPC, policy, throughput, and partial-response failures |
| `alchemy-debug-bundle` | Create an immutable, redacted provider diagnostic receipt |
| `alchemy-rate-limits` | Operate shared account-level admission control and bounded retries |
| `alchemy-security-basics` | Enforce credential, browser, signer, input, and webhook trust boundaries |
| `alchemy-prod-checklist` | Make an evidence-backed production go/no-go decision |
| `alchemy-upgrade-migration` | Move archived clients to current capability-specific integrations |
| `alchemy-ci-integration` | Separate deterministic, live-read, fork, and deployment CI authorities |
| `alchemy-deploy-integration` | Promote immutable artifacts through chain-aware canaries and rollback |
| `alchemy-webhooks-events` | Verify, deduplicate, acknowledge, process, and replay Notify events safely |
| `alchemy-performance-tuning` | Tune caching, batching, and concurrency without hiding stale or partial state |
| `alchemy-cost-tuning` | Attribute current compute usage and govern spend without stale constants |
| `alchemy-reference-architecture` | Design capability, credential, state, queue, signer, and provider boundaries |

## Primary sources

- [Alchemy documentation](https://www.alchemy.com/docs)
- [Archived SDK replacement guidance](https://github.com/alchemyplatform/alchemy-sdk-js)
- [Ethereum quickstart with viem](https://www.alchemy.com/docs/reference/ethereum-api-quickstart)
- [Data APIs](https://www.alchemy.com/docs/data)
- [Portfolio APIs](https://www.alchemy.com/docs/reference/portfolio-apis)
- [Wallet APIs](https://www.alchemy.com/docs/wallets/reference/wallet-apis)
- [Notify webhooks](https://www.alchemy.com/docs/reference/webhooks-overview)
- [Throughput](https://www.alchemy.com/docs/reference/throughput)

MIT licensed.
