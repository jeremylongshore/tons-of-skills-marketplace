# Runtime portability

## Contract

The portable artifact is the Agent Skills directory. The host controls
discovery, invocation, tool names, permissions, subagents, hooks, MCP wiring,
and plugin packaging.

Before naming support, check the repository harness registry. Distinguish:

- `verified-native`: fresh-environment discovery, activation, resource behavior,
  installation, and rollback evidence exists.
- `standard-compatible`: current documentation describes a compatible skill
  format or path, but the repository has not retained all promotion receipts.
- `candidate`: source evidence exists but no registry support state exists.
- `manual`: the model can receive the skill content as context; no native
  discovery claim is made.

## Named runtimes audited 2026-09-05

- Claude Code: registry-backed verified-native support.
- Codex and Goose: registry-backed standard-compatible candidates; public
  verified support remains disabled.
- Pi: its official repository documents the Agent Skills standard and discovers
  `SKILL.md` from Pi and `.agents/skills` locations; registry promotion remains.
- Hermes Agent: its official repository ships `SKILL.md` discovery and skill
  management; exact install and rollback receipts remain.

These are harness facts, not model restrictions. A host may run different
models, and a model may be used by multiple hosts.

## Capability fallback

- No native skill loader: inject `SKILL.md` and required references manually.
- No subagents: execute role packets sequentially and label self-review.
- No Beads: use the project-mandated task store or disclose in-session-only
  tracking.
- No shell: perform read-only analysis and provide commands without claiming
  they ran.
- No network: use retained primary sources and mark freshness unverified.
- No safe mutation or approval primitive: remain read-only or recommend-only.
