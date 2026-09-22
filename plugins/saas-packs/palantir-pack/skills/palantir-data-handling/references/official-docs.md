# Palantir Data Governance and Handling sources

Reviewed: 2026-09-12

## First-party sources

- [Projects and roles](https://www.palantir.com/docs/foundry/security/projects-and-roles)
- [Manage object security](https://www.palantir.com/docs/foundry/object-permissioning/managing-object-security)
- [Property security markings](https://www.palantir.com/docs/foundry/security/property-security-markings)
- [Audit logs](https://www.palantir.com/docs/foundry/security/audit-logs-overview)

## Contract notes

Discretionary project roles and mandatory controls are not interchangeable. Granular Ontology read policies do not automatically follow data into downstream outputs, so propagation must be tested rather than assumed.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
