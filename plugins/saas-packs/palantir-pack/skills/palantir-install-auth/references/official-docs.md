# Palantir SDK Selection and OAuth Setup sources

Reviewed: 2026-09-12

## First-party sources

- [API authentication](https://www.palantir.com/docs/foundry/api/general/overview/authentication)
- [Application restrictions](https://www.palantir.com/docs/foundry/developer-console/application-restrictions)
- [Ontology SDK overview](https://www.palantir.com/docs/foundry/ontology-sdk/overview)
- [Developer API reference](https://www.palantir.com/docs/foundry/api-reference)

## Contract notes

Do not use a personal token as a production architecture. The actual authority is the intersection of the OAuth grant and scope, Developer Console restrictions, and permissions of the user or service user.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
