# Cohere Official Documentation Snapshot

Verified against Cohere primary documentation, the official SDK repositories, and package registries on 2026-09-11. Recheck the live model catalog, deprecation schedule, pricing, and rate-limit page before changing a production workload because those surfaces are intentionally dynamic.

## SDK and authentication

- [Create a v2 client](https://docs.cohere.com/docs/create-client)
- [Official TypeScript SDK](https://github.com/cohere-ai/cohere-typescript)
- [Official Python SDK](https://github.com/cohere-ai/cohere-python)
- [API key types and limits](https://docs.cohere.com/docs/rate-limits)
- [Teams and roles](https://docs.cohere.com/reference/teams-and-roles)

## Models and inference

- [Live model catalog](https://docs.cohere.com/docs/models)
- [Command A+](https://docs.cohere.com/docs/command-a-plus)
- [Chat API](https://docs.cohere.com/reference/chat)
- [Embed API](https://docs.cohere.com/reference/embed)
- [Rerank models](https://docs.cohere.com/docs/rerank)
- [Rerank API](https://docs.cohere.com/reference/rerank)
- [Tool use](https://docs.cohere.com/docs/tool-use)
- [Streaming](https://docs.cohere.com/docs/streaming)
- [Safety modes](https://docs.cohere.com/docs/safety-modes)

## Lifecycle and operations

- [API v1 to v2 migration](https://docs.cohere.com/docs/migrating-v1-to-v2)
- [Deprecations](https://docs.cohere.com/docs/deprecations)
- [OpenAI compatibility](https://docs.cohere.com/docs/compatibility-api)
- [Going live](https://docs.cohere.com/docs/going-live)
- [Error reference](https://docs.cohere.com/reference/errors)
- [Cohere status](https://status.cohere.com)
- [Pricing](https://cohere.com/pricing)
- [Privacy policy](https://cohere.com/privacy)
- [Cloud-platform compatibility](https://docs.cohere.com/docs/cohere-works-everywhere/)

## Pinned interpretation

- New integrations use API v2 clients: `CohereClientV2` in TypeScript and `cohere.ClientV2` in Python. On 2026-09-11, the registry releases were `cohere-ai@8.1.0` and `cohere==7.1.1`; pin a compatible range and retain the resolved lockfile version.
- Resolve deployable models from the live catalog or Models API. `command-a-plus-05-2026`, `embed-v4.0`, `rerank-v4.0-pro`, and `rerank-v4.0-fast` were live reference candidates on the review date, not permanent aliases.
- API v2 requires `model` for Chat, Embed, Rerank, and Classify; Embed also requires `embedding_types`. Chat history lives in `messages`, and tools use JSON Schema.
- Managed `/v1/connectors`, `connectors` on Chat v1, Generate, Summarize, Classify, and legacy fine-tuning were listed as deprecated. In v2, implement retrieval or web search as application-owned tools.
- Evaluation and production limits differ by endpoint and model. Some newer Chat models require a sales-approved production arrangement. Treat the live limits page and response behavior as authoritative.
- Cohere Teams expose Owner and User roles, but application authorization, per-tenant budgets, and least-privilege runtime keys remain the customer's responsibility.
- The public privacy policy says enterprise customer-data commitments are contract-specific. Do not infer retention, residency, or training terms from generic marketing copy; bind production controls to the signed agreement.
