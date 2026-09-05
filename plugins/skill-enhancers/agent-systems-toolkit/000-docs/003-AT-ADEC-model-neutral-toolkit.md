# Model-neutral Agent Systems Toolkit decision

**Decision date:** 2026-09-05

**Status:** accepted for implementation; publication requires a later maintainer
checkpoint.

## Decision

Create `agent-systems-toolkit` as one repository-owned front door with three portable
Agent Skills:

1. `artifact-creator` for creating skills, agents, plugins, MCP integrations,
   hooks, and catalogs against the correct contract.
2. `artifact-validator` for discovering and validating those artifacts without
   introducing a competing source of truth.
3. `production-upgrade` for security-first, evidence-bound modernization.

Ship five focused plugin subagents as a Claude Code adapter and keep equivalent
model-neutral role packets inside `production-upgrade`. The portable workflow
must remain complete when the adapter is absent.

## Boundaries

- "Model-neutral" describes instruction and model selection, not universal
  host support.
- Agent Skills and MCP are open contracts. Plugins, subagent files, commands,
  hooks, and marketplace catalogs remain host-specific adapters.
- Existing creator and validator IDs remain available. This release records
  them in a capability map and does not remove or rename them.
- The repository's `scripts/validate-skills-schema.py` remains authoritative for
  Intent Solutions skill and agent validation. Kernel shadow lanes remain
  advisory until their separately governed promotion criteria are met.
- No runtime is advertised as verified unless the harness registry carries the
  required fresh-environment evidence.

## Rejected alternatives

### Copy every existing skill into the new plugin

Rejected because copied validators drift and create multiple authorities.

### Call every host format universal

Rejected because plugin, subagent, hook, permission, and installation contracts
differ materially across hosts.

### Require Beads and subagents everywhere

Rejected because those are optional runtime capabilities. They are mandatory
when project policy requires them, otherwise the workflow records its degraded
persistence or orchestration mode.

## Compatibility

The new plugin is additive. A future migration may convert old entry points into
generated compatibility wrappers only after direct invocation, package,
installation, and rollback tests exist and a deprecation window is approved.
