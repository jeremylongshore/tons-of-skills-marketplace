# Official Miro Sources for miro-core-workflow-b

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [Get boards](https://developers.miro.com/reference/get-boards)
- [Get items on a board](https://developers.miro.com/reference/get-items)
- [REST API comparison guide](https://developers.miro.com/docs/rest-api-comparison-guide)
- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Use an access token](https://developers.miro.com/reference/use-access-token-for-rest-api-requests)

## Workflow-specific review notes

- Follow documented cursors until termination; a short page is not proof that pagination is complete.
- Keep v2 item-type schemas distinct instead of collapsing them into the retired v1 widget model.
- Board metadata and item content can be confidential, so snapshot only the fields required for reconciliation.
