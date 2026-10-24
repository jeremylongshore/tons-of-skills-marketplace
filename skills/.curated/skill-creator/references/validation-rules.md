# Authoring validation

Use the current target repository's validator and schema changelog. These
instructions summarize the existing contract; they do not redefine it.
See [authoring authority](source-of-truth.md) and [field guidance](frontmatter-spec.md).

## Skill tiers

Standard validation checks the upstream minimum. Marketplace validation adds the
IS eight-field contract: `name`, `description`, `allowed-tools`, `version`,
`author`, `license`, `compatibility`, `tags`. Missing any required marketplace
field is an error. `metadata.version` and `metadata.author` do not substitute for
their top-level counterparts. Tracking metadata is required, not optional polish.

Run from the marketplace repository, with an absolute target skill path:

```bash
python3 scripts/validate-skills-schema.py --marketplace "$skill_file"
```

Use the validator's actual structural findings and grade. Retain missing-section,
invalid-field, permission and supporting-file findings; do not edit a baseline
or downgrade severity to accept generated content. `--enterprise` is a legacy
alias; use `--marketplace` in new instructions.

## Agent validation

Agents do not get a permissive tier escape. The existing plugin-agent contract
has eleven live fields; standalone agents have fourteen. The complete set and
context-specific handling are in [authoring authority](source-of-truth.md) and the
shared `templates/agent-template.md` used by `agent-creator`.

Resolve `validator` to the canonical validator file and `target_root` to the
repository containing the generated definitions:

```bash
python3 "$validator" --repo-root "$target_root" --agents-only --json
```

A plugin context requires its real `.claude-plugin/plugin.json`. A directory
whose name merely contains `plugins` is not enough: the validator otherwise
classifies its agents as standalone. When testing templates, create a scratch
plugin manifest and assert the context before interpreting a missing-field result.

Check MCP tool invocations against the declared allowlist. Fully qualified
references are checked by the canonical validator; `/validate-agent` also helps
inspect abbreviated names. Do not equate a static pass with successful agent
execution or complete security isolation.

## Optional and conditional fields

Use the canonical registry for the supported names, types and constraints.
Current authoring guidance must preserve these existing behaviors:

- `agent` requires `context: fork`; forked skills may omit `agent` and use the
  runtime default.
- `argument-hint` remains relevant to user invocation even when automatic model
  invocation is disabled.
- `when_to_use` is a recognized activation field, not a deprecated replacement
  for `description`; apply the validator's combined disclosure budget.
- Effort options include `xhigh`; model and runtime availability still matter.
- Optional runtime fields are not automatically accepted by every pinned IS
  contract. Keep warnings and errors visible and report disagreements.

Do not reuse skill-only field spellings on agents or import invented fields
such as `capabilities`, `expertise_level` or `activation_priority`.

## Evidence classes

Record separately:

1. Syntax, schema and rubric results from the canonical validator.
2. Static production checks from `validate-skillmd` and deterministic package
   checks supported by the installed J-Rig CLI.
3. Behavioral evidence from the actual authorized model/provider run, including
   its immutable target, selected cases, failures and missing coverage.

Use `/validate-skillmd` for the first two classes. Behavioral execution is opt-in
and follows that skill's supported wrapper and proof-destination instructions.
Neither a zero exit code, a model matrix nor an ignored CLI flag proves behavior.
Use SKIPPED when no behavioral run was requested and INCOMPLETE when requested
coverage or prerequisites are missing. Apply the repository's actual promotion
policy without inventing a new universal gate.

## Repository testing work

For test-quality or infrastructure work, `audit-tests` diagnoses first and
`implement-tests` applies the authorized handoff. Ordinary skill prose edits do
not by themselves authorize installing a test stack or calling providers.
Use focused observable fixtures for changed scripts or emitted artifacts.

## Forge and reforge

Keep the static outputs, requested behavioral scope, actual outcomes and evidence
paths in `.forge/proofs.md`. Preserve prior results during reforge. The build audit
trail is separate from runtime `references/`; do not claim an absent evaluation
passed or put build-only deliberations in every runtime invocation.
