# Official Miro Sources for miro-install-auth

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [OAuth 2.0 authorization code flow](https://developers.miro.com/docs/getting-started-with-oauth)
- [Use an access token](https://developers.miro.com/reference/use-access-token-for-rest-api-requests)
- [Get access-token context](https://developers.miro.com/reference/get-access-token-context)
- [Revoke an access token](https://developers.miro.com/reference/revoke-token)
- [App security guidelines](https://developers.miro.com/docs/security-guidelines)
- [OAuth troubleshooting](https://developers.miro.com/docs/troubleshooting-oauth20)

## Workflow-specific review notes

- OAuth authorization begins at `https://miro.com/oauth/authorize`; the token endpoint remains `https://api.miro.com/v1/oauth/token` while resources use REST v2.
- Expiring mode uses one-hour access tokens and rotating refresh tokens valid for 60 days; store each new pair atomically.
- Bind encrypted token records to application, user, authorized team, scopes, and expiry metadata, then prove context before reads or writes.
