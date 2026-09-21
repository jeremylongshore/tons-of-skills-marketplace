# Palantir Foundry CI and Review Gates sources

Reviewed: 2026-09-12

## First-party sources

- [Code Repositories navigation](https://www.palantir.com/docs/foundry/code-repositories/navigation)
- [Pipeline development best practices](https://www.palantir.com/docs/foundry/building-pipelines/development-best-practices)
- [Code Repositories FAQ](https://www.palantir.com/docs/foundry/code-repositories/faq)
- [Build transforms from VS Code](https://www.palantir.com/docs/foundry/palantir-extension-for-visual-studio-code/transforms-build)

## Contract notes

Foundry Code Repository checks and pull requests are the authoritative in-platform gate. Do not describe a generic GitHub Actions workflow as the mechanism that validates Foundry dataset ownership, transform declarations, or full platform builds.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
