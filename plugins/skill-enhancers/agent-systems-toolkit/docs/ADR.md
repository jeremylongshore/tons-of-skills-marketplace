# ADR: Agent Systems Toolkit — portable core with capability-detected adapters

**Author:** Jeremy Longshore

**Date:** 2026-09-05

**Status:** Accepted

## Context

The marketplace supports portable Agent Skills while also maintaining contracts
for Claude Code plugins and agents, Codex packaging, MCP, hooks, catalogs, and
Beads. Those contracts overlap but are not identical. A single copied schema or
mandatory host integration would drift from the repository authorities and make
the model-neutral claim misleading.

## Decision

Use three Agent Skills as the portable workflow core. Route artifact-specific
work through a plugin-local capability map that points to existing authorities.
Provide five model-neutral role packets and optional Claude Code agent adapters.
Treat Beads, subagents, shell, network, MCP, and automatic discovery as detected
host capabilities, with fail-closed behavior and explicit degradation records.

## Alternatives considered

| Alternative | Why rejected |
| --- | --- |
| Copy every creator and validator into this plugin | Creates duplicate authorities that can silently drift |
| Call every host format universal | Misstates incompatible packaging, permission, discovery, and orchestration contracts |
| Require Beads and subagents in every runtime | Excludes otherwise capable hosts and hides the actual portability boundary |

## Consequences

**Positive:**

- Existing public IDs and schema authorities remain intact.
- The same evidence workflow can run sequentially or through specialist agents.
- Public runtime claims stay tied to registry evidence instead of prose.

**Negative / accepted tradeoffs:**

- Host adapters still need separate validation and maintenance.
- Degraded runtimes lose parallelism or durable tracking and must disclose that loss.
- The capability map is routing metadata, not an executable universal plugin format.

## Tool-permission scope

| Tool | Why it is needed |
| --- | --- |
| `Read` | Inspect target artifacts, policies, references, and evidence |
| `Write` | Create approved artifacts and evidence records in creator and upgrade workflows |
| `Edit` | Apply bounded repairs and upgrades |

The audit-only validator declares only `Read`. No portable skill pre-authorizes
shell, network, MCP, task, deployment, publication, or destructive operations.
