# Palantir Event and Subscription Integration sources

Reviewed: 2026-09-12

## First-party sources

- [TypeScript OSDK subscriptions](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-subscriptions)
- [WebSocket subscriptions](https://www.palantir.com/docs/foundry/ontology-sdk/websocket-subscriptions)
- [Monitoring alerts to external systems](https://www.palantir.com/docs/foundry/monitoring-views/external-systems)
- [Ontology SDK overview](https://www.palantir.com/docs/foundry/ontology-sdk/overview)

## Contract notes

Ontology subscriptions, direct Object Set Watcher WebSockets, and monitoring/Data Connection webhooks are separate contracts. Do not publish a generic outgoing Ontology event registration or signature scheme without first-party documentation.

The live Palantir documentation, in-platform generated documentation, and generated SDK for the target enrollment are authoritative when they change after this review date. Re-verify API shapes, SDK versions, feature availability, permissions, limits, environment behavior, and support status immediately before a live change.
