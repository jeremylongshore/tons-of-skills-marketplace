# Palantir Foundry Migration and Cutover sources

Reviewed: 2026-09-12

## First-party sources

- [DevOps release management](https://www.palantir.com/docs/foundry/devops-release-management/use-devops-for-release-management)
- [Marketplace application installation](https://www.palantir.com/docs/foundry/developer-console/marketplace-installation)
- [Incremental transforms](https://www.palantir.com/docs/foundry/transforms-python/incremental-usage)
- [Projects and roles](https://www.palantir.com/docs/foundry/security/projects-and-roles)

## Contract notes

A migration is incomplete without semantic reconciliation, control parity, consumer cutover evidence, and a tested rollback. Do not retire the source during the same decision that first enables the target.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
