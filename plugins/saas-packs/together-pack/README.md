# Together AI Operator Skill Pack

> 16 source-grounded Claude Code skills for current Together AI application and model operations.

## What This Is

This pack covers project-scoped authentication, Python SDK v2 and OpenAI-compatible clients, real-time chat, asynchronous Batch API jobs, fine-tuning, current v2 Dedicated Model Inference, testing, production readiness, security, and cost control.

The pack deliberately avoids stale shortcuts:

- Python examples target `together>=2.0.0`; v1 is maintenance-only.
- Serverless limits are dynamic per organization and model and are read from response headers.
- Models, redirects, prices, context limits, and batch eligibility are resolved from current Together sources.
- Batch results are reconciled by `custom_id`, including the separate error file.
- Fine-tuning completion and model deployment are separate approval phases.
- New dedicated capacity uses v2 endpoint/deployment resources rather than retired v1 creation.
- Together job polling can drive an internally signed callback; the pack does not invent a provider webhook signature.

## Installation

```bash
/plugin install together-pack@claude-code-plugins-plus
```

## Skills

| Skill | Operator outcome |
|---|---|
| `together-install-auth` | Install SDK v2, configure a project key, and run a read-only access probe |
| `together-hello-world` | Prove bounded chat inference or streaming with a current model |
| `together-local-dev-loop` | Keep tests offline with an opt-in protected live lane |
| `together-sdk-patterns` | Build a typed provider adapter and OpenAI-compatible seam |
| `together-core-workflow-a` | Validate, submit, monitor, and evaluate a fine-tuning job |
| `together-core-workflow-b` | Run and reconcile asynchronous Batch API inference |
| `together-common-errors` | Diagnose request, auth, billing, model, limit, and job failures |
| `together-rate-limits` | Adapt concurrency to current per-model request and token headers |
| `together-security-basics` | Enforce credential, data, output, logging, and side-effect controls |
| `together-prod-checklist` | Issue an evidence-backed production go/no-go decision |
| `together-upgrade-migration` | Migrate SDKs, models, clients, or legacy dedicated endpoints |
| `together-ci-integration` | Split offline contract CI from a protected bounded live lane |
| `together-deploy-integration` | Release serverless services or v2 dedicated deployments reversibly |
| `together-webhooks-events` | Convert bounded job polling into idempotent internal events |
| `together-cost-tuning` | Model token, cache, batch, model, and dedicated-capacity economics |
| `together-reference-architecture` | Design governed real-time, batch, training, and reserved-capacity lanes |

## Primary Sources

- [Together AI quickstart](https://docs.together.ai/docs/quickstart)
- [Project-scoped API keys](https://docs.together.ai/docs/api-keys-authentication)
- [Dynamic serverless limits](https://docs.together.ai/docs/serverless/rate-limits)
- [Batch processing](https://docs.together.ai/docs/inference/batch/overview)
- [Dedicated Model Inference](https://docs.together.ai/docs/dedicated-endpoints/overview)
- [Official Together agent skills](https://github.com/togethercomputer/skills)

## License

MIT
