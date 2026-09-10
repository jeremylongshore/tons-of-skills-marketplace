# Official Miro Sources for miro-performance-tuning

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Get boards](https://developers.miro.com/reference/get-boards)
- [Get items on a board](https://developers.miro.com/reference/get-items)
- [Create items in bulk](https://developers.miro.com/reference/create-items)
- [Official Node.js API client](https://developers.miro.com/docs/miro-nodejs-api-client)

## Workflow-specific review notes

- Optimize from measured per-operation latency, cursor counts, credit cost, payload size, and freshness—not request count alone.
- Bulk creation is capped at 20 items and is transactional, but each item still incurs Level 2 credit cost.
- Preserve pagination completeness and tenant isolation when adding caching, concurrency, or batching.
