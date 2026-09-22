# Palantir Application and Compute Deployment sources

Reviewed: 2026-09-12

## First-party sources

- [Compute Modules overview](https://www.palantir.com/docs/foundry/compute-modules/overview)
- [Compute Module containers](https://www.palantir.com/docs/foundry/compute-modules/containers)
- [Compute Modules getting started](https://www.palantir.com/docs/foundry/compute-modules/get-started)
- [Marketplace application installation](https://www.palantir.com/docs/foundry/developer-console/marketplace-installation)

## Contract notes

External Cloud Run is not the default Foundry deployment contract. Use the current Palantir deployment primitive and verify its environment, image, access, and parameter rules before promotion.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
