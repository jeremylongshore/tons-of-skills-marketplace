# First-party Fly.io evidence

Consulted on 2026-09-13 for `flyio-webhooks-events`.

## Authority boundary

Fly.io documentation and the provider-maintained flyctl repository define platform behavior. This skill treats local examples as implementation guidance, not as an official SDK, support promise, price lock, regional-capacity guarantee, or proof that a live operation succeeded.

## Sources used

- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Machines resource](https://fly.io/docs/machines/api/machines-resource/)
- [Machine states](https://fly.io/docs/machines/machine-states/)
- [Health checks](https://fly.io/docs/reference/health-checks/)
- [Monitoring](https://fly.io/docs/monitoring/)
- [Export logs](https://fly.io/docs/monitoring/exporting-logs/)
- [flyctl releases](https://github.com/superfly/flyctl/releases) — provider-maintained CLI release history; latest observed release `v0.4.102` on 2026-09-10.

## Snapshot fingerprints

- Machines API setup HTML SHA-256: `f0f857b0b1e8b46f082b90f5038be0cf` + `0de0a0159f6923ed88b322b9d43b6e2d`.
- Automation and token guidance HTML SHA-256: `c9dfbd78f7451f9f8249380e1c140d5` + `e0a3c9545e45f2313e8d77a5d675c292b`.
- App configuration HTML SHA-256: `9f220de63646c15858e4bd9a550bcce7` + `e846694b2795e02fbec568fe294e615b`.

## Product facts applied

- The Machines API supports reads and a bounded wait for known target states.
- General app webhook registration and signing are not documented; extension-provider webhooks are a separate partner surface.
- Documented log shipping and health reads are safer sources than relying on an undocumented logs HTTP API.

## Maintenance rule

Re-fetch the linked first-party pages and current flyctl release before changing authentication, commands, API paths, state names, limits, deployment strategies, storage behavior, or pricing-sensitive guidance. Record the retrieval date and new fingerprints; do not silently preserve stale claims.
