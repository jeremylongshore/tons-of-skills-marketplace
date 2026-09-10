# Official Miro Sources for miro-security-basics

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [App security guidelines](https://developers.miro.com/docs/security-guidelines)
- [OAuth 2.0 authorization code flow](https://developers.miro.com/docs/getting-started-with-oauth)
- [Permission scopes](https://developers.miro.com/reference/scopes)
- [Use an access token](https://developers.miro.com/reference/use-access-token-for-rest-api-requests)
- [Revoke an access token](https://developers.miro.com/reference/revoke-token)
- [Get access-token context](https://developers.miro.com/reference/get-access-token-context)

## Workflow-specific review notes

- Use exact redirect URIs, unpredictable state, least-privilege scopes, encrypted token storage, and atomic refresh rotation.
- Bind authorization to the expected app, user, and team context before board access.
- Redact secrets and board content from logs and test revocation, reinstall, and incident recovery.
