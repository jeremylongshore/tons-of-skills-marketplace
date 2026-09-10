# Official Miro Sources for miro-core-workflow-a

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [REST API introduction](https://developers.miro.com/reference/overview)
- [Permission scopes](https://developers.miro.com/reference/scopes)
- [Create a board](https://developers.miro.com/reference/create-board-1)
- [Get items on a board](https://developers.miro.com/reference/get-items)
- [Create items in bulk](https://developers.miro.com/reference/create-items)
- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)

## Workflow-specific review notes

- Board and item mutations require the approved board identity and the narrowest applicable write scope.
- Miro documents a hard ceiling of 20 items per bulk-create call; the operation is transactional and charges Level 2 credits for each requested item.
- Re-read persisted state after a successful mutation and reconcile ambiguous failures before any retry.
