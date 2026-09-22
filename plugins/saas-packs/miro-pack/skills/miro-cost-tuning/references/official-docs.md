# Official Miro Sources for miro-cost-tuning

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Web SDK rate limiting](https://developers.miro.com/docs/websdk-reference-rate-limiting)
- [Get boards](https://developers.miro.com/reference/get-boards)
- [Get items on a board](https://developers.miro.com/reference/get-items)
- [Create items in bulk](https://developers.miro.com/reference/create-items)

## Workflow-specific review notes

- REST capacity is a shared per-user/application credit budget, not a simple request counter.
- Use observed rate-limit headers and endpoint credit weights to size concurrency, batching, and retry windows.
- Optimize reads and writes separately; bulk create still charges the documented level per item.
