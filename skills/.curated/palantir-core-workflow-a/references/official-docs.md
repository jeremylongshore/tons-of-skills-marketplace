# Palantir Python Transform Pipeline sources

Reviewed: 2026-09-12

## First-party sources

- [Python transforms overview](https://www.palantir.com/docs/foundry/transforms-python/overview)
- [Basic transforms](https://www.palantir.com/docs/foundry/transforms-python/transforms)
- [Incremental usage](https://www.palantir.com/docs/foundry/transforms-python/incremental-usage)
- [Compute engine selection](https://www.palantir.com/docs/foundry/transforms-python/compute-engines)

## Contract notes

Incremental correctness depends on transaction history, read modes, write mode, and snapshot behavior. Engine selection must follow required features and measured telemetry rather than invented dataset-size thresholds.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
