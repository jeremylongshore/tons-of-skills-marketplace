# Palantir DevOps Environment Separation sources

Reviewed: 2026-09-12

## First-party sources

- [Release management overview](https://www.palantir.com/docs/foundry/devops-release-management/overview)
- [Use DevOps for release management](https://www.palantir.com/docs/foundry/devops-release-management/use-devops-for-release-management)
- [Marketplace application installation](https://www.palantir.com/docs/foundry/developer-console/marketplace-installation)
- [Application restrictions](https://www.palantir.com/docs/foundry/developer-console/application-restrictions)

## Contract notes

Do not model environments as arbitrary hostname files alone. Spaces, products, dependencies, parameters, security policies, and release controls form the current Foundry environment contract.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
