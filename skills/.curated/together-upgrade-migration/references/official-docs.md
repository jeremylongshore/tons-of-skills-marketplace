# Together AI Official Documentation Snapshot

Verified against Together AI primary documentation and the official `togethercomputer/skills` repository on 2026-09-10. Recheck the live model catalog, pricing, rate-limit headers, and deprecation page before changing a production workload; those surfaces are intentionally dynamic.

## SDK and authentication

- [Quickstart](https://docs.together.ai/docs/quickstart)
- [Project-scoped API keys](https://docs.together.ai/docs/api-keys-authentication)
- [Python SDK v2 migration](https://docs.together.ai/docs/pythonv2-migration-guide)
- [Official Python v2 client](https://github.com/togethercomputer/together-py)
- [Official Together agent skills](https://github.com/togethercomputer/skills)

## Inference and models

- [Chat completions](https://docs.together.ai/docs/inference/chat/overview)
- [Chat API reference](https://docs.together.ai/reference/chat-completions)
- [OpenAI compatibility](https://docs.together.ai/docs/inference/openai-compatibility)
- [Serverless model catalog](https://docs.together.ai/docs/serverless/models)
- [Model-list API](https://docs.together.ai/reference/models)

## Asynchronous and managed workloads

- [Batch overview](https://docs.together.ai/docs/inference/batch/overview)
- [Batch tutorial](https://docs.together.ai/docs/inference/batch/tutorial)
- [Fine-tuning CLI and lifecycle](https://docs.together.ai/reference/cli/finetune)
- [Dedicated Model Inference](https://docs.together.ai/docs/dedicated-endpoints/overview)
- [Migrate dedicated endpoints from v1](https://docs.together.ai/docs/dedicated-endpoints/migrate-from-v1)

## Operations

- [Dynamic serverless rate limits](https://docs.together.ai/docs/serverless/rate-limits)
- [Usage and cost analytics](https://docs.together.ai/docs/billing-usage-limits)
- [Error codes](https://docs.together.ai/docs/error-codes)
- [Model lifecycle and deprecations](https://docs.together.ai/docs/deprecations)

## Pinned interpretation

- New Python work targets `together>=2.0.0`; v1 is maintenance-only and new features land in v2.
- SDKs read `TOGETHER_API_KEY`; REST requests use `Authorization: Bearer <token>`. Keys are project-scoped and must remain in an approved secret store.
- Serverless limits are dynamic per organization and model. Read response headers and adapt; do not encode a permanent RPM or TPM table.
- Batch input is JSONL with stable `custom_id` values. Upload with `purpose="batch-api"`, reconcile output and error files by `custom_id`, and do not assume output order.
- Batch and fine-tuning are asynchronous job APIs. Poll boundedly and persist job identifiers; Together does not document a general signed webhook delivery surface for these jobs.
- Current Dedicated Model Inference uses the v2 beta endpoint/deployment resource model. Do not create new capacity through the retired v1 endpoint-create flow.
- Model availability, redirects, context limits, prices, and batch eligibility change. Resolve them from the current catalog and deprecation pages at execution time.
