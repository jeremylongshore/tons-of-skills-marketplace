# Runway Operator Skill Pack

> Eighteen operator-grade Claude Code skills for Runway Dev authentication, model-aware media generation, asynchronous task operations, cost and capacity controls, security, deployment, and incident response.

## Scope

This pack covers the public Runway Dev API at `https://api.dev.runwayml.com`, the official Node and Python SDKs, direct model and Model Router workflows, task retrieval and cancellation, input media, temporary outputs, usage tiers, moderation, and production operations.

It does not claim that the consumer Runway application and Runway Dev share credentials or credits. It also does not claim native generation-completion webhooks: `runway-webhooks-events` shows how to turn authoritative task polling into an internal event or a service-owned signed callback.

## Installation

```bash
/plugin install runway-pack@claude-code-plugins-plus
```

## Skills

| Skill | Operator outcome |
| --- | --- |
| `runway-install-auth` | Bootstrap and rotate a server-only SDK or REST client. |
| `runway-hello-world` | Run one approved, billable, terminal-state smoke test. |
| `runway-local-dev-loop` | Test offline with deterministic task fixtures and an opt-in canary. |
| `runway-ci-integration` | Gate contracts without exposing fork secrets or paying per commit. |
| `runway-core-workflow-a` | Build a model-grounded text-to-video workflow. |
| `runway-core-workflow-b` | Validate and transform image or video inputs. |
| `runway-sdk-patterns` | Implement a typed, restart-safe SDK boundary. |
| `runway-common-errors` | Separate HTTP errors, task failures, and safe retries. |
| `runway-rate-limits` | Control per-model concurrency and rolling quotas. |
| `runway-performance-tuning` | Measure queue-to-asset latency by phase. |
| `runway-cost-tuning` | Optimize credits from current pricing and usage evidence. |
| `runway-debug-bundle` | Build a redacted support evidence package. |
| `runway-deploy-integration` | Deploy a durable asynchronous worker. |
| `runway-reference-architecture` | Design trust, control, data, and governance planes. |
| `runway-security-basics` | Protect organization keys, prompts, media, and outputs. |
| `runway-prod-checklist` | Make an evidence-backed launch decision. |
| `runway-upgrade-migration` | Migrate SDK and model contracts reversibly. |
| `runway-webhooks-events` | Relay polled task changes as idempotent internal events. |

## Contract principles

- Resolve model fields from the current model-specific API schema; do not copy ratios or durations across models.
- Persist the provider task ID before waiting, and never treat task creation as completion.
- Treat `THROTTLED` as queued work and a timeout as a stopped wait—not provider cancellation.
- Copy successful outputs to owned storage before their temporary URLs expire.
- Use current first-party pricing and usage evidence rather than hard-coded cost tables.
- Keep `RUNWAYML_API_SECRET`, customer media, unsafe prompts, and signed URLs out of public artifacts.

Every skill includes a dated `references/official-docs.md` with first-party links and split SHA-256 retrieval fingerprints.

## License

MIT
