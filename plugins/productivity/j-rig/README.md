# J-Rig Skill Refiner

Use the separately installed J-Rig refiner CLI to bootstrap evaluation metadata,
score a skill with an authorized provider, propose edits and inspect candidates.
This plugin provides instruction guidance and experimental hooks; it does not
implement a separate evaluator or automatic promotion service.

## Installation and prerequisites

```text
/plugin install j-rig@claude-code-plugins-plus
```

The commands require a compatible `@intentsolutions/jrig-cli` installation. Prefer
an existing project-pinned CLI and inspect its version/help. Provider-backed
scoring and proposal generation need an approved provider/model, input-data scope,
runtime credential source and bounded run/spend authorization. Do not install,
upgrade or activate paid work merely to inspect a skill.

## Workflow and limits

Read [the skill](skills/j-rig/SKILL.md) and its
[version-bound command reference](skills/j-rig/references/command-and-hook-contract.md).
The audited CLI supports bootstrap, score, propose, apply, status and report
rendering. Proposal generation is not automatic shadow validation; apply stores a
candidate rather than rewriting the skill or moving a best pointer. Actual
baseline/candidate case evidence and the source-change decision remain separate.
Rendering a report does not sign it.

## Experimental hook status

L1 is an advisory static check. L2 consumes custom event fields and can launch a
background proposal, but does not prove scored-rollout capture or successful
completion. L3 is an advisory stub, not an implemented blocking regression gate.
Hook activation, provider choice and background spend need their own reviewed
runtime scope; the skill does not enable them. See the source scripts and linked
reference for exact limits.

## License

Apache-2.0. Jeremy Longshore / Intent Solutions.
