# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Deterministic Development Loop**. Re-check sandbox and endpoint contracts before any provider test.

## Sources

- [Procore sandboxes](https://developers.procore.com/documentation/development-environments)
- [Troubleshooting](https://developers.procore.com/documentation/troubleshooting)
- [Error code reference](https://developers.procore.com/documentation/error-reference)
- [REST API lifecycle](https://developers.procore.com/documentation/rest-api-lifecycle)

## Provider boundaries

- Developer Sandbox credentials and endpoints are separate from production.
- Developer Sandboxes are isolated, seeded environments rather than production mirrors.
- Tests must not rely on a reset or refresh to clean up their data.
- Fixture changes require reviewed endpoint or changelog evidence.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
