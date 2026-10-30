# Authoring field guidance

Use [authoring authority](source-of-truth.md) for source priority and the target
repository's canonical validator for current names, types and limits. Upstream
runtime acceptance and IS marketplace acceptance are separate layers.

## Marketplace skill template

Emit all eight top-level fields using `templates/skill-template.md`:

| Field           | Purpose                                     |
| --------------- | ------------------------------------------- |
| `name`          | Identifier that matches the skill directory |
| `description`   | Capability and useful activation conditions |
| `allowed-tools` | Tools needed by this workflow               |
| `version`       | SemVer tracking                             |
| `author`        | Maintainer attribution                      |
| `license`       | Known license or applicable bundled notice  |
| `compatibility` | Actual runtime requirements                 |
| `tags`          | Discovery terms                             |

The open standard's smaller minimum does not satisfy marketplace submission.
Required tracking fields are not optional polish. Do not invent a license for
third-party content or move required fields into `metadata` to hide omissions.

## Tools and permissions

Skills use `allowed-tools` and `disallowed-tools`. Agents use `tools` and
`disallowedTools`. Follow the target validator's supported string/list forms.
Scope shell rules to intended commands; describe remaining capabilities honestly.
Keep skill allowlists and denylists disjoint; the existing validator rejects overlaps.
A field spelling or allowlist alone is not a portable sandbox.

Ensure instructions invoke tools that are available and declared. Fully qualified
MCP names have the form `mcp__server__tool`; do not replace them with an unrelated
colon notation. Include only the calls required for the actual workflow.

## Invocation and context

- Preserve ordinary discovery unless explicit-only invocation is requested or
  already configured. `disable-model-invocation` controls automatic selection;
  `user-invocable` controls the user menu.
- A forked skill may use the default agent. A named `agent` requires fork context.
- `argument-hint` describes actual user arguments; disabling automatic selection
  does not remove its usefulness from the menu.
- `when_to_use` is recognized activation context. Keep the combined disclosure
  text within the target validator's budget.
- Choose a model and effort only when useful to the task or required by the
  existing profile; do not imply support for an unavailable model/effort pair.
- Skill hooks use the documented lifecycle event structure. Do not substitute
  made-up event names or agent-specific fields.

See the [live skills reference](https://code.claude.com/docs/en/skills) for runtime
controls. A newly documented field may still differ from a pinned validator;
report that disagreement instead of silently changing the gate.

## Agents

The shared `templates/agent-template.md` emits the existing eleven-field plugin
contract. Activate the three standalone fields for standalone output:
`hooks: {}`, `mcpServers: []`, `permissionMode: default`, or the requested values.
Do not emit those fields on plugin agents. `agent-creator` owns the complete
agent workflow; [validation rules](validation-rules.md) describe its static check.

## Optional metadata and migration

Use `metadata` for additional structured data; it does not replace required
marketplace fields. Preserve supported optional fields and existing invocation
policy during narrow edits. Migrate deprecated `compatible-with` to free-text
`compatibility` through the canonical migration tool when that change is in scope.
Do not describe `when_to_use` as deprecated or treat nested tracking metadata as
an enterprise-required-field substitute.

## Paths and supporting files

Use the installed skill's own resources where possible and resolve paths from
`${CLAUDE_SKILL_DIR}`. Link conditional detail from SKILL.md rather than forcing
all references into every invocation. A companion-skill reference must name a
real installed resource; missing tooling or resources must be reported.

Runtime documentation belongs in `references/`. Forge research and proof records
belong in `.forge/`. For repository testing infrastructure, route through
`audit-tests` and its `implement-tests` handoff rather than inventing another
validator or replacing the target's existing test policy.
