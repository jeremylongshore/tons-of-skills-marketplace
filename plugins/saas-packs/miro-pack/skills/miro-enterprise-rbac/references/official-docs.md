# Official Miro Sources for miro-enterprise-rbac

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [Permission scopes](https://developers.miro.com/reference/scopes)
- [Get access-token context](https://developers.miro.com/reference/get-access-token-context)
- [App security guidelines](https://developers.miro.com/docs/security-guidelines)
- [REST API comparison guide](https://developers.miro.com/docs/rest-api-comparison-guide)
- [Get boards](https://developers.miro.com/reference/get-boards)

## Workflow-specific review notes

- Plan, role, app scope, installation context, team membership, and board permissions jointly determine effective access.
- Verify Enterprise availability before relying on organization or team administration surfaces.
- Keep the audit read-only until an accountable administrator approves exact membership, role, or sharing changes.
