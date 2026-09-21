# Palantir Foundry Incident Response sources

Reviewed: 2026-09-12

## First-party sources

- [API limits](https://www.palantir.com/docs/foundry/api/general/overview/limits)
- [Transform metrics](https://www.palantir.com/docs/foundry/transforms-python/metrics)
- [DevOps release management](https://www.palantir.com/docs/foundry/devops-release-management/use-devops-for-release-management)
- [Configure logging](https://www.palantir.com/docs/foundry/administration/configure-logging)

## Contract notes

A response is not complete when an endpoint turns green. Confirm data correctness, effective access, build/product identity, and pending side effects before declaring recovery.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
