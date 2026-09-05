# Creator, validator, and runtime capability audit

**Audit date:** 2026-09-05

**Purpose:** establish the existing capability surface and the factual boundary
for a model-neutral front door.

## Existing capability surface

The repository and Jeremy's installed skill library already contain separate
creator and validator entry points for Agent Skills, Claude Code agents and
plugins, MCP configuration, hooks, and marketplace catalogs. They are useful,
but they mix three different authorities:

1. The open Agent Skills and Model Context Protocol specifications.
2. Host-specific plugin, agent, command, hook, and discovery contracts.
3. The stricter Intent Solutions marketplace overlay and its canonical
   repository validator.

The toolkit therefore centralizes routing and workflow, not schema authority.
`capability-map.json` preserves the legacy entry-point names and identifies the
repository authority where one exists. Existing public IDs are not removed or
silently redirected in this release.

## Runtime research

The portable core is a directory containing `SKILL.md` and optional local
resources. The following primary sources demonstrate current skill support or
define the common contract:

- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Codex skills](https://developers.openai.com/codex/skills)
- [Pi skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md)
- [Goose Agent Skills](https://goose-docs.ai/docs/guides/context-engineering/using-skills/)
- [Hermes Agent repository](https://github.com/NousResearch/hermes-agent)
- [Model Context Protocol specification](https://modelcontextprotocol.io/specification/)
- [Beads repository](https://github.com/gastownhall/beads)

Pi explicitly implements the Agent Skills standard and discovers `SKILL.md`
under Pi-specific and `.agents/skills` locations. Goose documents global and
project `.agents/skills` discovery. Hermes ships a `SKILL.md` skill system and
skill-management implementation. These source facts establish compatibility
candidates; they are not fresh-environment installation receipts.

## Verified-support boundary

`config/harness-registry.json` is the repository authority for named harness
support. At audit time Claude Code is `verified-native`; Codex and Goose are
`standard-compatible` with public support disabled; Pi and Hermes remain
candidates pending registry entries and fresh-environment activation and
rollback receipts.

The toolkit can still be used manually by any model capable of receiving its
instructions. Automatic discovery, tool mapping, subagent execution, and safe
installation depend on the host and must not be implied by the phrase
"model-neutral."

## Databricks benchmark adopted

The production-upgrade workflow adopts the parts of the Databricks rebuild that
generalize:

- pain-grounded research rather than tutorial quotas;
- synthesis before implementation;
- deterministic scripts for load-bearing decisions;
- explicit architecture, safety, migration, and release decisions;
- positive, negative, edge, and adversarial evaluation;
- independent reproduction of reviewer claims;
- evidence and authorization bound to an exact revision.

It does not require every product to match Databricks document volume. The
evidence burden scales with risk, external API breadth, destructive authority,
data sensitivity, and compatibility impact.
