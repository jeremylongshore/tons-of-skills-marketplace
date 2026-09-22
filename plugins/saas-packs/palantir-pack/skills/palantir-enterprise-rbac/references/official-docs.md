# Palantir Foundry Access-Control Design sources

Reviewed: 2026-09-12

## First-party sources

- [Projects and roles](https://www.palantir.com/docs/foundry/security/projects-and-roles)
- [Checking permissions](https://www.palantir.com/docs/foundry/security/checking-permissions)
- [Application restrictions](https://www.palantir.com/docs/foundry/developer-console/application-restrictions)
- [API authentication](https://www.palantir.com/docs/foundry/api/general/overview/authentication)

## Contract notes

A role grant does not override organizations, markings, or CBAC. API access is further constrained by OAuth scopes and Developer Console restrictions, so report each layer independently.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
