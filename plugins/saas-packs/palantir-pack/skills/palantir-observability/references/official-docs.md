# Palantir Foundry Observability Design sources

Reviewed: 2026-09-12

## First-party sources

- [Transform metrics](https://www.palantir.com/docs/foundry/transforms-python/metrics)
- [Log permissions](https://www.palantir.com/docs/foundry/aip-observability/log-permissioning)
- [Configure logging](https://www.palantir.com/docs/foundry/administration/configure-logging)
- [Audit logs](https://www.palantir.com/docs/foundry/security/audit-logs-overview)

## Contract notes

Foundry logs are not audit logs. Log visibility and exports can expose sensitive workflow data, so permissions, markings, audiences, and retention are part of observability correctness.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
