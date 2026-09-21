# Palantir Foundry Error Triage sources

Reviewed: 2026-09-12

## First-party sources

- [API authentication](https://www.palantir.com/docs/foundry/api/general/overview/authentication)
- [API limits](https://www.palantir.com/docs/foundry/api/general/overview/limits)
- [Check access](https://www.palantir.com/docs/foundry/security/checking-permissions)
- [Builds and checks FAQ](https://www.palantir.com/docs/foundry/health-checks/builds-checks-faq)

## Contract notes

Treat authentication, OAuth scopes, Developer Console restrictions, discretionary roles, and mandatory controls as intersecting but distinct evidence. Do not recommend repeated credential rotation for an authorization or marking failure.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
