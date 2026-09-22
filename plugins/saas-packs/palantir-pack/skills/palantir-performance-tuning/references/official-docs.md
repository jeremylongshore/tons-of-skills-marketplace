# Palantir Workload Performance Tuning sources

Reviewed: 2026-09-12

## First-party sources

- [Transform metrics](https://www.palantir.com/docs/foundry/transforms-python/metrics)
- [Compute engine selection](https://www.palantir.com/docs/foundry/transforms-python/compute-engines)
- [Incremental usage](https://www.palantir.com/docs/foundry/transforms-python/incremental-usage)
- [TypeScript OSDK](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk)

## Contract notes

Do not publish fixed latency or data-size bands as platform guarantees. Use the target enrollment's telemetry, supported engine features, exact query shape, and representative data.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
