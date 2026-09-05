# Agent Systems Toolkit

Agent Systems Toolkit is the model-neutral front door for creating, validating,
and upgrading agent-system artifacts. It covers portable Agent Skills, harness
plugins and subagents, MCP servers and client configuration, hooks, and
marketplace catalogs without pretending those host-specific formats are one
universal standard.

## Included skills

| Skill                | Purpose                                                                                                                                 |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `artifact-creator`   | Design and create portable or host-specific agent artifacts against the correct authority.                                              |
| `artifact-validator` | Discover and validate skills, agents, plugins, MCP configuration, hooks, and catalogs without creating a competing validator authority. |
| `production-upgrade` | Run a Databricks-grade, security-first research, architecture, implementation, verification, and release-readiness workflow.            |

The production-upgrade workflow includes five reusable specialist roles:
researcher, architect, implementation engineer, verification engineer, and
security adversary. Hosts with subagent support may run them separately; other
hosts execute the same role packets sequentially in the main context.

## Portability contract

The canonical skills follow the open [Agent Skills specification](https://agentskills.io/specification).
They do not require a particular model. Runtime discovery, tool names, plugin
packaging, subagents, and hooks belong to the host adapter.

The repository harness registry remains authoritative for named support. A
runtime that can read a `SKILL.md` may execute these instructions manually, but
that fact alone does not qualify it for a public verified-support claim.

The marketplace-specific frontmatter is the repository overlay defined by
[`STANDARDS.md`](../../../STANDARDS.md) and enforced by
[`scripts/validate-skills-schema.py`](../../../scripts/validate-skills-schema.py).
Fields that are optional or host-specific are not presented as requirements of
the open Agent Skills contract. Repository provenance classifies artifacts with
no upstream source record as first-party; the executable rule lives in
[`scripts/plugin-provenance.mjs`](../../../scripts/plugin-provenance.mjs).

## Durable work

When a repository uses Beads, `production-upgrade` requires the `bd` workflow:
prime context, search before creating, claim before mutation, attach validation
receipts, and close only after the acceptance evidence exists. If Beads is not
installed and project policy does not require it, the skill uses the host's
durable task facility or an explicit in-session ledger and reports that weaker
persistence boundary.

## Security posture

- Unknown formats, permissions, side effects, and support states fail closed.
- Generated credentials and plaintext secrets are prohibited.
- Research claims cite current primary sources and carry verification dates.
- Reviewer output is evidence to reproduce, not authority to trust blindly.
- Publishing, deployment, destructive changes, and merges require explicit
  authorization at the exact state being acted on.
