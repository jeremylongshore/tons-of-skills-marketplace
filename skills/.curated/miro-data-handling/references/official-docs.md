# Official Miro Sources for miro-data-handling

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [App security guidelines](https://developers.miro.com/docs/security-guidelines)
- [Permission scopes](https://developers.miro.com/reference/scopes)
- [Get boards](https://developers.miro.com/reference/get-boards)
- [Get items on a board](https://developers.miro.com/reference/get-items)
- [Platform lifecycle policy](https://developers.miro.com/docs/lifecycle-policy)

## Workflow-specific review notes

- Treat board names, descriptions, owners, links, item text, and exports as potentially confidential customer content.
- Collect and retain only the fields required for the approved purpose, and bind deletion/retention controls to that purpose.
- Use narrow scopes and redact evidence before logs, tickets, or diagnostic bundles leave the trusted boundary.
