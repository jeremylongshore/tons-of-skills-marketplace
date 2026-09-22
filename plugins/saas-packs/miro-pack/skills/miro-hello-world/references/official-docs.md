# Official Miro Sources for miro-hello-world

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [Get boards](https://developers.miro.com/reference/get-boards)
- [Permission scopes](https://developers.miro.com/reference/scopes)
- [Get access-token context](https://developers.miro.com/reference/get-access-token-context)
- [Use an access token](https://developers.miro.com/reference/use-access-token-for-rest-api-requests)
- [OAuth troubleshooting](https://developers.miro.com/docs/troubleshooting-oauth20)

## Workflow-specific review notes

- Use a bounded board-list request with `boards:read`; do not create sample content merely to prove connectivity.
- Validate returned user/team context against the intended installation before treating HTTP 200 as success.
- Record pagination and rate headers without retaining board names, descriptions, links, or tokens.
