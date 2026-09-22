# Ideogram Operator Skill Pack

> 24 production-grade Claude Code skills for the current Ideogram API: V4, P-Image, V3 compatibility, image tools, verified async webhooks, durable assets, and governed operations.

This pack turns Ideogram's first-party contracts into bounded operator workflows. It treats API spend, uploaded and generated media, content safety, copyright controls, temporary URLs, async state, team access, and destructive actions as separate approval boundaries.

**Links:** [Ideogram developer docs](https://developer.ideogram.ai) · [API index](https://developer.ideogram.ai/api-reference.md) · [OpenAPI](https://developer.ideogram.ai/openapi.json) · [Current pricing](https://ideogram.ai/api-pricing) · [Tons of Skills](https://tonsofskills.com/learn/ideogram/)

## Installation

```bash
/plugin install ideogram-pack@claude-code-plugins-plus
```

## Current API Coverage

| Surface | Current contract |
|---|---|
| V4 generation | Synchronous, asynchronous, transparent, text or structured JSON prompting |
| P-Image | Synchronous and asynchronous generation |
| V3 | Generation, transparency, edit, remix, reframe, and compatibility workflows |
| Prompt workflows | V4 structured describe and magic prompt |
| Image tools | Background, object, logo, reframe, ad-resize, color, material, upscale, and text-layer operations |
| Async lifecycle | `generation_id`, Ed25519-signed webhook, idempotent reconciliation, polling fallback |
| Custom training | Dataset creation and upload, V3 training, model listing and status |
| Asset lifecycle | Item safety check, immediate download, application-owned storage, deletion |

The REST base is `https://api.ideogram.ai`; authentication uses the `Api-Key` header. The developer overview currently documents 10 in-flight requests by default. Returned image URLs expire, so successful completion requires durable application storage. Endpoint pages remain authoritative for multipart fields and rendering options; notably, V4 `FLASH` is currently rejected.

## Skills

| Skill | Operator outcome |
|---|---|
| `ideogram-install-auth` | Team, billing, key, secret, and revocation boundary |
| `ideogram-hello-world` | One bounded V4 sync generation and durable download |
| `ideogram-local-dev-loop` | Deterministic fixtures with opt-in paid live smoke |
| `ideogram-sdk-patterns` | Application-owned REST and multipart adapter |
| `ideogram-core-workflow-a` | V4, transparency, P-Image, sync, and async route selection |
| `ideogram-core-workflow-b` | Edit, remix, describe, magic prompt, and tool routing |
| `ideogram-common-errors` | Auth, validation, throttling, safety, and expiry diagnosis |
| `ideogram-debug-bundle` | Content-free support evidence |
| `ideogram-rate-limits` | Account-level concurrency, queue, and deadline control |
| `ideogram-security-basics` | Credentials, media, safety, copyright, and tenant controls |
| `ideogram-prod-checklist` | Fail-closed production release decision |
| `ideogram-upgrade-migration` | Bounded endpoint and schema upgrade |
| `ideogram-ci-integration` | Offline required tests and trusted optional live lane |
| `ideogram-deploy-integration` | Server, queue, storage, canary, and rollback topology |
| `ideogram-webhooks-events` | Ed25519 verification, deduplication, and polling fallback |
| `ideogram-performance-tuning` | Measured route, latency, and throughput optimization |
| `ideogram-cost-tuning` | Prepaid budget and useful-output governance |
| `ideogram-reference-architecture` | Policy gateway through audited durable asset |
| `ideogram-multi-env-setup` | Key, budget, route, webhook, and storage isolation |
| `ideogram-observability` | Content-free SLO, safety, queue, storage, and spend signals |
| `ideogram-incident-runbook` | Bounded containment, reconciliation, and recovery |
| `ideogram-data-handling` | Prompt, media, dataset, model, retention, and deletion lifecycle |
| `ideogram-enterprise-rbac` | Vendor team roles plus application-owned RBAC |
| `ideogram-migration-deep-dive` | Legacy and V3 to current-route staged migration |

Every skill includes a dated, local first-party evidence map. Recheck those sources before relying on mutable commercial, limit, enum, or lifecycle facts.

## Safety Defaults

- No live generation, upload, deployment, balance change, role change, key mutation, or destructive cleanup is authorized merely by invoking a skill.
- Credentials remain server-side; receipts exclude prompts, images, temporary URLs, and customer-derived content.
- Unsafe output, missing durable storage, or unreconciled async state is not a successful completion.
- Untrusted pull requests use sanitized fixtures and never receive an Ideogram key.

## License

MIT
