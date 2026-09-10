# Official Miro Sources for miro-debug-bundle

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [OAuth troubleshooting](https://developers.miro.com/docs/troubleshooting-oauth20)
- [Get access-token context](https://developers.miro.com/reference/get-access-token-context)
- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Miro service status](https://status.miro.com/)
- [App security guidelines](https://developers.miro.com/docs/security-guidelines)

## Workflow-specific review notes

- Capture status, safe error code, timing, rate headers, and hashed tenant/resource identifiers; omit tokens and board content.
- Separate vendor status evidence from local authentication, authorization, and deployment evidence.
- Apply redaction before writing or sharing the bundle, then verify the resulting artifact again.
