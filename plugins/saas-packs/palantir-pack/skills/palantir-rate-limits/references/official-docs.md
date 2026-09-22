# Palantir API Limit and Concurrency Control sources

Reviewed: 2026-09-12

## First-party sources

- [API limits](https://www.palantir.com/docs/foundry/api/general/overview/limits)
- [API authentication](https://www.palantir.com/docs/foundry/api/general/overview/authentication)
- [Ontology SDK overview](https://www.palantir.com/docs/foundry/ontology-sdk/overview)
- [Developer API reference](https://www.palantir.com/docs/foundry/api-reference)

## Contract notes

At review time the general documentation publishes global per-user values, but it explicitly allows stricter endpoint limits and practical variation. Re-read it before encoding a budget and never shard identities to evade limits.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
