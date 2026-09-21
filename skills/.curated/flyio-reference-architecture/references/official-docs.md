# First-party Fly.io evidence

Consulted on 2026-09-13 for `flyio-reference-architecture`.

## Authority boundary

Fly.io documentation and the provider-maintained flyctl repository define platform behavior. This skill treats local examples as implementation guidance, not as an official SDK, support promise, price lock, regional-capacity guarantee, or proof that a live operation succeeded.

## Sources used

- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Regions](https://fly.io/docs/reference/regions/)
- [Private networking](https://fly.io/docs/networking/private-networking/)
- [Managed Postgres](https://fly.io/docs/mpg/)
- [Fly Volumes](https://fly.io/docs/volumes/)
- [flyctl releases](https://github.com/superfly/flyctl/releases) — provider-maintained CLI release history; latest observed release `v0.4.102` on 2026-09-10.

## Snapshot fingerprints

- Machines API setup HTML SHA-256: `f0f857b0b1e8b46f082b90f5038be0cf` + `0de0a0159f6923ed88b322b9d43b6e2d`.
- Automation and token guidance HTML SHA-256: `c9dfbd78f7451f9f8249380e1c140d5` + `e0a3c9545e45f2313e8d77a5d675c292b`.
- App configuration HTML SHA-256: `9f220de63646c15858e4bd9a550bcce7` + `e846694b2795e02fbec568fe294e615b`.

## Product facts applied

- Current region and Managed Postgres availability should be queried instead of summarized as a permanent region count.
- Machines and volumes are regional; private 6PN spans apps in the same organization.
- Managed Postgres is distinct from unmanaged Postgres apps and from volume-backed application storage.

## Maintenance rule

Re-fetch the linked first-party pages and current flyctl release before changing authentication, commands, API paths, state names, limits, deployment strategies, storage behavior, or pricing-sensitive guidance. Record the retrieval date and new fingerprints; do not silently preserve stale claims.
