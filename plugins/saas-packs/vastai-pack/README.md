# Vast.ai Operator Skill Pack

> Twenty-four evidence-gated workflows for Vast.ai GPU rentals, Serverless, recovery, security, governance, and cost control.

## Installation

```bash
/plugin install vastai-pack@claude-code-plugins-plus
```

The standalone skills CLI can also install individual public skills from `jeremylongshore/tons-of-skills-marketplace`.

## Operating boundary

This pack is grounded in the first-party [Vast.ai documentation](https://docs.vast.ai/) and the provider-maintained [Vast.ai CLI and SDK repository](https://github.com/vast-ai/vast-cli). It complements the provider's command-reference skills by adding approval boundaries, failure handling, recovery evidence, and production governance.

Marketplace Grade A is a repository quality result. It is not Vast.ai certification, and no paid-resource success is claimed without a credentialed runtime receipt.

## Skills

| Skill | Operator outcome |
| --- | --- |
| `vastai-install-auth` | Install the supported client and prove a least-privilege key boundary. |
| `vastai-hello-world` | Rent, verify, and destroy one GPU canary inside a cost fence. |
| `vastai-local-dev-loop` | Promote local CPU/image tests to one disposable GPU canary. |
| `vastai-sdk-patterns` | Implement typed, bounded high-level, sync, async, or Serverless SDK lifecycles. |
| `vastai-core-workflow-a` | Run checkpointed training with external recovery and spend reconciliation. |
| `vastai-core-workflow-b` | Roll out a Serverless endpoint with measured scaling and graceful worker updates. |
| `vastai-common-errors` | Classify auth, offer, state, SSH, image, credit, and API failures. |
| `vastai-debug-bundle` | Build a minimal redacted support manifest with hashed evidence. |
| `vastai-rate-limits` | Bound CLI and REST traffic around endpoint/identity limits and 429 behavior. |
| `vastai-security-basics` | Harden keys, SSH, images, host selection, data, and teardown. |
| `vastai-prod-checklist` | Issue an evidence-backed production GO or NO-GO. |
| `vastai-upgrade-migration` | Upgrade or roll back clients, SDK imports, and immutable templates. |
| `vastai-ci-integration` | Run disposable GPU CI with protected secrets and unconditional cleanup. |
| `vastai-deploy-integration` | Deploy and roll back an immutable instance-based service or worker. |
| `vastai-webhooks-events` | Verify signed at-least-once notifications and enqueue idempotently. |
| `vastai-performance-tuning` | Optimize measured useful-work throughput and cost. |
| `vastai-cost-tuning` | Detect GPU, stopped-storage, volume, bandwidth, and spot-policy leakage. |
| `vastai-reference-architecture` | Separate planning, paid mutation, execution, recovery, evidence, and teardown. |
| `vastai-multi-env-setup` | Isolate dev, staging, and production contexts, keys, data, and budgets. |
| `vastai-observability` | Monitor provider state, workload SLOs, balance, cost, and cleanup. |
| `vastai-incident-runbook` | Recover from outbid, exited, offline, scheduling, and low-credit incidents. |
| `vastai-data-handling` | Move and verify datasets, checkpoints, volumes, and cloud-copy artifacts. |
| `vastai-enterprise-rbac` | Govern native Teams roles and scoped automation keys. |
| `vastai-migration-deep-dive` | Migrate from another GPU provider with parity, canary, and rollback evidence. |

## Safety defaults

- Search and planning remain read-only until an operator approves paid mutation.
- Every instance create records its ID before polling or workload execution.
- Readiness loops have deadlines and terminal-state branches.
- Important state is checkpointed outside disposable instance root disks.
- Stopped instances are treated as storage-billable until destroyed.
- Destruction and credit transfer remain explicit, reviewed actions.
- Receipts exclude API keys, SSH private keys, webhook secrets, and storage credentials.

## First-party references

- [Vast.ai documentation](https://docs.vast.ai/)
- [Vast.ai API reference](https://docs.vast.ai/api-reference/introduction)
- [Vast.ai CLI reference](https://docs.vast.ai/cli/hello-world)
- [Official Vast.ai CLI and SDK](https://github.com/vast-ai/vast-cli)
- [Notification webhooks](https://docs.vast.ai/guides/reference/notification-webhooks)
- [Serverless architecture](https://docs.vast.ai/guides/serverless/architecture)

## License

MIT
