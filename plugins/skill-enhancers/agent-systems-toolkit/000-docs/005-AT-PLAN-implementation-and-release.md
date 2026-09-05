# Agent Systems Toolkit implementation and release plan

## Implementation gates

- [x] Inventory existing creator and validator capabilities.
- [x] Research named runtime skill behavior from primary sources.
- [x] Define the authority-preserving capability map.
- [x] Implement three portable skills and five specialist role packets.
- [x] Implement the plugin subagent adapter.
- [x] Add deterministic evidence and artifact-inventory helpers.
- [x] Add focused contract and security regression tests.
- [x] Regenerate catalog-derived files.

## Validation gates

- [x] Focused toolkit unit tests and helper self-tests.
- [x] Marketplace skill schema validation.
- [x] Agent validation for every plugin subagent.
- [x] MCP/configuration validation is not applicable; this plugin ships no MCP
      configuration or server.
- [x] Unicode hygiene, formatting, generated-artifact, and secret checks.
- [x] Package dry-run and disposable install smoke.
- [ ] Independent adversarial review with every material claim reproduced.

## Release gates

- [ ] Exact candidate revision reported to Jeremy.
- [ ] Required CI and configured reviewer statuses reconciled.
- [ ] Explicit approval obtained for the exact revision.
- [ ] Package publication verified separately from repository merge.

This plan does not authorize commit, push, PR creation, merge, tag, release, or
publication.
