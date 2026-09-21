# Palantir Redacted Diagnostic Bundle sources

Reviewed: 2026-09-12

## First-party sources

- [Debug transforms](https://www.palantir.com/docs/foundry/code-repositories/debug-transforms)
- [Transform metrics](https://www.palantir.com/docs/foundry/transforms-python/metrics)
- [Configure logging](https://www.palantir.com/docs/foundry/administration/configure-logging)
- [API authentication](https://www.palantir.com/docs/foundry/api/general/overview/authentication)

## Contract notes

Do not create a recursive tarball of a repository or environment. Foundry logs can carry highly sensitive values, and debugger observations may not match committed outputs; collect only reviewed evidence.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
