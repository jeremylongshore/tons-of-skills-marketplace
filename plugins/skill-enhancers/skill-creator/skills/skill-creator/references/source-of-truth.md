# Authoring authority

Use the target repository's current contract. This guide explains the layers;
it does not override the validator or introduce a new schema policy.

## Sources

- [Claude Code skills](https://code.claude.com/docs/en/skills): runtime frontmatter,
  invocation and tool permissions.
- [Agent Skills specification](https://agentskills.io/specification): portable skill
  packaging and metadata.
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents): agent runtime
  fields and execution context.
- The marketplace `CLAUDE.md` validation section and `000-docs/SCHEMA_CHANGELOG.md`:
  the current IS gate, non-negotiables and migration status.
- The pinned kernel's authoring schemas and changelog: machine contract semantics.
  Read the target repository's pin and provenance instead of assuming an old
  vendored copy is current.

The existing marketplace gate is `scripts/validate-skills-schema.py`. Kernel
shadow reports are advisory until the repository's approved cutover; a kernel
pass does not waive a Python-validator failure. Report disagreements with the
source versions and evidence. Do not change required sets, error severity, pins,
baselines or source classification to make a generated artifact pass.

## Skill contract

The open standard requires `name` and `description`. IS marketplace output must
also emit top-level `allowed-tools`, `version`, `author`, `license`,
`compatibility` and `tags`. Missing any of the eight fields is an error at
marketplace tier. Nested metadata does not replace a required top-level field.
The permissive standard tier is not a marketplace acceptance result.

Body grading and structural checks remain governed by the target validator.
Use the complete template; keep mode-specific detail in references rather than
copying an upstream-minimum example and claiming enterprise compliance.

## Agent contract

The existing agent gate is strict at every tier. Plugin definitions require
`name`, `description`, `tools`, `model`, `color`, `version`, `author`, `tags`,
`disallowedTools`, `skills` and `background`. Standalone definitions additionally
require live `hooks`, `mcpServers` and `permissionMode` fields. Omit those three
from plugin agents and configure their capabilities at plugin level.

Agents use `tools` and camelCase `disallowedTools`; skills use `allowed-tools`
and kebab-case `disallowed-tools`. Use the shared agent template and the
`agent-creator` workflow. A valid schema does not establish behavioral quality.

## Validation and testing

Run the canonical validator against the generated files and retain its results.
[Validation rules](validation-rules.md) describe the commands and evidence classes.
For an existing repository's test-quality assessment, use `audit-tests` first;
use `implement-tests` for the resulting authorized installation or repairs.
These are distinct from skill scoring and opt-in model evaluations.

## Forge records

`.forge/` is the build-time decision and proof trail. Runtime instructions belong
in SKILL.md and `references/`; they must not require loading the build diary.
Keep research, provenance, static results and any authorized behavioral evidence
in the forge record. Do not manufacture a verified result when a provider run
was absent, skipped or incomplete.
