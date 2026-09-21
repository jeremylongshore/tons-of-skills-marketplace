# Palantir SDK and Application Upgrade sources

Reviewed: 2026-09-12

## First-party sources

- [TypeScript OSDK migration](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk-migration)
- [Ontology SDK overview](https://www.palantir.com/docs/foundry/ontology-sdk/overview)
- [Python Platform SDK releases](https://github.com/palantir/foundry-platform-python/releases)
- [DevOps release management](https://www.palantir.com/docs/foundry/devops-release-management/use-devops-for-release-management)

## Contract notes

Never invent generic major-version migrations. Use the exact generated OSDK migration guide or official Platform SDK release evidence for the versions in scope, and keep authentication changes separate.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
