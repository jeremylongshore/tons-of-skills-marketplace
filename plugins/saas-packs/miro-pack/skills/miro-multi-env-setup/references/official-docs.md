# Official Miro Sources for miro-multi-env-setup

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [OAuth 2.0 authorization code flow](https://developers.miro.com/docs/getting-started-with-oauth)
- [Permission scopes](https://developers.miro.com/reference/scopes)
- [Get access-token context](https://developers.miro.com/reference/get-access-token-context)
- [App security guidelines](https://developers.miro.com/docs/security-guidelines)
- [Revoke an access token](https://developers.miro.com/reference/revoke-token)

## Workflow-specific review notes

- Use separate Miro apps and exact redirect allowlists for development, staging, and production.
- Store token references under environment-specific identities and fail closed when app, team, or board context disagrees.
- Exercise revocation and reinstall recovery independently in every environment before production use.
